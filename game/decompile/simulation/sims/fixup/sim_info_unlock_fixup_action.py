# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\fixup\sim_info_unlock_fixup_action.py
# Compiled at: 2019-09-16 16:25:55
# Size of source mod 2**32: 1903 bytes
from sims.fixup.sim_info_fixup_action import _SimInfoFixupAction
from sims.unlock_tracker import TunableUnlockVariant
from sims4.tuning.tunable import Tunable, TunableList
import random

class _SimInfoUnlockFixupAction(_SimInfoFixupAction):
    FACTORY_TUNABLES = {'potential_unlocks':TunableList(description='\n            List of unlocks that could be given to the Sim.\n            ',
       tunable=TunableUnlockVariant(description='\n            An unlock that could be given to the Sim.\n            ')), 
     'number_of_unlocks_to_grant':Tunable(description='\n            The number of unlocks that should be granted to the Sim.\n            ',
       tunable_type=int,
       default=1)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)

    def __call__(self, sim_info):
        unlock_list = list()
        for potential_unlock in self.potential_unlocks:
            unlock_list.append(potential_unlock)

        if unlock_list is not None:
            num_unlocks_remaining = min(self.number_of_unlocks_to_grant, len(unlock_list))
            while num_unlocks_remaining > 0:
                unlock_to_grant = random.choice(unlock_list)
                sim_info.unlock_tracker.add_unlock(unlock_to_grant, None)
                unlock_list.remove(unlock_to_grant)
                num_unlocks_remaining -= 1