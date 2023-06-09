# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\suite.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 10800 bytes
import sys
from . import case
from . import util
__unittest = True

def _call_if_exists(parent, attr):
    func = getattr(parent, attr, (lambda: None))
    func()


class BaseTestSuite(object):
    _cleanup = True

    def __init__(self, tests=()):
        self._tests = []
        self._removed_tests = 0
        self.addTests(tests)

    def __repr__(self):
        return '<%s tests=%s>' % (util.strclass(self.__class__), list(self))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return list(self) == list(other)

    def __iter__(self):
        return iter(self._tests)

    def countTestCases(self):
        cases = self._removed_tests
        for test in self:
            if test:
                cases += test.countTestCases()

        return cases

    def addTest(self, test):
        if not callable(test):
            raise TypeError('{} is not callable'.format(repr(test)))
        if isinstance(test, type):
            if issubclass(test, (
             case.TestCase, TestSuite)):
                raise TypeError('TestCases and TestSuites must be instantiated before passing them to addTest()')
        self._tests.append(test)

    def addTests(self, tests):
        if isinstance(tests, str):
            raise TypeError('tests must be an iterable of tests, not a string')
        for test in tests:
            self.addTest(test)

    def run(self, result):
        for index, test in enumerate(self):
            if result.shouldStop:
                break
            test(result)
            if self._cleanup:
                self._removeTestAtIndex(index)

        return result

    def _removeTestAtIndex(self, index):
        try:
            test = self._tests[index]
        except TypeError:
            pass
        else:
            if hasattr(test, 'countTestCases'):
                self._removed_tests += test.countTestCases()
            self._tests[index] = None

    def __call__(self, *args, **kwds):
        return (self.run)(*args, **kwds)

    def debug(self):
        for test in self:
            test.debug()


class TestSuite(BaseTestSuite):

    def run(self, result, debug=False):
        topLevel = False
        if getattr(result, '_testRunEntered', False) is False:
            result._testRunEntered = topLevel = True
        for index, test in enumerate(self):
            if result.shouldStop:
                break
            if _isnotsuite(test):
                self._tearDownPreviousClass(test, result)
                self._handleModuleFixture(test, result)
                self._handleClassSetUp(test, result)
                result._previousTestClass = test.__class__
                if getattr(test.__class__, '_classSetupFailed', False) or getattr(result, '_moduleSetUpFailed', False):
                    continue
                elif not debug:
                    test(result)
                else:
                    test.debug()
                if self._cleanup:
                    self._removeTestAtIndex(index)

        if topLevel:
            self._tearDownPreviousClass(None, result)
            self._handleModuleTearDown(result)
            result._testRunEntered = False
        return result

    def debug(self):
        debug = _DebugResult()
        self.run(debug, True)

    def _handleClassSetUp(self, test, result):
        previousClass = getattr(result, '_previousTestClass', None)
        currentClass = test.__class__
        if currentClass == previousClass:
            return
        if result._moduleSetUpFailed:
            return
        if getattr(currentClass, '__unittest_skip__', False):
            return
        try:
            currentClass._classSetupFailed = False
        except TypeError:
            pass

        setUpClass = getattr(currentClass, 'setUpClass', None)
        if setUpClass is not None:
            _call_if_exists(result, '_setupStdout')
            try:
                try:
                    setUpClass()
                except Exception as e:
                    try:
                        if isinstance(result, _DebugResult):
                            raise
                        currentClass._classSetupFailed = True
                        className = util.strclass(currentClass)
                        errorName = 'setUpClass (%s)' % className
                        self._addClassOrModuleLevelException(result, e, errorName)
                    finally:
                        e = None
                        del e

            finally:
                _call_if_exists(result, '_restoreStdout')

    def _get_previous_module(self, result):
        previousModule = None
        previousClass = getattr(result, '_previousTestClass', None)
        if previousClass is not None:
            previousModule = previousClass.__module__
        return previousModule

    def _handleModuleFixture(self, test, result):
        previousModule = self._get_previous_module(result)
        currentModule = test.__class__.__module__
        if currentModule == previousModule:
            return
        self._handleModuleTearDown(result)
        result._moduleSetUpFailed = False
        try:
            module = sys.modules[currentModule]
        except KeyError:
            return
        else:
            setUpModule = getattr(module, 'setUpModule', None)
            if setUpModule is not None:
                _call_if_exists(result, '_setupStdout')
                try:
                    try:
                        setUpModule()
                    except Exception as e:
                        try:
                            if isinstance(result, _DebugResult):
                                raise
                            result._moduleSetUpFailed = True
                            errorName = 'setUpModule (%s)' % currentModule
                            self._addClassOrModuleLevelException(result, e, errorName)
                        finally:
                            e = None
                            del e

                finally:
                    _call_if_exists(result, '_restoreStdout')

    def _addClassOrModuleLevelException(self, result, exception, errorName):
        error = _ErrorHolder(errorName)
        addSkip = getattr(result, 'addSkip', None)
        if addSkip is not None and isinstance(exception, case.SkipTest):
            addSkip(error, str(exception))
        else:
            result.addError(error, sys.exc_info())

    def _handleModuleTearDown(self, result):
        previousModule = self._get_previous_module(result)
        if previousModule is None:
            return
        if result._moduleSetUpFailed:
            return
        try:
            module = sys.modules[previousModule]
        except KeyError:
            return
        else:
            tearDownModule = getattr(module, 'tearDownModule', None)
            if tearDownModule is not None:
                _call_if_exists(result, '_setupStdout')
                try:
                    try:
                        tearDownModule()
                    except Exception as e:
                        try:
                            if isinstance(result, _DebugResult):
                                raise
                            errorName = 'tearDownModule (%s)' % previousModule
                            self._addClassOrModuleLevelException(result, e, errorName)
                        finally:
                            e = None
                            del e

                finally:
                    _call_if_exists(result, '_restoreStdout')

    def _tearDownPreviousClass(self, test, result):
        previousClass = getattr(result, '_previousTestClass', None)
        currentClass = test.__class__
        if currentClass == previousClass:
            return
        if getattr(previousClass, '_classSetupFailed', False):
            return
        if getattr(result, '_moduleSetUpFailed', False):
            return
        if getattr(previousClass, '__unittest_skip__', False):
            return
        tearDownClass = getattr(previousClass, 'tearDownClass', None)
        if tearDownClass is not None:
            _call_if_exists(result, '_setupStdout')
            try:
                try:
                    tearDownClass()
                except Exception as e:
                    try:
                        if isinstance(result, _DebugResult):
                            raise
                        className = util.strclass(previousClass)
                        errorName = 'tearDownClass (%s)' % className
                        self._addClassOrModuleLevelException(result, e, errorName)
                    finally:
                        e = None
                        del e

            finally:
                _call_if_exists(result, '_restoreStdout')


class _ErrorHolder(object):
    failureException = None

    def __init__(self, description):
        self.description = description

    def id(self):
        return self.description

    def shortDescription(self):
        pass

    def __repr__(self):
        return '<ErrorHolder description=%r>' % (self.description,)

    def __str__(self):
        return self.id()

    def run(self, result):
        pass

    def __call__(self, result):
        return self.run(result)

    def countTestCases(self):
        return 0


def _isnotsuite(test):
    try:
        iter(test)
    except TypeError:
        return True
    else:
        return False


class _DebugResult(object):
    _previousTestClass = None
    _moduleSetUpFailed = False
    shouldStop = False