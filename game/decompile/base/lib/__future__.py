# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\__future__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 5247 bytes
all_feature_names = [
 "'nested_scopes'", 
 "'generators'", 
 "'division'", 
 "'absolute_import'", 
 "'with_statement'", 
 "'print_function'", 
 "'unicode_literals'", 
 "'barry_as_FLUFL'", 
 "'generator_stop'", 
 "'annotations'"]
__all__ = [
 'all_feature_names'] + all_feature_names
CO_NESTED = 16
CO_GENERATOR_ALLOWED = 0
CO_FUTURE_DIVISION = 8192
CO_FUTURE_ABSOLUTE_IMPORT = 16384
CO_FUTURE_WITH_STATEMENT = 32768
CO_FUTURE_PRINT_FUNCTION = 65536
CO_FUTURE_UNICODE_LITERALS = 131072
CO_FUTURE_BARRY_AS_BDFL = 262144
CO_FUTURE_GENERATOR_STOP = 524288
CO_FUTURE_ANNOTATIONS = 1048576

class _Feature:

    def __init__(self, optionalRelease, mandatoryRelease, compiler_flag):
        self.optional = optionalRelease
        self.mandatory = mandatoryRelease
        self.compiler_flag = compiler_flag

    def getOptionalRelease(self):
        return self.optional

    def getMandatoryRelease(self):
        return self.mandatory

    def __repr__(self):
        return '_Feature' + repr((self.optional,
         self.mandatory,
         self.compiler_flag))


nested_scopes = _Feature((2, 1, 0, 'beta', 1), (2, 2, 0, 'alpha', 0), CO_NESTED)
generators = _Feature((2, 2, 0, 'alpha', 1), (2, 3, 0, 'final', 0), CO_GENERATOR_ALLOWED)
division = _Feature((2, 2, 0, 'alpha', 2), (3, 0, 0, 'alpha', 0), CO_FUTURE_DIVISION)
absolute_import = _Feature((2, 5, 0, 'alpha', 1), (3, 0, 0, 'alpha', 0), CO_FUTURE_ABSOLUTE_IMPORT)
with_statement = _Feature((2, 5, 0, 'alpha', 1), (2, 6, 0, 'alpha', 0), CO_FUTURE_WITH_STATEMENT)
print_function = _Feature((2, 6, 0, 'alpha', 2), (3, 0, 0, 'alpha', 0), CO_FUTURE_PRINT_FUNCTION)
unicode_literals = _Feature((2, 6, 0, 'alpha', 2), (3, 0, 0, 'alpha', 0), CO_FUTURE_UNICODE_LITERALS)
barry_as_FLUFL = _Feature((3, 1, 0, 'alpha', 2), (3, 9, 0, 'alpha', 0), CO_FUTURE_BARRY_AS_BDFL)
generator_stop = _Feature((3, 5, 0, 'beta', 1), (3, 7, 0, 'alpha', 0), CO_FUTURE_GENERATOR_STOP)
annotations = _Feature((3, 7, 0, 'beta', 1), (4, 0, 0, 'alpha', 0), CO_FUTURE_ANNOTATIONS)