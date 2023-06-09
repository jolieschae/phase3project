# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\test_program.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 15491 bytes
import io, os, sys, subprocess
from test import support
import unittest, unittest.test

class Test_TestProgram(unittest.TestCase):

    def test_discovery_from_dotted_path(self):
        loader = unittest.TestLoader()
        tests = [
         self]
        expectedPath = os.path.abspath(os.path.dirname(unittest.test.__file__))
        self.wasRun = False

        def _find_tests(start_dir, pattern):
            self.wasRun = True
            self.assertEqual(start_dir, expectedPath)
            return tests

        loader._find_tests = _find_tests
        suite = loader.discover('unittest.test')
        self.assertTrue(self.wasRun)
        self.assertEqual(suite._tests, tests)

    def testNoExit(self):
        result = object()
        test = object()

        class FakeRunner(object):

            def run(self, test):
                self.test = test
                return result

        runner = FakeRunner()
        oldParseArgs = unittest.TestProgram.parseArgs

        def restoreParseArgs():
            unittest.TestProgram.parseArgs = oldParseArgs

        unittest.TestProgram.parseArgs = lambda *args: None
        self.addCleanup(restoreParseArgs)

        def removeTest():
            del unittest.TestProgram.test

        unittest.TestProgram.test = test
        self.addCleanup(removeTest)
        program = unittest.TestProgram(testRunner=runner, exit=False, verbosity=2)
        self.assertEqual(program.result, result)
        self.assertEqual(runner.test, test)
        self.assertEqual(program.verbosity, 2)

    class FooBar(unittest.TestCase):

        def testPass(self):
            pass

        def testFail(self):
            pass

    class FooBarLoader(unittest.TestLoader):

        def loadTestsFromModule(self, module):
            return self.suiteClass([
             self.loadTestsFromTestCase(Test_TestProgram.FooBar)])

        def loadTestsFromNames(self, names, module):
            return self.suiteClass([
             self.loadTestsFromTestCase(Test_TestProgram.FooBar)])

    def test_defaultTest_with_string(self):

        class FakeRunner(object):

            def run(self, test):
                self.test = test
                return True

        old_argv = sys.argv
        sys.argv = ['faketest']
        runner = FakeRunner()
        program = unittest.TestProgram(testRunner=runner, exit=False, defaultTest='unittest.test',
          testLoader=(self.FooBarLoader()))
        sys.argv = old_argv
        self.assertEqual(('unittest.test', ), program.testNames)

    def test_defaultTest_with_iterable(self):

        class FakeRunner(object):

            def run(self, test):
                self.test = test
                return True

        old_argv = sys.argv
        sys.argv = ['faketest']
        runner = FakeRunner()
        program = unittest.TestProgram(testRunner=runner,
          exit=False,
          defaultTest=[
         'unittest.test', 'unittest.test2'],
          testLoader=(self.FooBarLoader()))
        sys.argv = old_argv
        self.assertEqual(['unittest.test', 'unittest.test2'], program.testNames)

    def test_NonExit(self):
        program = unittest.main(exit=False, argv=[
         'foobar'],
          testRunner=unittest.TextTestRunner(stream=(io.StringIO())),
          testLoader=(self.FooBarLoader()))
        self.assertTrue(hasattr(program, 'result'))

    def test_Exit(self):
        self.assertRaises(SystemExit,
          (unittest.main),
          argv=[
         'foobar'],
          testRunner=unittest.TextTestRunner(stream=(io.StringIO())),
          exit=True,
          testLoader=(self.FooBarLoader()))

    def test_ExitAsDefault(self):
        self.assertRaises(SystemExit,
          (unittest.main),
          argv=[
         'foobar'],
          testRunner=unittest.TextTestRunner(stream=(io.StringIO())),
          testLoader=(self.FooBarLoader()))


class InitialisableProgram(unittest.TestProgram):
    exit = False
    result = None
    verbosity = 1
    defaultTest = None
    tb_locals = False
    testRunner = None
    testLoader = unittest.defaultTestLoader
    module = '__main__'
    progName = 'test'
    test = 'test'

    def __init__(self, *args):
        pass


RESULT = object()

class FakeRunner(object):
    initArgs = None
    test = None
    raiseError = 0

    def __init__(self, **kwargs):
        FakeRunner.initArgs = kwargs
        if FakeRunner.raiseError:
            FakeRunner.raiseError -= 1
            raise TypeError

    def run(self, test):
        FakeRunner.test = test
        return RESULT


class TestCommandLineArgs(unittest.TestCase):

    def setUp(self):
        self.program = InitialisableProgram()
        self.program.createTests = lambda: None
        FakeRunner.initArgs = None
        FakeRunner.test = None
        FakeRunner.raiseError = 0

    def testVerbosity(self):
        program = self.program
        for opt in ('-q', '--quiet'):
            program.verbosity = 1
            program.parseArgs([None, opt])
            self.assertEqual(program.verbosity, 0)

        for opt in ('-v', '--verbose'):
            program.verbosity = 1
            program.parseArgs([None, opt])
            self.assertEqual(program.verbosity, 2)

    def testBufferCatchFailfast(self):
        program = self.program
        for arg, attr in (('buffer', 'buffer'), ('failfast', 'failfast'), ('catch', 'catchbreak')):
            if attr == 'catch':
                if not hasInstallHandler:
                    continue
            setattr(program, attr, None)
            program.parseArgs([None])
            self.assertIs(getattr(program, attr), False)
            false = []
            setattr(program, attr, false)
            program.parseArgs([None])
            self.assertIs(getattr(program, attr), false)
            true = [
             42]
            setattr(program, attr, true)
            program.parseArgs([None])
            self.assertIs(getattr(program, attr), true)
            short_opt = '-%s' % arg[0]
            long_opt = '--%s' % arg
            for opt in (short_opt, long_opt):
                setattr(program, attr, None)
                program.parseArgs([None, opt])
                self.assertIs(getattr(program, attr), True)
                setattr(program, attr, False)
                with support.captured_stderr() as (stderr):
                    with self.assertRaises(SystemExit) as (cm):
                        program.parseArgs([None, opt])
                self.assertEqual(cm.exception.args, (2, ))
                setattr(program, attr, True)
                with support.captured_stderr() as (stderr):
                    with self.assertRaises(SystemExit) as (cm):
                        program.parseArgs([None, opt])
                self.assertEqual(cm.exception.args, (2, ))

    def testWarning(self):

        class FakeTP(unittest.TestProgram):

            def parseArgs(self, *args, **kw):
                pass

            def runTests(self, *args, **kw):
                pass

        warnoptions = sys.warnoptions[:]
        try:
            sys.warnoptions[:] = []
            self.assertEqual(FakeTP().warnings, 'default')
            self.assertEqual(FakeTP(warnings='ignore').warnings, 'ignore')
            sys.warnoptions[:] = ['somevalue']
            self.assertEqual(FakeTP().warnings, None)
            self.assertEqual(FakeTP(warnings='ignore').warnings, 'ignore')
        finally:
            sys.warnoptions[:] = warnoptions

    def testRunTestsRunnerClass(self):
        program = self.program
        program.testRunner = FakeRunner
        program.verbosity = 'verbosity'
        program.failfast = 'failfast'
        program.buffer = 'buffer'
        program.warnings = 'warnings'
        program.runTests()
        self.assertEqual(FakeRunner.initArgs, {'verbosity': "'verbosity'", 
         'failfast': "'failfast'", 
         'buffer': "'buffer'", 
         'tb_locals': False, 
         'warnings': "'warnings'"})
        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    def testRunTestsRunnerInstance(self):
        program = self.program
        program.testRunner = FakeRunner()
        FakeRunner.initArgs = None
        program.runTests()
        self.assertIsNone(FakeRunner.initArgs)
        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    def test_locals(self):
        program = self.program
        program.testRunner = FakeRunner
        program.parseArgs([None, '--locals'])
        self.assertEqual(True, program.tb_locals)
        program.runTests()
        self.assertEqual(FakeRunner.initArgs, {'buffer': False, 
         'failfast': False, 
         'tb_locals': True, 
         'verbosity': 1, 
         'warnings': None})

    def testRunTestsOldRunnerClass(self):
        program = self.program
        FakeRunner.raiseError = 2
        program.testRunner = FakeRunner
        program.verbosity = 'verbosity'
        program.failfast = 'failfast'
        program.buffer = 'buffer'
        program.test = 'test'
        program.runTests()
        self.assertEqual(FakeRunner.initArgs, {})
        self.assertEqual(FakeRunner.test, 'test')
        self.assertIs(program.result, RESULT)

    def testCatchBreakInstallsHandler(self):
        module = sys.modules['unittest.main']
        original = module.installHandler

        def restore():
            module.installHandler = original

        self.addCleanup(restore)
        self.installed = False

        def fakeInstallHandler():
            self.installed = True

        module.installHandler = fakeInstallHandler
        program = self.program
        program.catchbreak = True
        program.testRunner = FakeRunner
        program.runTests()
        self.assertTrue(self.installed)

    def _patch_isfile(self, names, exists=True):

        def isfile(path):
            return path in names

        original = os.path.isfile
        os.path.isfile = isfile

        def restore():
            os.path.isfile = original

        self.addCleanup(restore)

    def testParseArgsFileNames(self):
        program = self.program
        argv = ["'progname'", "'foo.py'", "'bar.Py'", "'baz.PY'", "'wing.txt'"]
        self._patch_isfile(argv)
        program.createTests = lambda: None
        program.parseArgs(argv)
        expected = [
         'foo', 'bar', 'baz', 'wing.txt']
        self.assertEqual(program.testNames, expected)

    def testParseArgsFilePaths(self):
        program = self.program
        argv = ['progname', 'foo/bar/baz.py', 'green\\red.py']
        self._patch_isfile(argv)
        program.createTests = lambda: None
        program.parseArgs(argv)
        expected = [
         'foo.bar.baz', 'green.red']
        self.assertEqual(program.testNames, expected)

    def testParseArgsNonExistentFiles(self):
        program = self.program
        argv = ['progname', 'foo/bar/baz.py', 'green\\red.py']
        self._patch_isfile([])
        program.createTests = lambda: None
        program.parseArgs(argv)
        self.assertEqual(program.testNames, argv[1:])

    def testParseArgsAbsolutePathsThatCanBeConverted(self):
        cur_dir = os.getcwd()
        program = self.program

        def _join(name):
            return os.path.join(cur_dir, name)

        argv = ['progname', _join('foo/bar/baz.py'), _join('green\\red.py')]
        self._patch_isfile(argv)
        program.createTests = lambda: None
        program.parseArgs(argv)
        expected = [
         'foo.bar.baz', 'green.red']
        self.assertEqual(program.testNames, expected)

    def testParseArgsAbsolutePathsThatCannotBeConverted(self):
        program = self.program
        argv = [
         'progname', '/foo/bar/baz.py', '/green/red.py']
        self._patch_isfile(argv)
        program.createTests = lambda: None
        program.parseArgs(argv)
        self.assertEqual(program.testNames, argv[1:])

    def testParseArgsSelectedTestNames(self):
        program = self.program
        argv = ["'progname'", "'-k'", "'foo'", "'-k'", "'bar'", "'-k'", "'*pat*'"]
        program.createTests = lambda: None
        program.parseArgs(argv)
        self.assertEqual(program.testNamePatterns, ['*foo*', '*bar*', '*pat*'])

    def testSelectedTestNamesFunctionalTest(self):

        def run_unittest(args):
            p = subprocess.Popen(([sys.executable, '-m', 'unittest'] + args), stdout=(subprocess.DEVNULL),
              stderr=(subprocess.PIPE),
              cwd=(os.path.dirname(__file__)))
            with p:
                _, stderr = p.communicate()
            return stderr.decode()

        t = '_test_warnings'
        self.assertIn('Ran 7 tests', run_unittest([t]))
        self.assertIn('Ran 7 tests', run_unittest(['-k', 'TestWarnings', t]))
        self.assertIn('Ran 7 tests', run_unittest(["'discover'", "'-p'", "'*_test*'", "'-k'", "'TestWarnings'"]))
        self.assertIn('Ran 2 tests', run_unittest(['-k', 'f', t]))
        self.assertIn('Ran 7 tests', run_unittest(['-k', 't', t]))
        self.assertIn('Ran 3 tests', run_unittest(['-k', '*t', t]))
        self.assertIn('Ran 7 tests', run_unittest(['-k', '*test_warnings.*Warning*', t]))
        self.assertIn('Ran 1 test', run_unittest(['-k', '*test_warnings.*warning*', t]))


if __name__ == '__main__':
    unittest.main()