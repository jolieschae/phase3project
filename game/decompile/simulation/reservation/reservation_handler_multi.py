# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\reservation\reservation_handler_multi.py
# Compiled at: 2016-11-04 14:09:52
# Size of source mod 2**32: 3766 bytes
from reservation.reservation_handler import _ReservationHandler
from reservation.reservation_handler_interlocked import ReservationHandlerInterlocked
from reservation.reservation_handler_uselist import ReservationHandlerUseList
from reservation.reservation_result import ReservationResult
from sims4.tuning.tunable import TunableVariant, HasTunableSingletonFactory, AutoFactoryInit, TunableReference
import services, sims4.resources

class ReservationHandlerMulti(_ReservationHandler):

    class ReservationLimitStatBased(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'reservation_statistic': TunableReference(description="\n                The statistic that drives the number of reservations allowed on\n                the object. If the statistic's value is 3, then any attempt to\n                place a fourth reservation on the object would fail.\n                ",
                                    manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)))}

        def allows_reservation(self, obj, reservation_handler):
            stat_value = obj.get_stat_value(self.reservation_statistic)
            if stat_value is None:
                return ReservationResult(False, '{} does not have reservation statistic {}', obj, (self.reservation_statistic),
                  result_obj=obj)
            if stat_value < len(obj.get_users()):
                return ReservationResult(False, '{} has statistic {} lower than the required number of users', obj,
                  (self.reservation_statistic), result_obj=obj)
            return ReservationResult.TRUE

    FACTORY_TUNABLES = {'reservation_limit': TunableVariant(description='\n            Specify a limit to the number of reservations allowed on the object.\n            ',
                            stat_based=(ReservationLimitStatBased.TunableFactory()),
                            locked_args={'unlimited': None},
                            default='unlimited')}

    def allows_reservation(self, other_reservation_handler):
        if self._is_sim_allowed_to_clobber(other_reservation_handler):
            return ReservationResult.TRUE
        else:
            if isinstance(other_reservation_handler, ReservationHandlerUseList):
                return ReservationResult.TRUE
            else:
                if isinstance(other_reservation_handler, ReservationHandlerInterlocked):
                    return ReservationResult.TRUE
                return isinstance(other_reservation_handler, ReservationHandlerMulti) or ReservationResult(False, '{} only allows other ReservationHandlerMulti. {} is not', self,
                  other_reservation_handler, result_obj=(self.sim))
            if self.reservation_limit is not None:
                result = self.reservation_limit.allows_reservation(self._target, other_reservation_handler)
                if not result:
                    return result
        return ReservationResult.TRUE