# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\floor_feature_test.py
# Compiled at: 2020-11-12 10:43:22
# Size of source mod 2**32: 3726 bytes
from build_buy import FloorFeatureType
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from caches import cached_test
from interactions import ParticipantType
from objects import ALL_HIDDEN_REASONS
from sims4.tuning.geometric import TunableDistanceSquared
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry
import build_buy, services, sims, sims4
logger = sims4.log.Logger('FloorFeatureTest')

class NearbyFloorFeatureTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'floor_feature':TunableEnumEntry(description="\n            The floor feature type that is required to be inside the radius_actor's\n            radius.\n            ",
       tunable_type=FloorFeatureType,
       default=FloorFeatureType.BURNT), 
     'radius':TunableDistanceSquared(description="\n            The radius, with the radius actor's position, that defines the area\n            within which the floor feature is valid.\n            ",
       default=5.0), 
     'radius_actor':TunableEnumEntry(description='\n            The Actor within whose radius the tuned floor feature must be in\n            for consideration.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor)}

    def floor_feature_exists_in_object_radius(self, radius_actors):
        floor_features = build_buy.list_floor_features(self.floor_feature)
        if floor_features is None:
            return False
        for actor in radius_actors:
            for ff_position, _ in floor_features:
                delta = ff_position - actor.position
                if delta.magnitude_squared() < self.radius:
                    return True

        return False

    def get_expected_args(self):
        return {'radius_actors': self.radius_actor}

    @cached_test
    def __call__(self, radius_actors=()):
        radius_objects = []
        SimInfo = sims.sim_info.SimInfo
        for radius_actor in radius_actors:
            if isinstance(radius_actor, SimInfo):
                radius_actor_object = radius_actor.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
                if radius_actor_object is None:
                    logger.error('{} has a None value and cannot be used to determine a nearby floor feature test.', radius_actor)
                else:
                    radius_objects.append(radius_actor_object)
            else:
                radius_objects.append(radius_actor)

        result = self.floor_feature_exists_in_object_radius(radius_objects)
        if not result:
            return TestResult(False, 'No Found Floor Features', tooltip=(self.tooltip))
        return TestResult.TRUE