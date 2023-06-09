# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\looping_interaction_situation.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 12966 bytes
from event_testing.test_events import TestEvent
from event_testing.tests import TunableTestSet
from interactions.base.interaction import InteractionFailureOptions
from interactions.context import InteractionContext, QueueInsertStrategy
from interactions.interaction_finisher import FinishingType
from interactions.priority import Priority
from sims4.tuning.tunable import Tunable, TunablePackSafeReference
from singletons import DEFAULT
from situations.situation import Situation
from situations.situation_complex import SituationComplexCommon, SituationStateData, CommonSituationState, TunableSituationJobAndRoleState
import interactions.aop, services, sims4.resources, situations, operator
OBJECT_TOKEN = 'object_id'

class RunInteractionState(CommonSituationState):
    FACTORY_TUNABLES = {'max_retry_attempts': Tunable(description='\n            The number of times the Sim can fail to successfully run the \n            tuned interaction before giving up and moving on to the next \n            object as a target.\n            ',
                             tunable_type=int,
                             default=3)}

    def __init__(self, *args, targets=None, interaction=None, max_retry_attempts=None, basic_extra=None, previous_si=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.targets = targets
        self.interaction = interaction
        self._retry_count = 0
        self._target = None
        self.max_retry_attempts = max_retry_attempts
        self.basic_extra = basic_extra
        self._previous_si = previous_si
        self._interaction_instance = None

    def on_activate(self, reader=None):
        if not self.find_target_and_push_interaction():
            if not self.targets:
                self.owner._self_destruct()
            else:
                self.retry_interaction()
            return
        self._test_event_register(TestEvent.InteractionStart)
        self._test_event_register(TestEvent.InteractionExitedPipeline)

    def handle_event(self, sim_info, event, resolver):
        if event == TestEvent.InteractionStart:
            if resolver.interaction is self._interaction_instance:
                if self._additional_tests(sim_info, event, resolver):
                    self._on_interaction_of_interest_start()
                    return
        elif event == TestEvent.InteractionExitedPipeline:
            if resolver.interaction is self._interaction_instance and self._additional_tests(sim_info, event, resolver):
                if resolver.interaction.has_been_user_canceled:
                    self.cancel_interaction()
                    return
                if not resolver.interaction.is_finishing_naturally:
                    self._on_interaction_of_interest_failure()
                return

    def _on_interaction_of_interest_start(self):
        self.owner.advance_to_next_object((self.targets), previous_si=(self._interaction_instance))

    def _on_interaction_of_interest_failure(self):
        self.retry_interaction()

    def _additional_tests(self, sim_info, event, resolver):
        return self.owner.is_sim_in_situation(sim_info.get_sim_instance())

    def cancel_interaction(self):
        self.owner._self_destruct()

    def timer_expired(self):
        self.owner.advance_to_next_object(previous_si=(self._interaction_instance))

    def find_target_and_push_interaction(self):
        if self.targets is None:
            self.owner._self_destruct()
            return
        sim = self.owner.initiating_sim_info.get_sim_instance()
        failed_connectivity_obj = None
        for obj in sorted((self.targets), key=(operator.attrgetter('part_group_index'))):
            if self._previous_si is not None:
                context = self._previous_si.context.clone_for_continuation(self._previous_si)
            else:
                context = InteractionContext(sim, (InteractionContext.SOURCE_SCRIPT),
                  (Priority.High),
                  insert_strategy=(QueueInsertStrategy.FIRST))
            resolver = self.interaction.get_resolver(target=obj, context=context)
            if not self.owner.tests.run_tests(resolver):
                self.targets.remove(obj)
                continue
            if not obj.is_connected(sim):
                failed_connectivity_obj = obj
                self.targets.remove(obj)
                continue
            self.targets.remove(obj)
            self._target = obj
            return self.push_interaction(context=context)

        if failed_connectivity_obj is not None:
            route_fail_context = InteractionContext(sim, (InteractionContext.SOURCE_SCRIPT),
              (Priority.High),
              insert_strategy=(QueueInsertStrategy.NEXT))
            result = sim.push_super_affordance((InteractionFailureOptions.ROUTE_FAILURE_AFFORDANCE), failed_connectivity_obj,
              route_fail_context, interaction_name=self.interaction.get_name(target=failed_connectivity_obj, context=route_fail_context),
              interaction_icon_info=self.interaction.get_icon_info(target=failed_connectivity_obj, context=route_fail_context))
        return False

    def push_interaction(self, context=DEFAULT):
        for sim in self.owner.all_sims_in_situation_gen():
            if context is DEFAULT:
                context = InteractionContext(sim, (InteractionContext.SOURCE_SCRIPT), (Priority.High),
                  insert_strategy=(QueueInsertStrategy.NEXT))
            aop = interactions.aop.AffordanceObjectPair(self.interaction, self._target, self.interaction, None)
            test_result, execute_result = aop.test_and_execute(context)
            self._interaction_instance = execute_result[1]
            if self.basic_extra:
                if self._interaction_instance is not None:
                    self._interaction_instance.add_additional_instance_basic_extra(self.basic_extra)
            return test_result

    def retry_interaction(self):
        self._retry_count += 1
        if self._retry_count < self.max_retry_attempts:
            self.push_interaction()
        else:
            self._retry_count = 0
            self.owner.advance_to_next_object((self.targets), previous_si=(self._interaction_instance))


class LoopingInteractionSituation(situations.situation_complex.SituationComplexCommon):
    INSTANCE_TUNABLES = {'tendor_job_and_role_state':TunableSituationJobAndRoleState(description='\n            Job and Role State for the Sim in this situation.\n            '), 
     'interaction':TunablePackSafeReference(description='\n            The interaction that the Sim will run in looping succession on\n            the object(s) specified if the tests pass.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION)), 
     'tests':TunableTestSet(description='\n            The tests that muss pass for the Sim to run the tuned interaction\n            with the object as the target.\n            '), 
     'run_interaction_state':RunInteractionState.TunableFactory(description='\n            Situation State used to run the tuned interaction on a specific\n            object.\n            ',
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP)}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        reader = self._seed.custom_init_params_reader
        self.targets = None
        self._retry_count = 0
        self.interaction_override = self._seed.extra_kwargs.get('interaction', None)
        self.basic_extra = self._seed.extra_kwargs.get('basic_extra', ())
        if reader is None:
            self._target_id = self._seed.extra_kwargs.get('default_target_id', None)
        else:
            self._target_id = reader.read_uint64(OBJECT_TOKEN, None)
        if self._target_id is not None:
            target = services.object_manager().get(self._target_id)
            if target.parts:
                self.targets = set(target.parts)
            else:
                self.targets = set((target,))

    @classmethod
    def default_job(cls):
        pass

    @classmethod
    def _states(cls):
        return (SituationStateData(1, RunInteractionState, factory=(cls.run_interaction_state)),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.tendor_job_and_role_state.job, cls.tendor_job_and_role_state.role_state)]

    def _on_set_sim_job(self, sim, job_type):
        super()._on_set_sim_job(sim, job_type)
        self._change_state(self.run_interaction_state(targets=(self.targets), interaction=(self.looping_interaction),
          basic_extra=(self.basic_extra)))

    def advance_to_next_object(self, targets, previous_si=None):
        self._change_state(self.run_interaction_state(targets=targets, interaction=(self.looping_interaction),
          basic_extra=(self.basic_extra),
          previous_si=previous_si))

    @property
    def looping_interaction(self):
        if self.interaction_override is not None:
            return self.interaction_override
        return self.interaction