# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\trait_day_night_tracking.py
# Compiled at: 2016-10-05 19:09:15
# Size of source mod 2**32: 6466 bytes
from buffs.tunable import TunableBuffReference
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableSet

class DayNightTracking(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'sunlight_buffs':TunableSet(description="\n            Allows a list of buffs to be added to the owning Sim when they're in\n            the sunlight.\n            \n            These buffs are also guaranteed to be removed from the Sim when\n            they're no longer in sunlight, regardless of where the buff was\n            applied. For instance, if an interaction has a basic extra that also\n            applied a buff in this list, but the Sim is given this trait and\n            they're not in the sunlight. That buff will be removed.\n            \n            Do not rely on Sunlight Buffs and Shade Buffs to be perfectly\n            mutually exclusive. It's possible, due to timing issues, that both\n            buffs in Sunlight Buffs and buffs in Shade buffs can be on the sim\n            at the same time, or neither on the sim, for a brief amount of time.\n            If you need buff exclusivity, use the tuning on buffs.\n            ",
       tunable=TunableBuffReference(description="\n                The buff to be added to the owning Sim when they're in the\n                sunlight.\n                ",
       pack_safe=True)), 
     'shade_buffs':TunableSet(description="\n            Allows a list of buffs to be added to the owning Sim when they're\n            not in the sunlight.\n            \n            These buffs are also guaranteed to be removed from the Sim when\n            they're no longer in the shade, regardless of where the buff was\n            applied. For instance, if an interaction has a basic extra that also\n            applied a buff in this list, but the Sim is given this trait and\n            they're not in the shade. That buff will be removed.\n            \n            Do not rely on Sunlight Buffs and Shade Buffs to be perfectly\n            mutually exclusive. It's possible, due to timing issues, that both\n            Sunlight Buffs and Shade Buffs can be on the Sim at the same time,\n            or neither on the Sim, for a brief amount of time. If you need buff\n            exclusivity, use the tuning on buffs.\n            ",
       tunable=TunableBuffReference(description="\n                The buff to be added to the owning Sim when they're not in the\n                sunlight.\n                ",
       pack_safe=True)), 
     'day_buffs':TunableSet(description="\n            Allows a list of buffs to be added to the owning Sim when it's\n            currently day time in the region (based on Sunrise and Sunset time\n            tuning for the Region).\n            \n            These buffs are also guaranteed to be removed from the Sim when it's\n            no longer day time, regardless of where the buff was applied. For\n            instance, if an interaction has a basic extra that also applied a\n            buff in this list, but the Sim is given this trait and it's not day\n            time. That buff will be removed.\n            \n            Do not rely on Day Buffs and Night Buffs to be perfectly\n            mutually exclusive. It's possible, due to timing issues, that both\n            Day Buffs and Night Buffs can be on the Sim at the same time,\n            or neither on the Sim, for a brief amount of time. If you need buff\n            exclusivity, use the tuning on buffs.\n            ",
       tunable=TunableBuffReference(description="\n                The buff to be added to the owning Sim when it's day time.\n                ",
       pack_safe=True)), 
     'night_buffs':TunableSet(description="\n            Allows a list of buffs to be added to the owning Sim when it's\n            currently night time in the region (based on Sunrise and Sunset time\n            tuning for the Region).\n            \n            These buffs are also guaranteed to be removed from the Sim when it's\n            no longer night time, regardless of where the buff was applied. For\n            instance, if an interaction has a basic extra that also applied a\n            buff in this list, but the Sim is given this trait and it's not\n            night time. That buff will be removed.\n            \n            Do not rely on Day Buffs and Night Buffs to be perfectly\n            mutually exclusive. It's possible, due to timing issues, that both\n            Day Buffs and Night Buffs can be on the Sim at the same time,\n            or neither on the Sim, for a brief amount of time. If you need buff\n            exclusivity, use the tuning on buffs.\n            ",
       tunable=TunableBuffReference(description="\n                The buff to be added to the owning Sim when it's night time.\n                ",
       pack_safe=True)), 
     'force_refresh_buffs':TunableSet(description='\n            This is the list of buffs, which upon removal, refreshes the status \n            of day-night-sunlight buffs. This is needed because when the vampire \n            resistance cocktail buff expires, we have no good way of adding the \n            burnt-by-sun buff automatically. Any buff which should refresh the \n            day-night-sunlight buff should be added to this list.\n            ',
       tunable=TunableBuffReference(description='\n                The buff that upon removal will force a refresh on the \n                ',
       pack_safe=True))}


class DayNightTrackingState:

    def __init__(self, is_day, in_sunlight):
        self.is_day = is_day
        self.in_sunlight = in_sunlight