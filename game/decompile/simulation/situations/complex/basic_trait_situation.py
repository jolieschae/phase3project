# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\basic_trait_situation.py
# Compiled at: 2019-01-15 18:48:45
# Size of source mod 2**32: 2382 bytes
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableReference
from sims4.utils import classproperty
from situations.bouncer.bouncer_types import BouncerExclusivityCategory
from situations.situation import Situation
from situations.situation_complex import SituationState, SituationComplexCommon, SituationStateData
from situations.situation_types import SituationSerializationOption, SituationCreationUIOption
import services, sims4.resources

class BasicTraitSituationState(SituationState):
    pass


class BasicTraitSitaution(SituationComplexCommon):
    INSTANCE_TUNABLES = {'job':TunableReference(description='\n            The job of the Sim with the trait.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)), 
     'role':TunableReference(description='\n            The role of the Sim with the trait.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.ROLE_STATE))}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _states(cls):
        return (SituationStateData(1, BasicTraitSituationState),)

    @classmethod
    def default_job(cls):
        pass

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.job, cls.role)]

    @classproperty
    def situation_serialization_option(cls):
        return SituationSerializationOption.DONT

    def start_situation(self):
        super().start_situation()
        self._change_state(BasicTraitSituationState())


lock_instance_tunables(BasicTraitSitaution, exclusivity=(BouncerExclusivityCategory.NEUTRAL),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE))