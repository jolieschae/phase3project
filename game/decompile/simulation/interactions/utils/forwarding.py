# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\forwarding.py
# Compiled at: 2017-10-04 13:45:02
# Size of source mod 2**32: 940 bytes
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit
from tunable_utils.tunable_object_filter import TunableObjectFilterVariant
import sims4.log
logger = sims4.log.Logger('Interactions')

class Forwarding(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'object_filter': TunableObjectFilterVariant(description='\n            The object we want to forward this interaction *on* must satisfy\n            this filter.\n            ',
                        default=(TunableObjectFilterVariant.FILTER_ALL))}

    def is_allowed_to_forward(self, interaction, obj):
        if not self.object_filter.is_object_valid(obj):
            return False
        return True