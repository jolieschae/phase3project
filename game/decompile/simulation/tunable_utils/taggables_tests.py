# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\tunable_utils\taggables_tests.py
# Compiled at: 2020-11-12 10:43:22
# Size of source mod 2**32: 1698 bytes
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from caches import cached_test
from sims4.resources import Types
from sims4.tuning.tunable import TunableSet, TunableReference, AutoFactoryInit, HasTunableSingletonFactory
from tag import TunableTags
import services

class SituationIdentityTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'situation_list':TunableSet(description='\n            Test will pass if the specified reference is in the given list.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(Types.SITUATION)),
       pack_safe=True)), 
     'situation_tags':TunableTags(description='\n            Test will pass if the tested reference is tagged\n            with one of the tuned tags.\n            ',
       filter_prefixes=('situation', ))}

    @cached_test
    def __call__(self, situation):
        match = situation in self.situation_list or self.situation_tags & situation.tags
        if not match:
            return TestResult(False, 'Failed {}. Items Tested: {}. Tags Tested: {}', situation,
              (self.situation_list), (self.situation_tags), tooltip=(self.tooltip))
        return TestResult.TRUE