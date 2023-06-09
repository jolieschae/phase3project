# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\game_effect_modifier\affordance_filter_modifier.py
# Compiled at: 2020-03-12 18:10:13
# Size of source mod 2**32: 4723 bytes
from game_effect_modifier.base_game_effect_modifier import BaseGameEffectModifier
from game_effect_modifier.game_effect_type import GameEffectType
from interactions.utils.affordance_filter import AffordanceFilterVariant
from event_testing.results import TestResult
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, OptionalTunable
import sims4.log
logger = sims4.log.Logger('Affordance Filter Modifiers', default_owner='jdimailig')

class _AffordanceFilter(HasTunableSingletonFactory, AutoFactoryInit):

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, _source, value):
        if not value.super_affordance_filter:
            if not value.mixer_affordance_filter:
                logger.error('{} does not supply any affordance filters in {}', instance_class, tunable_name)

    @staticmethod
    def _callback(instance_class, _tunable_name, _source, value):
        setattr(value, 'affordance_filter_source', instance_class)

    FACTORY_TUNABLES = {'super_affordance_filter':OptionalTunable(description='Filter on Super Interactions',
       tunable=AffordanceFilterVariant(),
       enabled_by_default=True), 
     'mixer_affordance_filter':OptionalTunable(description='Filter on Mixer Interactions',
       tunable=AffordanceFilterVariant()), 
     'callback':_callback, 
     'verify_tunable_callback':_verify_tunable_callback}

    def _filter_affordance(self, affordance):
        if affordance.is_super and self.super_affordance_filter is not None:
            return self.super_affordance_filter(affordance) or TestResult(False, 'Failed to pass super affordance filter on {}', self.affordance_filter_source)
        else:
            if self.mixer_affordance_filter is not None:
                if not self.mixer_affordance_filter(affordance):
                    return TestResult(False, 'Failed to pass mixer affordance filter on {}', self.affordance_filter_source)
        return TestResult.TRUE


class _AffordanceFilters(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'social_filters':OptionalTunable(description='If enabled, filters to apply to social interactions.',
       tunable=_AffordanceFilter.TunableFactory()), 
     'interaction_filters':OptionalTunable(description='If enabled, filters to apply to non-social interactions.',
       tunable=_AffordanceFilter.TunableFactory(locked_args={'mixer_affordance_filter': None}))}

    def filter_affordance(self, affordance):
        if affordance.is_social:
            if self.social_filters is not None:
                return self.social_filters._filter_affordance(affordance)
            return TestResult.TRUE
        if affordance.is_super:
            if self.interaction_filters is not None:
                return self.interaction_filters._filter_affordance(affordance)
            return TestResult.TRUE
        return TestResult.TRUE


class AffordanceFilterModifier(HasTunableSingletonFactory, AutoFactoryInit, BaseGameEffectModifier):

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, _source, value):
        if not value.as_actor:
            if not value.as_target:
                logger.error('{} does not supply any affordance filters for {}', instance_class, tunable_name)

    FACTORY_TUNABLES = {'as_actor':OptionalTunable(description='\n            Filters to apply when this Sim is the actor for an affordance.\n            ',
       tunable=_AffordanceFilters.TunableFactory()), 
     'as_target':OptionalTunable(description='\n            Filters to apply when this Sim is the target of an affordance.\n            ',
       tunable=_AffordanceFilters.TunableFactory()), 
     'verify_tunable_callback':_verify_tunable_callback}

    def __init__(self, **kwargs):
        (super().__init__)((GameEffectType.AFFORDANCE_FILTER_MODIFIER), **kwargs)