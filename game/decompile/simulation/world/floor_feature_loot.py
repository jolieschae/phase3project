# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\floor_feature_loot.py
# Compiled at: 2020-03-06 18:28:03
# Size of source mod 2**32: 3629 bytes
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunableEnumEntry, Tunable
import build_buy, services, sims4
logger = logger = sims4.log.Logger('FloorFeatureLoot')

class FloorFeatureRemoveOp(BaseLootOperation):
    FACTORY_TUNABLES = {'floor_feature_type':TunableEnumEntry(description='\n            The floor feature type that will be removed.\n            ',
       tunable_type=build_buy.FloorFeatureType,
       default=build_buy.FloorFeatureType.BURNT), 
     'removal_radius':Tunable(description='\n            The radius in the loot will remove floor features.\n            ',
       tunable_type=float,
       default=2.5)}

    def __init__(self, *args, floor_feature_type, removal_radius, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.floor_feature_type = floor_feature_type
        self.removal_radius = removal_radius

    def find_floor_feature_locations_within_radius(self, ff_type, location, level, radius):
        found_ff = set()
        radius_squared = radius * radius
        ff_locations = build_buy.list_floor_features(ff_type)
        if ff_locations is None:
            return found_ff
        for ff_pos, ff_level in ff_locations:
            if ff_level == level and (location - ff_pos).magnitude_squared() <= radius_squared:
                found_ff.add(ff_pos)

        return found_ff

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            logger.error('Subject {} is None for the loot {}..', self.subject, self)
            return
        else:
            subject.is_sim or logger.error('Subject {} is not Sim for the loot {}.', self.subject, self)
            return
        sim = self._get_object_from_recipient(subject)
        location = (sims4.math.Vector3)(*sim.location.transform.translation) + sim.forward
        level = sim.location.level
        floor_feature_locations = self.find_floor_feature_locations_within_radius(self.floor_feature_type, location, level, self.removal_radius)
        if floor_feature_locations:
            zone_id = services.current_zone_id()
            with build_buy.floor_feature_update_context(zone_id, self.floor_feature_type):
                for ff_loc in floor_feature_locations:
                    build_buy.set_floor_feature(zone_id, self.floor_feature_type, ff_loc, level, 0)