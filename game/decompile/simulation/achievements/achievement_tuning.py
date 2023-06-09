# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\achievements\achievement_tuning.py
# Compiled at: 2019-02-21 15:02:42
# Size of source mod 2**32: 8220 bytes
from distributor.shared_messages import IconInfoData
from event_testing.milestone import Milestone
from event_testing.resolver import SingleSimResolver
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import OptionalTunable
from sims4.tuning.tunable_base import GroupNames
from ui.ui_dialog import UiDialogResponse
from ui.ui_dialog_notification import UiDialogNotification
import services, sims4.localization, sims4.log, sims4.tuning.tunable, ui.screen_slam
logger = sims4.log.Logger('AchievementTuning')

class Achievement(Milestone, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ACHIEVEMENT)):
    INSTANCE_TUNABLES = {'display_name':sims4.localization.TunableLocalizedString(description='\n            Name of this Achievement.\n            ',
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI), 
     'descriptive_text':sims4.localization.TunableLocalizedString(description='\n            Description of this Achievement.\n            ',
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI), 
     'point_value':sims4.tuning.tunable.Tunable(description='\n            Point value for an achievement.\n            ',
       tunable_type=int,
       default=1,
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.REWARDS), 
     'pid':sims4.tuning.tunable.TunableRange(description='\n            PID for an achievement.\n            ',
       tunable_type=int,
       default=0,
       minimum=0,
       maximum=127,
       export_modes=sims4.tuning.tunable_base.ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'xid':sims4.tuning.tunable.Tunable(description='\n            XID for an achievement.\n            ',
       tunable_type=str,
       default='',
       allow_empty=True,
       export_modes=sims4.tuning.tunable_base.ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'reward':sims4.tuning.tunable.TunableReference(description='\n            The reward received when this achievement is completed.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.REWARD),
       allow_none=True,
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.REWARDS), 
     'category':sims4.tuning.tunable.TunableList(description='\n            A List of all of the categories that this Achievement is a part of.\n            ',
       tunable=sims4.tuning.tunable.TunableReference(description='\n                One of the categories that this Achievement is a part of.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.ACHIEVEMENT_CATEGORY))),
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI), 
     'is_hidden':sims4.tuning.tunable.Tunable(description='\n            If checked then this Achievement will be hidden from the\n            Achievement UI until it has been completed.\n            ',
       tunable_type=bool,
       default=False,
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI), 
     'icon':sims4.tuning.tunable.TunableResourceKey(None, resource_types=sims4.resources.CompoundTypes.IMAGE, description='\n            The icon to be displayed in the panel view.\n            ',
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI), 
     'screen_slam':OptionalTunable(description='\n            Which screen slam to show when this achievement is completed.  \n            Localization Tokens: Achievement Name = {0.String}\n            ',
       tunable=ui.screen_slam.TunableScreenSlamSnippet(),
       tuning_group=GroupNames.UI), 
     'notification':OptionalTunable(description='\n            If enabled, this notification will show when the achievement is\n            completed.\n            ',
       tunable=UiDialogNotification.TunableFactory(locked_args={'title':None, 
      'text':None, 
      'icon':None, 
      'primary_icon_response':UiDialogResponse(text=None, ui_request=UiDialogResponse.UiDialogUiRequest.SHOW_ACHIEVEMENTS)}),
       tuning_group=GroupNames.UI)}

    @classmethod
    def handle_event(cls, sim_info, event, resolver):
        if sim_info is not None:
            if sim_info.account is not None:
                sim_info.account.achievement_tracker.handle_event(cls, event, resolver)

    @classmethod
    def register_callbacks(cls):
        tests = [objective.objective_test for objective in cls.objectives]
        services.get_event_manager().register_tests(cls, tests)

    @classmethod
    def show_achievement_notification(cls, sim_info):
        if cls.notification is not None:
            dialog = cls.notification(sim_info, (SingleSimResolver(sim_info)), title=(lambda *_, **__: cls.display_name),
              text=(lambda *_, **__: cls.descriptive_text))
            dialog.show_dialog(icon_override=IconInfoData(icon_resource=(cls.icon)), event_id=(cls.guid64))


class AchievementCat(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ACHIEVEMENT_CATEGORY)):
    INSTANCE_TUNABLES = {'display_text':sims4.localization.TunableLocalizedString(description='\n            The name of this Achievement Category in the UI.\n            ',
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI), 
     'sorting_order':sims4.tuning.tunable.Tunable(description='\n            The sort order of this Achievement Category in the UI.\n            ',
       tunable_type=int,
       default=0,
       export_modes=sims4.tuning.tunable_base.ExportModes.All,
       tuning_group=GroupNames.UI)}


class AchievementCollection(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ACHIEVEMENT_COLLECTION)):
    INSTANCE_TUNABLES = {'display_text': sims4.localization.TunableLocalizedString(description='"\n            Text used to describe the achievement reward set.\n            ',
                       export_modes=(sims4.tuning.tunable_base.ExportModes.All),
                       tuning_group=(GroupNames.UI))}