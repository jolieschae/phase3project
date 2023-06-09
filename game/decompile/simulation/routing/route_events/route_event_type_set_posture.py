# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\route_events\route_event_type_set_posture.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 4570 bytes
import animation.arb, element_utils, services, sims4.log
from animation.animation_utils import flush_all_animations
from animation.arb_element import distribute_arb_element
from animation.posture_manifest import Hand
from postures.posture_specs import get_origin_spec, PostureSpecVariable
from postures.posture_state import PostureState
from routing.route_events.route_event_mixins import RouteEventDataBase
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableReference
logger = sims4.log.Logger('SetPostureRouteEvent', default_owner='trevor')

class RouteEventTypeSetPosture(RouteEventDataBase, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'posture_type': TunableReference(description='\n            The posture type to set on the Sim.\n            ',
                       manager=(services.get_instance_manager(sims4.resources.Types.POSTURE)))}

    @property
    def duration_override(self):
        return 0

    def prepare(self, actor):
        pass

    def execute(self, actor, path=None):
        previous_posture_state = actor.posture_state
        origin_posture_spec = get_origin_spec(self.posture_type)
        var_map = {PostureSpecVariable.HAND: Hand.LEFT}
        carry_posture_overrides = {previous_posture_state.left.track: previous_posture_state.left, 
         previous_posture_state.right.track: previous_posture_state.right}
        actor.posture_state = PostureState(actor, (actor.posture_state), origin_posture_spec, var_map, carry_posture_overrides=carry_posture_overrides)
        actor.posture_state.body.source_interaction = actor.create_default_si()
        final_routing_surface = path.final_location.routing_surface
        idle_arb = animation.arb.Arb()
        actor.posture.append_transition_to_arb(idle_arb, None)
        actor.posture.append_idle_to_arb(idle_arb)
        distribute_arb_element(idle_arb, master=actor)
        running_interaction = actor.queue.running
        if running_interaction is not None:
            running_interaction.satisfied = True

        def kickstart_posture(_timeline):
            result = yield from actor.posture_state.body.kickstart_gen(_timeline, actor.posture_state, final_routing_surface)
            return result
            if False:
                yield None

        def end_body_aspect(_timeline):
            if previous_posture_state.body:
                result = yield from element_utils.run_child(_timeline, previous_posture_state.body.end())
                if not result:
                    return result
            return True
            if False:
                yield None

        timeline = services.time_service().sim_timeline.get_sub_timeline()
        element = element_utils.build_element(actor.posture.get_idle_behavior())
        timeline.schedule(element)
        if not timeline.simulate(timeline.now):
            logger.error('Failed trying to run idle behavior on Sim {} during a set posture route event.', actor)
        element = element_utils.build_element(flush_all_animations)
        timeline.schedule(element)
        if not timeline.simulate(timeline.now):
            logger.error('Failed trying to flush animations on Sim {} during a set posture route event.', actor)
        element = element_utils.build_element(kickstart_posture)
        timeline.schedule(element)
        if not timeline.simulate(timeline.now):
            logger.error('Failed trying to kickstart a posture on Sim {} during a set posture route event.', actor)
        element = element_utils.build_element(end_body_aspect)
        timeline.schedule(element)
        if not timeline.simulate(timeline.now):
            logger.error('Failed trying to end previous body aspect on Sim {} during a set posture route event.', actor)

    def process(self, actor):
        pass