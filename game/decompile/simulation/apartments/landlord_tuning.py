# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\apartments\landlord_tuning.py
# Compiled at: 2019-10-10 23:26:54
# Size of source mod 2**32: 1652 bytes
from event_testing.tests import TunableTestSet
from filters.tunable import TunableSimFilter
from relationships.relationship_bit import RelationshipBit
from traits.traits import Trait
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet

class LandlordTuning:
    LANDLORD_FILTER = TunableSimFilter.TunablePackSafeReference(description='\n        The Sim Filter used to find/create a Landlord for the game.\n        ')
    LANDLORD_REL_BIT = RelationshipBit.TunablePackSafeReference(description='\n        The rel bit to add between a landlord and apartment tenants. This will\n        be removed if a tenant moves out of an apartment.\n        ')
    TENANT_REL_BIT = RelationshipBit.TunablePackSafeReference(description='\n        The rel bit to add between an apartment Tenant and their Landlord. This\n        will be removed if a tenant moves out of an apartment.\n        ')
    LANDLORD_TRAIT = Trait.TunablePackSafeReference(description='\n        The Landlord Trait used in testing and Sim Filters.\n        ')
    LANDLORD_FIRST_PLAY_RENT_REMINDER_NOTIFICATION = TunableUiDialogNotificationSnippet(description='\n        The notification to show a household if they are played on a new\n        apartment home.\n        ')
    HOUSEHOLD_LANDLORD_EXCEPTION_TESTS = TunableTestSet(description='\n        Tests to run when determining if a household requires a landlord.\n        ')