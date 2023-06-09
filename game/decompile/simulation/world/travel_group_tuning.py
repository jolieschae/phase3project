# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\travel_group_tuning.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 3658 bytes
from sims4.tuning.tunable import TunableTuple, TunableRange, TunableList, TunableReference
from ui.ui_dialog_notification import UiDialogNotification
import services, sims4

class TravelGroupTuning:
    VACATION_ENDING_DAYS_TNS = TunableTuple(description="\n        When the travel group's vacation is about to end, we want to show a TNS\n        letting the player know in case they want to prepare to leave or extend\n        their vacation.\n        ",
      days_before_vacation_ends=TunableRange(description='\n            The number of days before the vacation ends that we should fire\n            this TNS.\n            ',
      tunable_type=float,
      default=1.0,
      minimum=1.0,
      maximum=7.0),
      notification_to_show=UiDialogNotification.TunableFactory(description="\n            A TNS that is displayed when the Sim's vacation is about to end.\n            "))
    RESIDENTIAL_WELCOME_NOTIFICATION = UiDialogNotification.TunableFactory(description='\n        A TNS that will fire when a vacation for active sim starts in a residential region.\n        ')
    VACATION_CONTINUE_NOTIFICATION = UiDialogNotification.TunableFactory(description='\n        A TNS that will fire on load when not simply travelling from one zone to another\n        if active sim is in travel group. (e.g. loading the save)\n        \n        First additional token is household name, second is time remaining.\n        ')
    SS3_PARK_INTERACTIONS = TunableList(description='\n        Interactions in which to park NPC travel mates during SS3.\n        One of which will be randomly selected\n        ',
      tunable=TunableReference(description='\n                The affordance to push.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      class_restrictions=('SuperInteraction', ),
      pack_safe=True))
    VACATION_ENDING_HOURS_TNS = TunableTuple(description="\n        When the travel group's vacation is about to end, we want to show a TNS\n        letting the player know in case they want to prepare to leave or extend\n        their vacation.\n        ",
      hours_before_vacation_ends=TunableRange(description='\n            The number of hours before the vacation ends that we should fire\n            this TNS.\n            ',
      tunable_type=float,
      default=4.0,
      minimum=1.0,
      maximum=23.0),
      notification_to_show=UiDialogNotification.TunableFactory(description="\n            A TNS that is displayed when the Sim's vacation is about to end.\n            Tokens: 0 - number of hours left before the vacation ends.\n            "))
    INSTANCED_SIM_LOOT = TunableList(description='\n        Loot given to instanced sims when they join a travel group,\n        or to sims in a travel group when they are instanced.\n        ',
      tunable=TunableReference(description='\n            Loot to apply on sim.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
      class_restrictions=('LootActions', 'RandomWeightedLoot'),
      pack_safe=True))