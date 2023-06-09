# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\route_events\route_event_type_animation.py
# Compiled at: 2020-11-17 21:07:19
# Size of source mod 2**32: 12605 bytes
import functools, services
from animation.arb import Arb
from animation.arb_element import distribute_arb_element
from animation.posture_manifest import MATCH_NONE
from event_testing.resolver import SingleObjectResolver, DoubleSimResolver, SingleSimResolver
from event_testing.results import TestResult
from interactions import ParticipantType
from interactions.utils.animation_reference import TunableAnimationReference
from interactions.utils.routing import FollowPath
from postures import are_carry_compatible
from routing.route_events.route_event_mixins import RouteEventDataBase
from sims4.math import MAX_INT32
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, OptionalTunable, TunableRange, TunableEnumEntry, TunableList, TunableReference, TunableTuple, Tunable
import sims4.log
logger = sims4.log.Logger('RouteEvents', default_owner='rmccord')

class RouteEventTypeAnimation(RouteEventDataBase, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'animation_elements':TunableList(description='\n            List of animation elements that will be played.\n            ',
       tunable=TunableAnimationReference(description='\n                The animation that Sims play during the Route Event.\n                ',
       callback=None,
       class_restrictions=()),
       minlength=1), 
     '_duration_override':OptionalTunable(description="\n            If enabled, we override the must run duration we expect this route\n            event to take. We do this for animations that will freeze the\n            locomotion so that we don't actually take time away from the rest of\n            the path where other route events could play.\n            ",
       tunable=TunableRange(description='\n                The duration we want this route event to have. This modifies how\n                much of the route time this event will take up to play the\n                animation. For route events that freeze locomotion, you might\n                want to set this to a very low value. Bear in mind that high\n                values are less likely to be scheduled for shorter routes.\n                ',
       tunable_type=float,
       default=0.1,
       minimum=0.1)), 
     'target_participant':OptionalTunable(description='\n            The target of the animation based on the resolver of the actor\n            playing the route event.\n            ',
       tunable=TunableEnumEntry(description='\n                The participant related to the actor that plays the route event.\n                ',
       tunable_type=ParticipantType,
       default=(ParticipantType.ObjectChildren))), 
     'loots_on_xevt':TunableList(description='\n            A list of loot operations that will be applied at an xevent\n            during the route event animation. Using this tuning will modify the\n            way we schedule the animation for this route event, so should only\n            be used after discussion with a GPE.\n            ',
       tunable=TunableTuple(loot=TunableReference(description='\n                    Loot to be applied.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       pack_safe=True),
       xevt=Tunable(description='\n                    The id of the xevent.\n                    ',
       tunable_type=int,
       default=101)))}

    @classmethod
    def _get_tuning_suggestions(cls, event_data_tuning, print_suggestion):
        if event_data_tuning.loots_on_xevt:
            print_suggestion('Loots on xevt is tuned. This will cause this route event to defer processing to execute() and may cause it to schedule inconsistently, especially at SS3.', owner='rrodgers')
            if event_data_tuning._duration_override < 0.5:
                print_suggestion('Deferred processing route event has a short duration. This can causing routing issues. See TS4-100768', owner='rrodgers')

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.arb = None
        self._duration_total = MAX_INT32
        self._duration_must_run = MAX_INT32
        self._duration_repeat = MAX_INT32
        self.defer_process_until_execute = False
        self.target_loot_sim = None

    @classmethod
    def test(cls, actor, event_data_tuning, ignore_carry=False):
        if actor is None:
            return TestResult(False, 'Route Event Actor is None.')
        if actor.is_sim:
            for animation_element in event_data_tuning.animation_elements:
                postures = animation_element.get_supported_postures()
                sim_posture_state = actor.posture_state
                provided_postures = sim_posture_state.body.get_provided_postures(surface_target=MATCH_NONE)
                supported_postures = provided_postures.intersection(postures)
                if not supported_postures:
                    return TestResult(False, 'Animation Route Event does not support {} for {}.', actor.posture_state, actor)
                    carry_state = ignore_carry or sim_posture_state.get_carry_state()
                    return any((are_carry_compatible(entry, carry_state) for entry in supported_postures)) or TestResult(False, 'Animation Route Event does not support {} for {}.', actor.posture_state, actor)

        return TestResult.TRUE

    @property
    def duration_override(self):
        if self._duration_override is not None:
            return self._duration_override
        return self._duration_must_run

    def get_target(self, actor):
        if self.target_participant is None:
            return
        elif actor.is_sim:
            resolver = SingleSimResolver(actor.sim_info)
        else:
            resolver = SingleObjectResolver(actor)
        targets = resolver.get_participants(self.target_participant)
        if targets:
            return next(iter(targets))

    def prepare(self, actor, setup_asm_override=None):

        def restart_asm(asm):
            asm.set_current_state('entry')
            return True

        target = self.get_target(actor)
        routing_component = actor.routing_component
        if actor.is_sim:
            route_interaction = routing_component.route_interaction
            if route_interaction is None:
                logger.error('Route Interaction was None for {}', actor)
                return
        self.arb = Arb()
        for animation_element in self.animation_elements:
            if actor.is_sim:
                route_event_animation = animation_element(route_interaction, setup_asm_additional=(restart_asm if setup_asm_override is None else setup_asm_override),
                  enable_auto_exit=False)
                asm = route_event_animation.get_asm()
                if asm is not None:
                    if target is not None:
                        if not asm.set_actor(route_event_animation.target_name, target):
                            logger.error('Route Event {} Failed to setup target.', self)
                            return
                if asm is None:
                    logger.warn('Unable to get a valid Route Event ASM ({}) for {}.', route_event_animation, actor)
                    return
            else:
                route_event_animation = animation_element(actor, target=target,
                  setup_asm_func=(restart_asm if setup_asm_override is None else setup_asm_override))
                animation_context = routing_component.animation_context
                asm = route_event_animation.get_asm(animation_context=animation_context)
                if asm is None:
                    logger.warn('Unable to get a valid Route Event ASM ({}) for {}.', route_event_animation, actor)
                    return
                route_event_animation.append_to_arb(asm, self.arb)
                route_event_animation.append_exit_to_arb(asm, self.arb)

        if self.arb is None:
            logger.error('Unable to create arb for Route Event: {}', self)
            return
        self._duration_total, self._duration_must_run, self._duration_repeat = self.arb.get_timing()

    def is_valid_for_scheduling(self, actor, path):
        if self.arb is None or self.arb.empty:
            return False
        return True

    def execute(self, actor, **kwargs):

        def _event_handler(resolver, loot, *_, **__):
            loot.apply_to_resolver(resolver)

        if self.arb is not None:
            if self.loots_on_xevt or self.defer_process_until_execute:
                target_sim = self.target_loot_sim() if self.target_loot_sim is not None else None
                if target_sim is not None:
                    resolver = DoubleSimResolver(actor.sim_info, target_sim.sim_info)
                else:
                    resolver = SingleSimResolver(actor.sim_info)
                for loot_tuning in self.loots_on_xevt:
                    callback = functools.partial(_event_handler, resolver, loot_tuning.loot)
                    self.arb.register_event_handler(callback, handler_id=(loot_tuning.xevt))

                distribute_arb_element((self.arb), master=actor, immediate=True)
        if actor.primitives:
            for primitive in tuple(actor.primitives):
                if isinstance(primitive, FollowPath):
                    primitive.set_animation_sleep_end(self._duration_must_run)
                    return

    def process(self, actor):
        if self.arb is not None:
            if not self.loots_on_xevt:
                if not self.defer_process_until_execute:
                    distribute_arb_element((self.arb), master=actor, immediate=True)