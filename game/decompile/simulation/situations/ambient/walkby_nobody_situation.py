# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\ambient\walkby_nobody_situation.py
# Compiled at: 2015-04-06 16:26:37
# Size of source mod 2**32: 1826 bytes
from sims4.utils import classproperty
from situations.situation_complex import SituationState, SituationStateData
import sims4.tuning.instances, situations.bouncer, situations.situation_complex

class WalkbyNobodySituation(situations.situation_complex.SituationComplexCommon):
    REMOVE_INSTANCE_TUNABLES = situations.situation.Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _NobodyState),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return []

    @classmethod
    def default_job(cls):
        pass

    def start_situation(self):
        super().start_situation()
        self._change_state(_NobodyState())

    @classmethod
    def get_sims_expected_to_be_in_situation(cls):
        return 1

    @classmethod
    def _can_start_walkby(cls, lot_id: int):
        return True

    @classproperty
    def situation_serialization_option(cls):
        return situations.situation_types.SituationSerializationOption.OPEN_STREETS


sims4.tuning.instances.lock_instance_tunables(WalkbyNobodySituation, exclusivity=(situations.bouncer.bouncer_types.BouncerExclusivityCategory.WALKBY),
  creation_ui_option=(situations.situation_types.SituationCreationUIOption.NOT_AVAILABLE))

class _NobodyState(SituationState):
    pass