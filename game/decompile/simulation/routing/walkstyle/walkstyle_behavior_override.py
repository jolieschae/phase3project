# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\walkstyle\walkstyle_behavior_override.py
# Compiled at: 2018-09-12 14:05:55
# Size of source mod 2**32: 4412 bytes
from routing.walkstyle.walkstyle_enums import WalkStyleRunAllowedFlags, WalkstyleBehaviorOverridePriority
from routing.walkstyle.walkstyle_tuning import TunableWalkstyle
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, OptionalTunable, TunableRange, TunableEnumFlags, TunableEnumEntry

def _get_tunable_override(tunable):
    return OptionalTunable(description=('\n        If enabled, override this property: {}\n        \n        NOTE: This override is not additive. The only value that is considered\n        is the one associated with the walkstyle override with the highest\n        priority.\n        '.format(getattr(tunable, 'description', ''))),
      tunable=tunable,
      enabled_name='Override',
      disabled_name='Leave_Unchanged')


class WalkstyleBehaviorOverride(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'walkstyle_behavior_priority':TunableEnumEntry(description='\n            Define the priority of this override relative to other overrides.\n            This is meaningful for the non-additive properties of this override.\n            ',
       tunable_type=WalkstyleBehaviorOverridePriority,
       default=WalkstyleBehaviorOverridePriority.DEFAULT), 
     'run_required_total_distance':_get_tunable_override(tunable=TunableRange(description='\n                For an entire route, the minimum distance required for Sim to\n                run.\n                ',
       tunable_type=float,
       minimum=0,
       default=20)), 
     'run_required_segment_distance':_get_tunable_override(tunable=TunableRange(description='\n                For a specific route segment, the minimum distance required for\n                the Sim to run.\n                ',
       tunable_type=float,
       minimum=0,
       default=10)), 
     'run_walkstyle':_get_tunable_override(tunable=TunableWalkstyle(description='\n                Override the walkstyle to use when this Sim is supposed to be running.\n                ')), 
     'short_walkstyle':_get_tunable_override(tunable=TunableWalkstyle(description='\n                Override walkstyle used when Sims are routing over a short distance.\n                ')), 
     'wading_walkstyle':_get_tunable_override(tunable=TunableWalkstyle(description='\n                Override walkstyle used when Sims are walking through the water.\n                ')), 
     'additional_run_flags':TunableEnumFlags(description='\n            Define where the Sim is allowed to run.\n            \n            NOTE: This is *additive*, meaning the resulting run flags for a Sim\n            are defined by the default tuning plus all overrides. However,\n            removed_run_flags is applied last.\n            ',
       enum_type=WalkStyleRunAllowedFlags,
       allow_no_flags=True), 
     'removed_run_flags':TunableEnumFlags(description='\n            Modify a Sim\'s ability to run.\n            \n            NOTE: This is *additive* with respect to all overrides, and is\n            applied to the combination of the default tuning plus\n            additional_run_flags from all overrides.\n            \n            e.g.: The default behavior for a human is to exclusively run\n            outdoors. A hypothetical "excitable" trait might add the ability to\n            run indoors (meaning the total result is indoors+outdoors). However,\n            the "pregnant" trait might remove the ability to run (both outdoors\n            and indoors), effectively preventing the Sim from running at all.\n            ',
       enum_type=WalkStyleRunAllowedFlags,
       allow_no_flags=True)}