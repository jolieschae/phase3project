# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\results.py
# Compiled at: 2021-11-22 21:29:05
# Size of source mod 2**32: 7120 bytes
from sims4.utils import constproperty
import collections

class ExecuteResult(collections.namedtuple('_ExecuteResult', ('result', 'interaction', 'reason'))):
    __slots__ = ()
    NONE = None

    def __bool__(self):
        if self.result:
            return True
        return False

    def __repr__(self):
        if self.interaction is not None:
            return '<ExecuteResult: {}: ({}) - {}>'.format(self.result, self.reason, self.interaction)
        return '<ExecuteResult: {}: ({})>'.format(self.result, self.reason)


class TestResult:
    __slots__ = ('result', 'tooltip', '_reason', '_format_args', 'icon', 'influence_by_active_mood')
    TRUE = None
    NONE = None

    def __init__(self, result, *args, tooltip=None, icon=None, influence_by_active_mood=False):
        if result is None:
            raise AssertionError('Attempting to create a TestResult from None, some test function is missing return True/False')
        else:
            self.result = result
            self.tooltip = tooltip
            if args:
                self._reason, self._format_args = args[0], args[1:]
            else:
                self._reason, self._format_args = (None, ())
        self.icon = icon
        self.influence_by_active_mood = influence_by_active_mood

    @property
    def reason(self):
        if self._format_args:
            if self._reason:
                self._reason = (self._reason.format)(*self._format_args)
                self._format_args = ()
        return self._reason

    @constproperty
    def is_numeric():
        return False

    def __str__(self):
        if self.reason:
            return self.reason
        return str(bool(self.result))

    def __repr__(self):
        if self.reason:
            return '<TestResult: {0} ({1})>'.format(bool(self.result), self.reason)
        return '<TestResult: {0}>'.format(bool(self.result))

    def __eq__(self, other):
        if isinstance(other, bool):
            return self.result is other
        if isinstance(other, TestResult):
            return self.result == other.result
        return super().__eq__(other)

    def __ne__(self, other):
        return not self == other

    def __bool__(self):
        return self.result

    def __and__(self, other):
        result = self.result and other.result
        tooltip = self.tooltip or other.tooltip
        if self._reason:
            reason = self._reason
            format_args = self._format_args
        else:
            reason = other._reason
            format_args = other._format_args
        if result:
            icon = self.icon or other.icon
            influence_by_active_mood = self.influence_by_active_mood or other.influence_by_active_mood
        else:
            icon = None
            influence_by_active_mood = False
        return TestResult(result, reason, *format_args, **{'tooltip':tooltip,  'icon':icon,  'influence_by_active_mood':influence_by_active_mood})


class TestResultNumeric(TestResult):
    __slots__ = ('current_value', 'goal_value', 'is_money')

    def __init__(self, result, *args, current_value, goal_value, is_money=False, tooltip=None):
        self.current_value = current_value
        self.goal_value = goal_value
        self.is_money = is_money
        (super().__init__)(result, *args, **{'tooltip': tooltip})

    @constproperty
    def is_numeric():
        return True


class EnqueueResult(collections.namedtuple('_EnqueueResult', ('test_result', 'execute_result'))):
    __slots__ = ()
    NONE = None

    def __new__(cls, test_result, execute_result):
        if test_result is None:
            if execute_result is None:
                if cls.NONE is not None:
                    return cls.NONE
        if test_result is None:
            test_result = TestResult.NONE
        if execute_result is None:
            execute_result = ExecuteResult.NONE
        return super(EnqueueResult, cls).__new__(cls, test_result, execute_result)

    def __bool__(self):
        if self.test_result:
            if self.execute_result:
                return True
        return False

    def __repr__(self):
        return '<EnqueueResult: {0} {1}>'.format(self.test_result, self.execute_result)

    @property
    def interaction(self):
        return self.execute_result.interaction


ExecuteResult.NONE = ExecuteResult(False, None, None)
TestResult.TRUE = TestResult(True)
TestResult.NONE = TestResult(False)
EnqueueResult.NONE = EnqueueResult(None, None)