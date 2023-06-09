# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\support.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 3890 bytes
import unittest

class TestEquality(object):

    def test_eq(self):
        for obj_1, obj_2 in self.eq_pairs:
            self.assertEqual(obj_1, obj_2)
            self.assertEqual(obj_2, obj_1)

    def test_ne(self):
        for obj_1, obj_2 in self.ne_pairs:
            self.assertNotEqual(obj_1, obj_2)
            self.assertNotEqual(obj_2, obj_1)


class TestHashing(object):

    def test_hash(self):
        for obj_1, obj_2 in self.eq_pairs:
            try:
                if not hash(obj_1) == hash(obj_2):
                    self.fail('%r and %r do not hash equal' % (obj_1, obj_2))
            except Exception as e:
                try:
                    self.fail('Problem hashing %r and %r: %s' % (obj_1, obj_2, e))
                finally:
                    e = None
                    del e

        for obj_1, obj_2 in self.ne_pairs:
            try:
                if hash(obj_1) == hash(obj_2):
                    self.fail("%s and %s hash equal, but shouldn't" % (
                     obj_1, obj_2))
            except Exception as e:
                try:
                    self.fail('Problem hashing %s and %s: %s' % (obj_1, obj_2, e))
                finally:
                    e = None
                    del e


class _BaseLoggingResult(unittest.TestResult):

    def __init__(self, log):
        self._events = log
        super().__init__()

    def startTest(self, test):
        self._events.append('startTest')
        super().startTest(test)

    def startTestRun(self):
        self._events.append('startTestRun')
        super().startTestRun()

    def stopTest(self, test):
        self._events.append('stopTest')
        super().stopTest(test)

    def stopTestRun(self):
        self._events.append('stopTestRun')
        super().stopTestRun()

    def addFailure(self, *args):
        self._events.append('addFailure')
        (super().addFailure)(*args)

    def addSuccess(self, *args):
        self._events.append('addSuccess')
        (super().addSuccess)(*args)

    def addError(self, *args):
        self._events.append('addError')
        (super().addError)(*args)

    def addSkip(self, *args):
        self._events.append('addSkip')
        (super().addSkip)(*args)

    def addExpectedFailure(self, *args):
        self._events.append('addExpectedFailure')
        (super().addExpectedFailure)(*args)

    def addUnexpectedSuccess(self, *args):
        self._events.append('addUnexpectedSuccess')
        (super().addUnexpectedSuccess)(*args)


class LegacyLoggingResult(_BaseLoggingResult):

    @property
    def addSubTest(self):
        raise AttributeError


class LoggingResult(_BaseLoggingResult):

    def addSubTest(self, test, subtest, err):
        if err is None:
            self._events.append('addSubTestSuccess')
        else:
            self._events.append('addSubTestFailure')
        super().addSubTest(test, subtest, err)


class ResultWithNoStartTestRunStopTestRun(object):

    def __init__(self):
        self.failures = []
        self.errors = []
        self.testsRun = 0
        self.skipped = []
        self.expectedFailures = []
        self.unexpectedSuccesses = []
        self.shouldStop = False

    def startTest(self, test):
        pass

    def stopTest(self, test):
        pass

    def addError(self, test):
        pass

    def addFailure(self, test):
        pass

    def addSuccess(self, test):
        pass

    def wasSuccessful(self):
        return True