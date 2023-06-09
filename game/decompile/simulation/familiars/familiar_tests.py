# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\familiars\familiar_tests.py
# Compiled at: 2019-07-31 17:46:49
# Size of source mod 2**32: 5440 bytes
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from familiars.familiar_enums import FamiliarType
from interactions import ParticipantTypeSingle
from sims4.tuning.tunable import TunableEnumEntry, HasTunableSingletonFactory, AutoFactoryInit, OptionalTunable, Tunable
from tunable_utils.tunable_white_black_list import TunableWhiteBlackList

class FamiliarTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description="\n            The subject who's familiar tracker we are checking.\n            ",
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Actor), 
     'familiar_type_filter':OptionalTunable(description='\n            If enabled then we will filter based on the familiar type.\n            ',
       tunable=TunableWhiteBlackList(description='\n                A filter on the type of familiar that is active.\n                ',
       tunable=TunableEnumEntry(description='\n                    The type of familiar to check for.\n                    ',
       tunable_type=FamiliarType,
       default=(FamiliarType.CAT)))), 
     'negate':Tunable(description='\n            If checked then we will negate the results of this test.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'subject': self.subject}

    def __call__(self, subject=None):
        for sim in subject:
            familiar_tracker = sim.sim_info.familiar_tracker
            if familiar_tracker is None:
                if self.negate:
                    return TestResult.TRUE
                return TestResult(False, '{} does not have a familiar tracker.',
                  sim,
                  tooltip=(self.tooltip))
                active_familiar = familiar_tracker.get_active_familiar()
                if active_familiar is None or active_familiar.is_hidden():
                    if self.negate:
                        return TestResult.TRUE
                    return TestResult(False, '{} does not have an active familiar.',
                      sim,
                      tooltip=(self.tooltip))
                if self.familiar_type_filter is not None:
                    if self.familiar_type_filter.test_item(familiar_tracker.active_familiar_type) or self.negate:
                        return TestResult.TRUE
                    return TestResult(False, "{}'s familiar is of type {} which doesn't pass the filter.",
                      sim,
                      (familiar_tracker.active_familiar_type),
                      tooltip=(self.tooltip))

        if self.negate:
            return TestResult(False, 'All sims pass the familiar requirements.',
              tooltip=(self.tooltip))
        return TestResult.TRUE


class HasFamiliarTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description="\n            The subject who's familiar tracker we are checking.\n            ",
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Actor), 
     'negate':Tunable(description='\n            If checked then we will negate the results of this test.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'subject': self.subject}

    def __call__(self, subject=None):
        for sim in subject:
            familiar_tracker = sim.sim_info.familiar_tracker
            if familiar_tracker is None:
                if self.negate:
                    return TestResult.TRUE
                    return TestResult(False, '{} does not have a familiar tracker.',
                      sim,
                      tooltip=(self.tooltip))
                    if familiar_tracker.has_familiars:
                        if self.negate:
                            return TestResult(False, '{} has at least one familiar.',
                              sim,
                              tooltip=(self.tooltip))
                else:
                    return self.negate or TestResult(False, '{} does not have any familiars.',
                      sim,
                      tooltip=(self.tooltip))

        return TestResult.TRUE