# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\waypoints\waypoint_generator_connected_points.py
# Compiled at: 2020-04-21 19:40:18
# Size of source mod 2**32: 3643 bytes
import sims4
from event_testing.resolver import SingleSimResolver
from routing.waypoints.tunable_waypoint_graph import TunableWaypointGraphSnippet, TunableWaypointWeightedSet
from routing.waypoints.waypoint_generator import _WaypointGeneratorBase
from sims4.tuning.tunable import TunableRange
logger = sims4.log.Logger('WaypointGeneratorConnectedPoints', default_owner='miking')

class _WaypointGeneratorConnectedPoints(_WaypointGeneratorBase):
    FACTORY_TUNABLES = {'waypoint_graph':TunableWaypointGraphSnippet(description='\n            Defines the waypoints and connections between them.\n            '), 
     'starting_waypoint':TunableWaypointWeightedSet.TunableFactory(description='\n            Waypoint for the generator to start at (will choose one based on the tests/weights).\n            '), 
     'ending_waypoint':TunableWaypointWeightedSet.TunableFactory(description='\n            Waypoint for the generator to end at (will choose one based on the tests/weights).\n            '), 
     'max_waypoints':TunableRange(description='\n            The maximum number of waypoints to visit. Set to 0 to keep going until ending_waypoint is reached.\n            ',
       tunable_type=int,
       default=0,
       minimum=0,
       maximum=100)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sim = self._context.sim
        resolver = SingleSimResolver(self._sim)
        self._starting_waypoint, self._start_constraint = self.starting_waypoint.choose(self.waypoint_graph, self._routing_surface, resolver)

    def get_start_constraint(self):
        return self._start_constraint

    def get_waypoint_constraints_gen(self, routing_agent, waypoint_count):
        resolver = SingleSimResolver(self._sim)
        if self.ending_waypoint is not None:
            ending_waypoint, _ = self.ending_waypoint.choose(self.waypoint_graph, self._routing_surface, resolver)
        else:
            ending_waypoint = None
        cur_waypoint = self._starting_waypoint
        prev_waypoint = None
        num_visited = 0
        while num_visited < self.max_waypoints or self.max_waypoints == 0:
            connections = self.waypoint_graph.connections.get(cur_waypoint, None)
            if connections is None:
                logger.warn('No connections defined in waypoint graph for waypoint id {}.', cur_waypoint)
                break
            new_waypoint, waypoint_constraint = connections.choose(self.waypoint_graph, self._routing_surface, resolver, prev_waypoint)
            prev_waypoint = cur_waypoint
            cur_waypoint = new_waypoint
            if cur_waypoint is None:
                logger.warn('No connection chosen from waypoint graph for waypoint id {}.', prev_waypoint)
                break
            num_visited += 1
            yield waypoint_constraint
            if cur_waypoint == ending_waypoint:
                break