# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\static_commodity.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 2648 bytes
from sims4.tuning.instance_manager import InstanceManager
from sims4.tuning.instances import TunedInstanceMetaclass
from sims4.tuning.tunable import Tunable, HasTunableReference
from sims4.utils import classproperty, flexproperty
from statistics.base_statistic import BaseStatistic
import services, sims4.resources

class StaticCommodity(HasTunableReference, BaseStatistic, metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.STATIC_COMMODITY)):
    INSTANCE_TUNABLES = {'ad_data': Tunable(description='\n                                Autonomous desire to fulfill this static commodity.  This is analogous to \n                                the returned ad curve value of regular commodities and should generally be\n                                between 0 and 1.  If a Sim has this static commodity, they will always \n                                desire it at this value.',
                  tunable_type=float,
                  default=0)}

    def __init__(self, tracker):
        super().__init__(tracker, 0)

    @classproperty
    def persisted(cls):
        return False

    @classmethod
    def type_id(cls):
        name_resource_key = sims4.resources.get_resource_key(cls.__name__, sims4.resources.Types.STATIC_COMMODITY)
        return name_resource_key.instance

    def set_value(self, value):
        raise NotImplementedError

    @classproperty
    def is_scored(cls):
        return True

    @flexproperty
    def autonomous_desire(cls, inst):
        this = inst if inst is not None else cls
        return this.ad_data

    def lock(self):
        raise NotImplementedError

    def unlock(self):
        raise NotImplementedError