# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\game_effect_modifier\affordance_reference_scoring_modifier.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 9150 bytes
from game_effect_modifier.base_game_effect_modifier import BaseGameEffectModifier
from game_effect_modifier.game_effect_type import GameEffectType
from interactions.base.basic import TunableBasicExtras
from interactions.utils.tunable_icon import TunableIconAllPacks
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import Tunable, TunablePercent, TunableList, TunableReference, TunableSet, TunableEnumEntry, TunableSingletonFactory, OptionalTunable
from tag import Tag
import event_testing.tests, services, sims4.log, snippets
logger = sims4.log.Logger('AffordanceModifier')

class AffordanceReferenceScoringModifier(BaseGameEffectModifier):
    FACTORY_TUNABLES = {'content_score_bonus':Tunable(description='\n            When determine content score for affordances and afforance matches\n            tuned here, content score is increased by this amount.\n            ',
       tunable_type=int,
       default=0), 
     'success_modifier':TunablePercent(description='\n            Amount to adjust percent success chance. For example, tuning 10%\n            will increase success chance by 10% over the base success chance.\n            Additive with other buffs.\n            ',
       default=0,
       minimum=-100), 
     'affordances':TunableList(description='\n            A list of affordances that will be compared against.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       pack_safe=True)), 
     'affordance_lists':TunableList(description='\n            A list of affordance snippets that will be compared against.\n            ',
       tunable=snippets.TunableAffordanceListReference(pack_safe=True)), 
     'interaction_category_tags':TunableSet(description='\n            This attribute is used to test for affordances that contain any of the tags in this set.\n            ',
       tunable=TunableEnumEntry(description='\n                These tag values are used for testing interactions.\n                ',
       tunable_type=Tag,
       default=(Tag.INVALID))), 
     'interaction_category_blacklist_tags':TunableSet(description='\n            Any interaction with a tag in this set will NOT be modiified.\n            Affects display name on a per interaction basis.\n            ',
       tunable=TunableEnumEntry(description='\n                These tag values are used for testing interactions.\n                ',
       tunable_type=Tag,
       default=(Tag.INVALID))), 
     'pie_menu_parent_name':OptionalTunable(description='\n            If enabled, we will insert the name into this parent string\n            in the pie menu.  Only affected by test and blacklist tags\n            (for performance reasons)\n            ',
       tunable=TunableLocalizedStringFactory(description='\n                A string to wrap the normal interaction name.  Token 0 is actor,\n                Token 1 is the normal name.\n                ')), 
     'new_pie_menu_icon':TunableIconAllPacks(description="\n            Icon to put on interactions that pass test (interaction resolver)\n            and don't match blacklist tags.\n            ",
       allow_none=True), 
     'basic_extras':TunableBasicExtras(description='\n            Basic extras to add to interactions that match. \n            '), 
     'test':event_testing.tests.TunableTestSet(description='\n            The test to run to see if this affordance modifier should be applied. Ors of Ands.\n            ')}

    def __init__(self, content_score_bonus=0, success_modifier=0, affordances=(), affordance_lists=(), interaction_category_tags=set(), interaction_category_blacklist_tags=set(), pie_menu_parent_name=None, new_pie_menu_icon=None, basic_extras=(), test=None):
        super().__init__(GameEffectType.AFFORDANCE_MODIFIER)
        self._score_bonus = content_score_bonus
        self._success_modifier = success_modifier
        self._affordances = affordances
        self._affordance_lists = affordance_lists
        self._interaction_category_tags = interaction_category_tags
        self._interaction_category_blacklist_tags = interaction_category_blacklist_tags
        self._pie_menu_parent_name = pie_menu_parent_name
        self._new_pie_menu_icon = new_pie_menu_icon
        self._basic_extras = basic_extras
        self._test = test

    def is_type(self, affordance, resolver):

        def test_results():
            if not self._test:
                return True
            result = False
            try:
                result = self._test.run_tests(resolver)
            except:
                pass

            return result

        if affordance is not None:
            if affordance.interaction_category_tags & self._interaction_category_blacklist_tags:
                return False
            if affordance in self._affordances:
                return test_results()
            for affordances in self._affordance_lists:
                if affordance in affordances:
                    return test_results()

            if affordance.interaction_category_tags & self._interaction_category_tags:
                return test_results()
            if self._interaction_category_blacklist_tags and not self._affordances:
                if not self._affordance_lists:
                    if not self._interaction_category_tags:
                        return test_results()
        elif self._pie_menu_parent_name or self._new_pie_menu_icon:
            return test_results()
        return False

    def get_score_for_type(self, affordance, resolver):
        if self.is_type(affordance, resolver):
            return self._score_bonus
        return 0

    def get_success_for_type(self, affordance, resolver):
        if self.is_type(affordance, resolver):
            return self._success_modifier
        return 0

    def get_new_pie_menu_icon_and_parent_name_for_type(self, affordance, resolver):
        if self.is_type(affordance, resolver):
            return (
             self._new_pie_menu_icon, self._pie_menu_parent_name, self._interaction_category_blacklist_tags)
        return (None, None, None)

    def get_basic_extras_for_type(self, affordance, resolver):
        if self.is_type(affordance, resolver):
            return self._basic_extras
        return []

    def debug_affordances_gen(self):
        for affordance in self._affordances:
            yield affordance.__name__

        for affordnace_snippet in self._affordance_lists:
            yield affordnace_snippet.__name__


TunableAffordanceScoringModifier = TunableSingletonFactory.create_auto_factory(AffordanceReferenceScoringModifier)