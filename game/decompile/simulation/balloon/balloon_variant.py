# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\balloon\balloon_variant.py
# Compiled at: 2018-03-01 16:29:23
# Size of source mod 2**32: 1966 bytes
from balloon.balloon_icon import BalloonIcon
from event_testing.tests import TunableTestSet
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableFactory, TunableVariant, TunableReference
from singletons import DEFAULT
import gsi_handlers, services, sims4.resources

class BalloonVariant(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'tests': TunableTestSet(description='\n            A set of tests that are run when selecting the balloon icon.  If the\n            tests do not pass then this balloon icon will not be selected.\n            ')}

    @TunableFactory.factory_option
    def balloon_type(balloon_type=DEFAULT):
        return {'item': TunableVariant(balloon_icon=BalloonIcon.TunableFactory(locked_args=({} if balloon_type is DEFAULT else {'balloon_type': balloon_type})),
                   balloon_category=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.BALLOON)),
                   pack_safe=True),
                   default='balloon_icon')}

    def get_balloon_icons(self, resolver, gsi_test_result=None, **kwargs):
        if gsi_test_result is None or gsi_test_result:
            test_result = self.tests.run_tests(resolver)
        else:
            test_result = gsi_test_result
        if test_result or gsi_handlers.balloon_handlers.archiver.enabled:
            return (self.item().get_balloon_icons)(resolver, gsi_test_result=test_result, **kwargs)
        return []