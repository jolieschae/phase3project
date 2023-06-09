# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\template_affordance_provider\tunable_affordance_template_discipline.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 2692 bytes
from interactions.utils.loot_element import LootElement
from sims.template_affordance_provider.tunable_affordance_template_base import TunableAffordanceTemplateBase
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableList, TunableVariant
import services, sims4.resources

class TunableDisciplineBasicExtras(TunableList):

    def __init__(self, **kwargs):
        (super().__init__)(description='\n            Basic Extras to run at the outcome of this template interaction.\n            ', 
         tunable=TunableVariant(loot=(LootElement.TunableFactory())), **kwargs)


class TunableAffordanceTemplateDiscipline(HasTunableSingletonFactory, AutoFactoryInit, TunableAffordanceTemplateBase):
    FACTORY_TUNABLES = {'template_affordance':TunableReference(description='\n            The affordance to use as a template.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION),
       class_restrictions=('DisciplineTemplateSuperInteraction', 'DisciplineTemplateSocialSuperInteraction'),
       pack_safe=True), 
     'display_name_override':TunableLocalizedStringFactory(description='\n            The name to use for this template interaction.\n            '), 
     'outcome_basic_extras':TunableDisciplineBasicExtras()}

    def get_template_affordance(self):
        return self.template_affordance

    def get_template_kwargs(self):
        return {'template_display_name':self.display_name_override, 
         'template_outcome_basic_extras':self.outcome_basic_extras}