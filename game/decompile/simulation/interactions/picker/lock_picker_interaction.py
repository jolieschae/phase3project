# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\picker\lock_picker_interaction.py
# Compiled at: 2018-08-20 14:33:09
# Size of source mod 2**32: 3434 bytes
from interactions.base.picker_interaction import SimPickerInteraction
from objects.components.portal_lock_data import IndividualSimDoorLockData
from objects.components.portal_locking_enums import LockPriority, LockSide, ClearLock
from sims4.tuning.tunable import TunableEnumEntry
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
import enum, services

class LockOperationType(enum.Int):
    LOCK = 0
    UNLOCK = 1


class LockHouseholdSimsPickerInteraction(SimPickerInteraction):
    INSTANCE_TUNABLES = {'lock_operation': TunableEnumEntry(description='\n            Define the type of lock operation that should be made on this\n            portal.\n            ',
                         tunable_type=LockOperationType,
                         default=(LockOperationType.LOCK),
                         tuning_group=(GroupNames.PICKERTUNING))}

    @flexmethod
    def _get_valid_sim_choices_gen(cls, inst, target, context, **kwargs):
        if context.sim is None:
            return
        for filter_result in (super()._get_valid_sim_choices_gen)(target, context, **kwargs):
            sim_locked = target.test_lock(filter_result.sim_info)
            if cls.lock_operation == LockOperationType.LOCK:
                if sim_locked:
                    continue
            elif not sim_locked:
                continue
            yield filter_result

    def _on_successful_picker_selection(self, results=()):
        sim_info_manager = services.sim_info_manager()
        for sim_id in results:
            sim_info = sim_info_manager.get(sim_id)
            if sim_info is None:
                continue
            if self.lock_operation == LockOperationType.LOCK:
                lock_data = IndividualSimDoorLockData(lock_sim=sim_info, lock_priority=(LockPriority.PLAYER_LOCK),
                  lock_sides=(LockSide.LOCK_BOTH),
                  should_persist=True)
                self.target.add_lock_data(lock_data, replace_same_lock_type=False, clear_existing_locks=(ClearLock.CLEAR_OTHER_LOCK_TYPES))
            else:
                lock_data = IndividualSimDoorLockData(unlock_sim=sim_info, lock_priority=(LockPriority.PLAYER_LOCK),
                  lock_sides=(LockSide.LOCK_BOTH),
                  should_persist=True)
                self.target.add_lock_data(lock_data, replace_same_lock_type=False, clear_existing_locks=(ClearLock.CLEAR_NONE))