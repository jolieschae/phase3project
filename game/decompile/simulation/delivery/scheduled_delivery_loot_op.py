# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\delivery\scheduled_delivery_loot_op.py
# Compiled at: 2019-01-29 16:39:15
# Size of source mod 2**32: 3239 bytes
from date_and_time import create_time_span
from interactions import ParticipantTypeSingleSim
from interactions.object_rewards import ObjectRewardsOperation
from interactions.utils import LootType
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableSimMinute, OptionalTunable, HasTunableReference, HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry
from sims4.utils import classproperty, flexmethod
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
import services, sims4.resources

class ScheduledDeliveryLoot(HasTunableReference, HasTunableSingletonFactory, AutoFactoryInit, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ACTION)):
    INSTANCE_TUNABLES = {'participant':TunableEnumEntry(description='\n            Sim who is getting the delivery delivered to their household.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'time_from_now':TunableSimMinute(description='\n            How far from now we want our delivery.\n            ',
       default=1440,
       minimum=1,
       maximum=10080), 
     'not_home_notification':OptionalTunable(description='\n            If enabled, a notification will be displayed when the Sim is not\n            currently home when the object(s) would be delivered.\n            The object will be in the mailbox when they arrive back at their\n            home lot.\n            ',
       tunable=TunableUiDialogNotificationSnippet()), 
     'at_home_notification':OptionalTunable(description='\n            The notification that will be displayed when the Sim is at\n            home when the object(s) would be delivered. The object(s)\n            will end up in hidden inventory waiting to be delivered by\n            the mailman.\n            ',
       tunable=TunableUiDialogNotificationSnippet()), 
     'objects_to_deliver':ObjectRewardsOperation.TunableFactory(description='\n            The objects to be delivered. When participants are used \n            within this structure, only Sim-type participants will resolve.\n            ',
       locked_args={'notification':None, 
      'place_in_mailbox':True, 
      'force_family_inventory':False})}

    @classproperty
    def loot_type(self):
        return LootType.SCHEDULED_DELIVERY

    @flexmethod
    def apply_to_resolver(cls, inst, resolver, skip_test=False):
        subject = resolver.get_participant(cls.participant)
        subject.household.delivery_tracker.request_delivery(subject.sim_id, cls.guid64, create_time_span(minutes=(cls.time_from_now)))