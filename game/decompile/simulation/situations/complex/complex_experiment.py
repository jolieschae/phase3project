# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\complex_experiment.py
# Compiled at: 2016-10-20 19:42:24
# Size of source mod 2**32: 4968 bytes
from interactions import ParticipantType
from role.role_state import RoleState
from situations.situation_complex import SituationComplexCommon, SituationState, SituationStateData
from situations.situation_job import SituationJob
import alarms, clock, event_testing.tests_with_data, sims4.tuning.tunable

class SituationComplexExperiment(SituationComplexCommon):
    INSTANCE_TUNABLES = {'test_job':sims4.tuning.tunable.TunableTuple(situation_job=SituationJob.TunableReference(description='A reference to a SituationJob that can be performed at this Situation.'),
       friendly_role_state=RoleState.TunableReference(description='A role state the sim assigned to the job will perform'),
       angry_role_state=RoleState.TunableReference(description='A role state the sim assigned to the job will perform')), 
     '_host_job':sims4.tuning.tunable.TunableTuple(situation_job=SituationJob.TunableReference(description='A reference to a SituationJob that can be performed at this Situation.'),
       default_role_state=RoleState.TunableReference(description='A role state the sim assigned to the job will perform')), 
     'mean_test':event_testing.tests_with_data.TunableParticipantRanInteractionTest(locked_args={'participant':ParticipantType.TargetSim,  'interaction_outcome':None,  'running_time':None,  'tooltip':None}, description='Test for a mean interaction that will trigger a state change')}

    @classmethod
    def _states(cls):
        return (SituationStateData(1, AngrySituationState),
         SituationStateData(2, FriendlySituationState))

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        reader = self._seed.custom_init_params_reader
        if reader is None:
            self._test_bool = True
        else:
            self._test_bool = reader.read_bool('test_bool', True)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.test_job.situation_job, cls.test_job.friendly_role_state), (cls._host_job.situation_job, cls._host_job.default_role_state)]

    @classmethod
    def default_job(cls):
        return cls.test_job.situation_job

    @classmethod
    def resident_job(cls):
        return cls._host_job.situation_job

    def _save_custom_situation(self, writer):
        super()._save_custom_situation(writer)
        writer.write_bool('test_bool', False)

    def start_situation(self):
        super().start_situation()
        self._change_state(FriendlySituationState())


class AngrySituationState(SituationState):

    def on_activate(self, reader):
        super().on_activate(reader)
        self.owner._set_job_role_state(self.owner.test_job.situation_job, self.owner.test_job.angry_role_state)
        timeout = 10 if reader is None else reader.read_float('timer', 10)
        self._handle = alarms.add_alarm(self, clock.interval_in_sim_minutes(timeout), lambda _: self.timer_expired())

    def save_state(self, writer):
        super().save_state(writer)
        if self._handle is not None:
            writer.write_float('timer', self._handle.get_remaining_time().in_minutes())

    def on_deactivate(self):
        if self._handle is not None:
            alarms.cancel_alarm(self._handle)
        super().on_deactivate()

    def timer_expired(self):
        self._change_state(FriendlySituationState())


class FriendlySituationState(SituationState):

    def __init__(self):
        super().__init__()
        self._test_int = 12

    def on_activate(self, reader):
        super().on_activate(reader)
        custom_keys = self.owner.mean_test.get_custom_event_registration_keys()
        for _, custom_key in custom_keys:
            self._test_event_register(event_testing.test_events.TestEvent.InteractionComplete, custom_key)

        self.owner._set_job_role_state(self.owner.test_job.situation_job, self.owner.test_job.friendly_role_state)
        if reader is not None:
            self._test_int = reader.read_uint32('test_uint32', 24)

    def save_state(self, writer):
        super().save_state(writer)
        writer.write_uint32('test_uint32', self._test_int)

    def handle_event(self, sim_info, event, resolver):
        if self.owner.test_interaction_complete_by_job_holder(sim_info, resolver, self.owner.test_job.situation_job, self.owner.mean_test):
            self._change_state(AngrySituationState())