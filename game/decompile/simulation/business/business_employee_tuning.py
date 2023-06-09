# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\business\business_employee_tuning.py
# Compiled at: 2016-04-28 01:42:22
# Size of source mod 2**32: 8508 bytes
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunablePackSafeReference, TunableMapping, TunablePercent, TunableRange, TunablePackSafeResourceKey, TunableReference, TunableResourceKey, TunableTuple
from sims4.tuning.tunable_base import GroupNames
from snippets import define_snippet
import services, sims4.resources

class BusinessEmployeeData(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'career':TunableReference(description='\n            The Career that employees of this type will have applied to them.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER)), 
     'employee_count_default':TunableRange(description='\n            The number of this type of employee the player will be able to hire by default\n            ',
       tunable_type=int,
       default=1,
       minimum=0), 
     'employee_count_max':TunableRange(description='\n            The maximum number of employees allowed to be hired. This assumes\n            all perks have been unlocked.\n            ',
       tunable_type=int,
       default=3,
       minimum=0), 
     'employee_skills':TunableMapping(description='\n            A mapping of employee skills to their data.\n            ',
       key_type=TunableReference(description='\n                A skill on the employee. The Sim Filter that generates this\n                employee should also apply this skill.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
       class_restrictions=('Skill', ),
       pack_safe=True),
       value_type=TunableTuple(description='\n                The data associated with the tuned employee skill.\n                ',
       weight=TunablePercent(description="\n                    The weight of this skill's completion level. This is used to\n                    compute a weighted average of skill completion.\n                    \n                    e.g. If all skills are maxed out, and their weights are all\n                    100%, the average completion is 100%.\n                    \n                    If there are two skills, both maxed out, one of which has a 50%\n                    weight while the other has a 100% weight, the average completion\n                    is 75%.\n                    ",
       default=100),
       business_summary_description=TunableLocalizedString(description='\n                    The description displayed in the business summary UI for\n                    this skill.\n                    '))), 
     'weighted_skill_to_career_level_ratio':TunableRange(description='\n            The ratio between the computed weighted average of the employee skills\n            and the desired career level within the retail career.\n            \n            e.g. All skills are equally weighted, and the average skill level is 50%\n            completion.\n            \n            If this value is 100%, then the employee will start in (and desire to\n            be), at 50% progression within the career.\n            \n            If this value is 50%, then the employee will start in (and desire to\n            be), at 25% progression within the career.\n            ',
       tunable_type=float,
       default=1,
       minimum=0), 
     'career_level_delta_buffs':TunableMapping(description="\n            A dictionary mapping the delta in career level and desired\n            career level to a buff that is applied when employee matches the delta.\n            \n            e.g. A Sim is hired at their desired career level. They would be\n            awarded the buff corresponding to entry '0'.\n            \n            e.g. A Sim is hired at a level 2 employee but desires to be level 5.\n            They would be awarded the buff corresponding to '-3'.\n            ",
       key_type=int,
       value_type=TunablePackSafeReference(description='\n                The buff to be awarded when the specified difference between\n                career level and desired career level matches.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.BUFF)))), 
     'satisfaction_commodity':TunablePackSafeReference(description="\n            The commodity representing this employee type's satisfaction. Its\n            states are used to populate the UI for the business.\n            ",
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       class_restrictions=('Commodity', )), 
     'potential_employee_pool_filter':TunablePackSafeReference(description='\n            The filter to use when looking at Sims to hire this employee type.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SIM_FILTER)), 
     'potential_employee_pool_size':TunableRange(description="\n            The number of Sims shown in the hire picker. If you want the cap\n            raised, you'll need to chat with a GPE. There are performance\n            concerns with generating too many SimInfos.\n            ",
       tunable_type=int,
       default=6,
       minimum=1,
       maximum=9), 
     'uniform_pose':TunablePackSafeReference(description='\n            The post that mannequins in CAS are in when designing the uniform\n            for this employee type.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.ANIMATION),
       class_restrictions=('ObjectPose', )), 
     'uniform_male':TunablePackSafeResourceKey(description='\n            The SimInfo file to use when editing male uniforms for this employee type.\n            ',
       default=None,
       resource_types=(
      sims4.resources.Types.SIMINFO,)), 
     'uniform_female':TunablePackSafeResourceKey(description='\n            ',
       default=None,
       resource_types=(
      sims4.resources.Types.SIMINFO,)), 
     'interaction_hire':TunablePackSafeReference(description='\n            The interaction to run when hiring this type of employee via the UI.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION)), 
     'interaction_fire':TunablePackSafeReference(description='\n            The interaction to run when firing this type of employee via the UI.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION)), 
     'interaction_promote':TunablePackSafeReference(description='\n            The interaction to run when promoting this type of employee via the UI.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION)), 
     'interaction_demote':TunablePackSafeReference(description='\n            The interaction to run when demoting this type of employee via the UI.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION)), 
     'job_name':TunableLocalizedString(description='\n            The name of this business job.\n            ',
       tuning_group=GroupNames.UI), 
     'job_icon':TunableResourceKey(description='\n            The icon for this business job.\n            ',
       resource_types=sims4.resources.CompoundTypes.IMAGE,
       tuning_group=GroupNames.UI)}


_, TunableBusinessEmployeeDataSnippet = define_snippet('BusinessEmployeeData', BusinessEmployeeData.TunableFactory())