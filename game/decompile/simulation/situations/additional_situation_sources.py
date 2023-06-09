# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\additional_situation_sources.py
# Compiled at: 2019-10-22 15:58:14
# Size of source mod 2**32: 3632 bytes
from narrative.narrative_enums import NarrativeSituationShiftType
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableEnumEntry
import services, sims4.resources

class AdditionalSituationSource(HasTunableSingletonFactory, AutoFactoryInit):

    def get_additional_situations(self, predicate=lambda _: True):
        raise NotImplementedError


class HolidayWalkbys(AdditionalSituationSource):

    def get_additional_situations(self, predicate=lambda _: True):
        active_household = services.active_household()
        if active_household is None:
            return ()
        return active_household.holiday_tracker.get_additional_holiday_walkbys(predicate=predicate)


class ZoneModifierSituations(AdditionalSituationSource):
    FACTORY_TUNABLES = {'zone_modifier': TunableReference(description='\n            The zone modifier that we want to get the \n            ',
                        manager=(services.get_instance_manager(sims4.resources.Types.ZONE_MODIFIER)),
                        pack_safe=True)}

    def get_additional_situations(self, predicate=(lambda _: True)):
        zone_id = services.current_zone_id()
        zone_modifier_service = services.get_zone_modifier_service()
        zone_modifiers = zone_modifier_service.get_zone_modifiers(zone_id)
        if self.zone_modifier not in zone_modifiers:
            return ()
        weighted_situations = self.zone_modifier.additional_situations.get_weighted_situations(predicate=predicate)
        if weighted_situations is None:
            return ()
        return weighted_situations


class NarrativeSituations(AdditionalSituationSource):
    FACTORY_TUNABLES = {'narrative_situation_shift_type': TunableEnumEntry(description='\n            Shift type to look for.\n            ',
                                         tunable_type=NarrativeSituationShiftType,
                                         default=(NarrativeSituationShiftType.INVALID),
                                         invalid_enums=(
                                        NarrativeSituationShiftType.INVALID,),
                                         pack_safe=True)}

    def get_additional_situations(self, predicate=(lambda _: True)):
        weighted_situations = []
        narrative_service = services.narrative_service()
        for narrative in narrative_service.active_narratives:
            if self.narrative_situation_shift_type not in narrative.additional_situation_shifts:
                continue
            shift = narrative.additional_situation_shifts[self.narrative_situation_shift_type]
            shift_situations = shift.get_weighted_situations(predicate=predicate)
            if shift_situations is not None:
                weighted_situations.extend(shift_situations)

        return weighted_situations