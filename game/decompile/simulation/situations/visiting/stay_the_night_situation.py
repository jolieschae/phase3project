# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\visiting\stay_the_night_situation.py
# Compiled at: 2015-04-03 18:03:00
# Size of source mod 2**32: 2978 bytes
from role.role_state import RoleState
from situations.situation_complex import SituationState, SituationStateData
from situations.situation_job import SituationJob
from situations.visiting.visiting_situation_common import VisitingNPCSituation
import services, sims4.tuning.instances, sims4.tuning.tunable, situations.bouncer, tunable_time

class StayTheNightSituation(VisitingNPCSituation):
    INSTANCE_TUNABLES = {'invited_job':sims4.tuning.tunable.TunableTuple(situation_job=SituationJob.TunableReference(description='\n                          The situation job for the sim spending the night.\n                          '),
       staying_role_state=RoleState.TunableReference(description='\n                          The role state for the sim spending the night.\n                          ')), 
     'when_to_leave':tunable_time.TunableTimeOfDay(description='\n            The time of day for the invited sim to leave.\n            ',
       default_hour=7)}

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _StayState),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.invited_job.situation_job, cls.invited_job.staying_role_state)]

    @classmethod
    def default_job(cls):
        return cls.invited_job.situation_job

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._start_time = None

    def start_situation(self):
        super().start_situation()
        self._start_time = services.time_service().sim_now
        self._change_state(_StayState())

    def _get_duration(self):
        if self._seed.duration_override is not None:
            return self._seed.duration_override
        time_span = self._start_time.time_till_next_day_time(self.when_to_leave)
        return time_span.in_minutes()


sims4.tuning.instances.lock_instance_tunables(StayTheNightSituation, exclusivity=(situations.bouncer.bouncer_types.BouncerExclusivityCategory.VISIT),
  creation_ui_option=(situations.situation_types.SituationCreationUIOption.NOT_AVAILABLE),
  duration=0,
  _implies_greeted_status=True)

class _StayState(SituationState):
    pass