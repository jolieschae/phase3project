# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\tested_variant.py
# Compiled at: 2020-11-02 18:44:27
# Size of source mod 2**32: 4614 bytes
from civic_policies.street_civic_policy_tests import StreetCivicPolicyTest
from conditional_layers.conditional_layer_tests import ConditionalLayerLoadedTest
from event_testing.tests import TunableTestSet
from sims4.tuning.tunable import TunableVariant, HasTunableSingletonFactory, AutoFactoryInit, TunableList, TunableTuple
import event_testing, global_policies, narrative
from venues.civic_policies.venue_civic_policy_tests import VenueCivicPolicyTest
from zone_tests import ZoneTest

class TunableTestedVariant(TunableVariant):

    @staticmethod
    def _create_tested_selector(tunable_type, is_noncallable_type=False):

        class _TestedSelector(HasTunableSingletonFactory):
            FACTORY_TUNABLES = {'records': TunableList(tunable=TunableTuple(tests=(TunableTestSet()),
                          item=tunable_type))}

            def __call__(self, *args, resolver=None, **kwargs):
                for item_pair in self.records:
                    if item_pair.tests.run_tests(resolver):
                        if is_noncallable_type:
                            return item_pair.item
                        return (item_pair.item)(args, resolver=resolver, **kwargs)

        return _TestedSelector.TunableFactory()

    @staticmethod
    def _create_noncallable_item_factory(tunable_type):

        class _NonCallableItem(HasTunableSingletonFactory):
            FACTORY_TUNABLES = {'item': tunable_type}

            def __call__(self, *args, **kwargs):
                return self.item

        return _NonCallableItem.TunableFactory()

    def __init__(self, tunable_type, is_noncallable_type=False, **kwargs):
        (super().__init__)(single=TunableTestedVariant._create_noncallable_item_factory(tunable_type) if is_noncallable_type else tunable_type, 
         tested=TunableTestedVariant._create_tested_selector(tunable_type, is_noncallable_type=is_noncallable_type), 
         default='single', **kwargs)


class TunableGlobalTestList(event_testing.tests.TestListLoadingMixin):
    DEFAULT_LIST = event_testing.tests.TestList()

    def __init__(self, description=None):
        if description is None:
            description = 'A list of tests.  All tests must succeed to pass the TestSet.'
        super().__init__(description=description, tunable=(TunableGlobalTestVariant()))


class TunableGlobalTestVariant(TunableVariant):

    def __init__(self, description='A tunable test supported for a global resolver.', **kwargs):
        (super().__init__)(narrative=narrative.narrative_tests.NarrativeTest.TunableFactory(locked_args={'tooltip': None}), 
         global_policy=global_policies.global_policy_tests.GlobalPolicyStateTest.TunableFactory(locked_args={'tooltip': None}), 
         street_civic_policy=StreetCivicPolicyTest.TunableFactory(locked_args={'tooltip': None}), 
         venue_civic_policy=VenueCivicPolicyTest.TunableFactory(locked_args={'tooltip': None}), 
         conditional_layer_loaded=ConditionalLayerLoadedTest.TunableFactory(locked_args={'tooltip': None}), 
         zone=ZoneTest.TunableFactory(locked_args={'tooltip': None}), 
         description=description, **kwargs)