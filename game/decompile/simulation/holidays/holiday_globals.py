# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\holidays\holiday_globals.py
# Compiled at: 2018-03-12 20:01:18
# Size of source mod 2**32: 6011 bytes
from careers.career_ops import CareerTimeOffReason
from interactions.utils.loot import LootActions
from sims4.tuning.tunable import TunablePackSafeReference, TunableMapping, TunableEnumEntry, Tunable, TunableTuple, TunableList, TunableThreshold, TunableReference
from situations.situation_types import SituationMedal
from tunable_time import TunableTimeOfDay, TunableTimeSpan
from ui.ui_dialog_notification import UiDialogNotification
import enum, services, sims4

class HolidayState(enum.Int, export=False):
    INITIALIZED = ...
    PRE_DAY = ...
    RUNNING = ...
    SHUTDOWN = ...


class TraditionPreference(enum.Int):
    DOES_NOT_CARE = 0
    LIKES = 1
    LOVES = 2


TRADITION_PREFERENCE_CARES = frozenset((TraditionPreference.LIKES, TraditionPreference.LOVES))

class HolidayTuning:
    HOLIDAY_SITUATION = TunablePackSafeReference(description='\n        Reference to the holiday situation.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.SITUATION)))
    HOLIDAY_JOB = TunablePackSafeReference(description='\n        Holiday Situation Job.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)))
    HOLIDAY_DURATION = TunableTimeSpan(description='\n        The number of hours the main holidays and surprise holidays run for.\n        ',
      default_hours=22,
      locked_args={'days':0, 
     'minutes':0})
    HOLIDAY_TIME_OFF_REASON = TunableEnumEntry(description='\n        The holiday time off reason.\n        ',
      tunable_type=CareerTimeOffReason,
      default=(CareerTimeOffReason.NO_TIME_OFF))
    MAIN_HOLIDAY_START_TIME = TunableTimeOfDay(description='\n        The start time for main holidays.\n        ',
      default_hour=6)
    HOLIDAY_NOTIFICATION_INFORMATION = TunableMapping(description='\n        Notification to be shown based on the medal achieved.\n        ',
      key_type=TunableEnumEntry(description='\n            The medal achieved for the situation.\n            ',
      tunable_type=SituationMedal,
      default=(SituationMedal.GOLD)),
      value_type=UiDialogNotification.TunableFactory(description='\n            The notification to be shown.\n            0 - Sim\n            1 - Holiday Name\n            '))
    HOLIDAY_SCORING_INFORMATION = TunableList(description='\n        Information related to scoring the holiday situation based on the number\n        of traditions a Sim LIKES or LOVES.\n        \n        Order is important. The first threshold that passes returns the maximum\n        score associated with it. Because of this, order the thresholds from\n        greater to lesser threshold values.\n        \n        If no thresholds pass, the situation will have an undefined maximum\n        score.\n        ',
      tunable=TunableTuple(description='\n            The number of traditions a Sim cares about that determines the \n            maximum score to use and the rewards to be given for the holiday \n            situation.\n            ',
      max_score=Tunable(description='\n                The maximum score for the holiday situation. \n                ',
      tunable_type=int,
      default=0),
      reward=TunableMapping(description='\n                Reward to be given based on the medal achieved.\n                ',
      key_type=TunableEnumEntry(description='\n                    The medal achieved for the situation.\n                    ',
      tunable_type=SituationMedal,
      default=(SituationMedal.GOLD)),
      value_type=TunableReference(description='\n                    The reward to be given.\n                    ',
      manager=(services.get_instance_manager(sims4.resources.Types.REWARD)),
      pack_safe=True)),
      threshold=TunableThreshold(description='\n                The number of traditions that a Sim cares about that determines\n                which score and rewards are used.\n                ')))
    TRADITION_PREFERENCE_SCORE_MULTIPLIER = TunableMapping(description='\n        Map of tradition preference to score multiplier, that is used to\n        modify the score a Sim receives when they complete a holiday tradition\n        based on their preferences.\n        ',
      key_type=TunableEnumEntry(description="\n            A Sim's tradition preference.\n            ",
      tunable_type=TraditionPreference,
      default=(TraditionPreference.LIKES)),
      value_type=Tunable(description='\n            The score multiplier for the preference.\n            ',
      tunable_type=float,
      default=1))
    HOLIDAY_DISPLAY_DELAY = TunableTimeSpan(description='\n        The number of hours that elapses from the start of the holiday\n        before UI shows the full UI. \n        ',
      default_hours=3,
      locked_args={'days':0, 
     'minutes':0})