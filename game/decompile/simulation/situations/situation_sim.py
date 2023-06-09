# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_sim.py
# Compiled at: 2021-06-14 20:07:21
# Size of source mod 2**32: 3494 bytes


class SituationSim:

    def __init__(self, sim):
        self._sim = sim
        self._current_job_type = None
        self._current_role_state_type = None
        self._local_score = 0
        self._emotional_buff_name = 'None'
        self.buff_handle = None
        self.outfit_priority_handle = None

    def destroy(self):
        self.set_role_state_type(None)
        self._sim = None

    @property
    def current_job_type(self):
        return self._current_job_type

    @current_job_type.setter
    def current_job_type(self, value):
        self.set_role_state_type(None, None)
        self._current_job_type = value

    def set_role_state_type(self, role_state_type, affordance_target=None, situation=None, **affordance_override_kwargs):
        if self._current_role_state_type is not None:
            self._sim.remove_role_of_type(self._current_role_state_type)
        self._current_role_state_type = role_state_type
        if self._current_role_state_type is not None:
            (self._sim.add_role)(self._current_role_state_type, affordance_target, situation=situation, **affordance_override_kwargs)

    @property
    def current_role_state_type(self):
        return self._current_role_state_type

    @property
    def current_role_state_instance(self):
        if self.current_role_state_type is None:
            return
        for role_instance in self._sim.active_roles():
            if isinstance(role_instance, self.current_role_state_type):
                return role_instance

    def get_total_score(self):
        return self._local_score

    def get_int_total_score(self):
        return int(round(self.get_total_score()))

    def update_score(self, delta):
        self._local_score += delta

    def set_emotional_buff_for_gsi(self, emotional_buff):
        if emotional_buff is not None:
            self._emotional_buff_name = emotional_buff.__name__

    @property
    def emotional_buff_name(self):
        return self._emotional_buff_name