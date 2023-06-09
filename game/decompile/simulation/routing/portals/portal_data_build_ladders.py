# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\portals\portal_data_build_ladders.py
# Compiled at: 2020-04-20 13:35:53
# Size of source mod 2**32: 1928 bytes
import routing, sims4.log
from routing.portals.build_ladders_mixin import _BuildLaddersMixin
from routing.portals.portal_data_ladders import _PortalTypeDataLadders
from routing.portals.portal_enums import LadderType
from routing.portals.portal_tuning import PortalFlags
logger = sims4.log.Logger('BuildLaddersPortalData', default_owner='bnguyen')

class _PortalTypeDataBuildLadders(_PortalTypeDataLadders, _BuildLaddersMixin):

    def get_portal_duration(self, portal_instance, is_mirrored, walkstyle, age, gender, species):
        return self._calculate_walkstyle_duration(portal_instance, is_mirrored, age, gender, species, walkstyle, walkstyle)

    def get_portal_locations(self, obj):
        return self._get_ladder_portal_locations(obj)

    def _get_additional_portal_location_flags(self):
        return PortalFlags.STAIRS_PORTAL_LONG

    def _get_route_ladder_data(self, is_mirrored):
        op = super()._get_route_ladder_data(is_mirrored)
        op.portal_alignment = self.portal_alignment
        op.ladder_type = LadderType.LADDER_BUILD
        return op

    def _get_num_rungs(self, ladder):
        _, _, ladder_height = routing.get_ladder_levels_and_height(ladder.id, ladder.zone_id)
        return ladder_height // self.ladder_rung_distance + 1