# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\set_posture_element.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 9282 bytes
from animation.animation_utils import flush_all_animations
from animation.arb_element import distribute_arb_element
from animation.posture_manifest import Hand
from element_utils import build_critical_section, build_critical_section_with_finally
from elements import ParentElement
from postures.posture_specs import get_origin_spec, PostureSpecVariable
from postures.transition import PostureTransition
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableReference, TunableEnumEntry
import animation.arb, element_utils, routing, services, sims4.log
logger = sims4.log.Logger('SetPosture', default_owner='tingyul')

class SetPosture(ParentElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'posture_type':TunableReference(description='\n            Posture to set.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.POSTURE)), 
     'surface_type':TunableEnumEntry(routing.SurfaceType, description='\n            The surface type the posture requires. For example, swim should set\n            this to SURFACETYPE_POOL.\n            ',
       default=routing.SurfaceType.SURFACETYPE_WORLD)}

    def __init__(self, interaction, *args, sequence=(), **kwargs):
        (super().__init__)(*args, **kwargs)
        self.interaction = interaction
        self.sequence = sequence
        self._event_handler_handle = None
        self._xevt_triggered = False
        self._previous_posture_state = None
        self._previous_linked_posture_state = None

    def _run(self, timeline):
        sequence = build_critical_section(build_critical_section_with_finally(self._register_set_posture_xevt, self.sequence, self._release_set_posture_xevt), self._start_posture_gen)
        return timeline.run_child(sequence)

    def _register_set_posture_xevt(self, element):
        animation_context = self.interaction.animation_context
        self._event_handler_handle = animation_context.register_event_handler((self._set_posture),
          handler_id=(PostureTransition.IDLE_TRANSITION_XEVT))
        posture_anim_context = self.interaction.sim.posture.animation_context
        if posture_anim_context is None:
            logger.error('Posture animation context is None. Cannot add user data to interaction animation context for interaction {}.', self.interaction)
            return
        animation_context.add_user_data_from_anim_context(posture_anim_context)

    def _release_set_posture_xevt(self, element):
        self._event_handler_handle.release()
        self._event_handler_handle = None

    def _set_posture(self, *args, **kwargs):
        self._xevt_triggered = True
        from postures.posture_state import PostureState
        interaction_sim = self.interaction.sim
        sims_to_set_posture_for = [interaction_sim]
        self._previous_posture_state = interaction_sim.posture_state
        linked_posture_state = interaction_sim.posture_state.linked_posture_state
        if linked_posture_state is not None:
            self._previous_linked_posture_state = linked_posture_state
            sims_to_set_posture_for.append(linked_posture_state.sim)
        for sim in sims_to_set_posture_for:
            origin_posture_spec = get_origin_spec(self.posture_type)
            sim.posture_state = PostureState(sim, None, origin_posture_spec, {PostureSpecVariable.HAND: (Hand.LEFT,)})
            sim.posture_state.body.source_interaction = sim.create_default_si()
            idle_arb = animation.arb.Arb()
            sim.posture.append_transition_to_arb(idle_arb, None)
            sim.posture.append_idle_to_arb(idle_arb)
            distribute_arb_element(idle_arb, master=sim)

    def _start_posture_gen(self, timeline):
        if not self._xevt_triggered:
            if self.interaction.has_been_canceled:
                return
            logger.error('{} is missing a 750 xevt in its animation. Set Posture basic extra requires it to work correctly. Without it, Sim will likely pop between posture idles.', self.interaction)
            self._set_posture()
        sim = self.interaction.sim
        target = self.interaction.target if self.interaction.target is not None else sim
        self.interaction.satisfied = True
        sims_to_set_posture_for = [
         sim]
        if self._previous_linked_posture_state is not None:
            sims_to_set_posture_for.append(self._previous_linked_posture_state.sim)
        for sim in sims_to_set_posture_for:
            routing_surface = routing.SurfaceIdentifier(target.zone_id, target.level, self.surface_type)
            if not sim.routing_surface != target.routing_surface:
                if sim.routing_surface.type != self.surface_type:
                    sim.move_to(routing_surface=routing_surface)
                yield from element_utils.run_child(timeline, (
                 sim.posture.get_idle_behavior(), flush_all_animations))
                yield from sim.posture_state.kickstart_gen(timeline, routing_surface)

        for aspect in self._previous_posture_state.aspects:
            yield from element_utils.run_child(timeline, aspect.end())

        if self._previous_linked_posture_state is not None:
            for aspect in self._previous_linked_posture_state.aspects:
                yield from element_utils.run_child(timeline, aspect.end())

        if False:
            yield None