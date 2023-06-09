# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\test_base.py
# Compiled at: 2020-11-12 10:43:18
# Size of source mod 2**32: 6129 bytes
from event_testing.resolver import RESOLVER_PARTICIPANT
from singletons import DEFAULT
import event_testing.results, sims4.localization, sims4.tuning.tunable

class BaseTest:
    test_events = ()
    USES_DATA_OBJECT = False
    UNIQUE_TARGET_TRACKING_AVAILABLE = False
    UNIQUE_POSTURE_TRACKING_AVAILABLE = False
    TAG_CHECKLIST_TRACKING_AVAILABLE = False
    USES_EVENT_DATA = False
    FACTORY_TUNABLES = {'tooltip': sims4.tuning.tunable.OptionalTunable(sims4.localization.TunableLocalizedStringFactory(description='Reason of failure.'))}
    __slots__ = ('tooltip', '_safe_to_skip', 'expected_kwargs', 'participants_for_early_testing',
                 '_supports_early_testing')

    def __init__(self, *args, safe_to_skip=False, tooltip=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        if not (tooltip is not None or hasattr(self, 'tooltip')):
            self.tooltip = tooltip
        self._safe_to_skip = safe_to_skip
        self.expected_kwargs = None
        self.participants_for_early_testing = None
        self._supports_early_testing = None

    def qualifies_for_cache_clear(self):
        return True

    def supports_early_testing(self):
        if self._supports_early_testing is None:
            if any((participant == RESOLVER_PARTICIPANT for participant in self.get_expected_args().values())):
                self._supports_early_testing = False
            else:
                self._supports_early_testing = True
        return self._supports_early_testing

    def has_tooltip(self):
        return self.tooltip is not None

    @property
    def safe_to_skip(self):
        return self._safe_to_skip

    @property
    def allow_failfast_tests(self):
        return True

    def get_target_id(self, **kwargs):
        pass

    def get_posture_id(self, **kwargs):
        pass

    def get_tags(self, **kwargs):
        return ()

    def save_relative_start_values(self, objective_guid64, data_object):
        pass

    def validate_tuning_for_objective(self, objective):
        pass

    def goal_value(self):
        return 1

    @property
    def is_goal_value_money(self):
        return False

    def get_test_events_to_register(self):
        return self.test_events

    def get_custom_event_registration_keys(self):
        return ()