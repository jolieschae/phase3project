# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\fame\fame_tuning.py
# Compiled at: 2020-03-30 16:21:56
# Size of source mod 2**32: 6282 bytes
import event_testing.tests, services, sims4.resources
from bucks.bucks_enums import BucksType
from event_testing.test_events import TestEvent
from event_testing.test_variants import RegionTest
from sims4.tuning.dynamic_enum import DynamicEnumLocked
from sims4.tuning.tunable import TunableEnumEntry, TunablePackSafeReference, TunablePercent, TunableMapping, TunableRange, TunableVariant
from sims4.tuning.tunable_base import ExportModes

class LifestyleBrandTargetMarket(DynamicEnumLocked):
    INVALID = 0


class LifestyleBrandProduct(DynamicEnumLocked):
    INVALID = 0


class TrailblazerEffectAvailableTestVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, region=RegionTest.TunableFactory(locked_args={'tooltip': None}), 
         default='region', **kwargs)


class TrailblazerEffectAvailableTestList(event_testing.tests.TestListLoadingMixin):
    DEFAULT_LIST = event_testing.tests.TestList()

    def __init__(self, description=None):
        super().__init__(description=description, tunable=(TrailblazerEffectAvailableTestVariant()))


class FameTunables:
    FAME_RANKED_STATISTIC = TunablePackSafeReference(description='\n        The ranked statistic that is to be used for tracking fame progress.\n        \n        This should not need to be tuned at all. If you think you need to tune\n        this please speak with a GPE before doing so.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      class_restrictions=('RankedStatistic', ),
      export_modes=(
     ExportModes.ClientBinary,))
    FAME_PERKS_BUCKS_TYPE = TunableEnumEntry(description='\n        A reference to the bucks type used for Fame Perks.\n        ',
      tunable_type=BucksType,
      default=(BucksType.INVALID),
      pack_safe=True)
    FAME_MOMENT_EVENT = TunableEnumEntry(description='\n        The event to register for when waiting for a Fame Moment to occur.\n        ',
      tunable_type=TestEvent,
      default=(TestEvent.Invalid))
    CAREER_HOPPER_PERK = TunablePackSafeReference(description="\n        A reference to the Career Hopper perk. You shouldn't need to tune this.\n        If you do please see your GPE partner.\n        ",
      manager=(services.get_instance_manager(sims4.resources.Types.BUCKS_PERK)))
    TRAILBLAZER_PERK = TunablePackSafeReference(description='\n        A reference to the perk that is used to identify a Sim as being a \n        trailblazer when it is unlocked in that Sims bucks tracker.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.BUCKS_PERK)))
    TRAILBLAZER_EFFECT_AVAILABLE_TESTS = TrailblazerEffectAvailableTestList(description='\n        A set of tests, all of which must pass in order for the trailblazer perk to be able to activate.\n        ')
    CHANCE_TO_WEAR_TRAILBLAZER_OUTFIT = TunablePercent(description='\n        a percentage chance for a sim in a situation without an overriding\n        outfit will wear the same outfit as a trend setting sim.\n        ',
      default=50)
    SHUNNED_REL_BIT = TunablePackSafeReference(description='\n        A reference to the relbit that identifies that a sim is being shunned &#xA;by another sim in the relationship panel.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)),
      export_modes=(
     ExportModes.ClientBinary,))
    LIFESTYLE_BRAND_PERK = TunablePackSafeReference(description='\n        A reference to the perk that is used to unlock the lifestyle brand \n        interactions.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.BUCKS_PERK)))
    END_FEUD_LOOT = TunablePackSafeReference(description='\n        The loot to apply in order to remove the feud and clean up all of the\n        stuff that comes along with ending a feud.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.ACTION)))
    PARENT_FAME_AGE_UP_BONUS = TunableMapping(description="\n        This is a mapping of difference in Fame Rank Level between the Sim and\n        the highest fame parent, and the amount of fame to award the Sim as a\n        bonus.\n        \n        The calculation looks something like this:\n        \n        Sim A is aging up and is Fame Rank 1.\n        Sim A's Father is Fame Rank 3.\n        Sim A's mother is Fame Rank 4.\n        \n        The value we will use for the calculation is Sim A's Parent with the \n        most Fame minus Sim A's Fame. In this case this is Sim A's mom has the\n        highest Rank Fame so we will use her value, 4. Subtracting 1 from 4 \n        results in a difference of 3. \n        \n        Using 3 as the lookup we find the amount of Fame the child gets just\n        for their parent being famous and add that amount to their Fame.\n        ",
      key_type=TunableRange(description='\n            The difference in Fame between the parent and child.\n            ',
      tunable_type=int,
      minimum=0,
      maximum=5,
      default=1),
      value_type=TunableRange(description='\n            The amount of Fame to award the child.\n            ',
      tunable_type=int,
      minimum=0,
      default=10))