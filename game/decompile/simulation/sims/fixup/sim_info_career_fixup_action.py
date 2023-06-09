# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\fixup\sim_info_career_fixup_action.py
# Compiled at: 2019-09-16 16:28:01
# Size of source mod 2**32: 2102 bytes
import services, sims4
from rewards.reward_enums import RewardType
from sims.fixup.sim_info_fixup_action import _SimInfoFixupAction
from sims.fixup.sim_info_skill_fixup_action import _SimInfoSkillFixupAction
from sims4.tuning.tunable import TunableList, TunableReference
logger = sims4.log.Logger('CAS Stories', default_owner='rrodgers')

class _SimInfoCareerFixupAction(_SimInfoFixupAction):
    FACTORY_TUNABLES = {'career_level':TunableReference(description='\n            The career and level to assign to the \n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER_LEVEL)), 
     'skill_fixup_actions':TunableList(description='\n            Some career levels have skill requirements. Those requirements\n            should be tuned here as fixup actions so they can be fixed up as\n            well.\n            ',
       tunable=_SimInfoSkillFixupAction.TunableFactory())}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)

    def __call__(self, sim_info):
        career_type = self.career_level.career
        if not career_type.is_valid_career(sim_info=sim_info, from_join=True):
            logger.error('Tried to fixup {} with an invalid career: {}', sim_info, career_type)
            return
        for skill_fixup_action in self.skill_fixup_actions:
            skill_fixup_action(sim_info)

        career = career_type(sim_info)
        sim_info.career_tracker.add_career(career, career_level_override=(self.career_level), give_skipped_rewards=True, show_join_msg=False,
          disallowed_reward_types=(RewardType.MONEY,),
          force_rewards_to_sim_info_inventory=True,
          defer_first_assignment=True)
        sim_info.update_school_data()