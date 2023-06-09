# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\ambient\walkby_consumer_situation.py
# Compiled at: 2020-05-06 18:26:18
# Size of source mod 2**32: 12080 bytes
import random
from crafting.crafting_interactions import create_craftable
from event_testing.test_events import TestEvent
from objects import ALL_HIDDEN_REASONS
from sims4.tuning.tunable import TunableList, TunableReference, TunableInterval, TunableSimMinute, TunableVariant, TunableTuple
from sims4.utils import classproperty
from situations.situation_complex import SituationStateData, CommonSituationState, CommonInteractionCompletedSituationState
import services, sims4.tuning.instances, situations.bouncer, situations.situation_complex
RECIPE_CREATION = 0
DEFINITION_CREATION = 1

class StartingState(CommonInteractionCompletedSituationState):
    FACTORY_TUNABLES = {'create_object': TunableVariant(description='\n            How to create the object.\n            ',
                        create_via_recipe=TunableTuple(description='\n                Create the object using a recipe.\n                ',
                        possible_recipes=TunableList(description='\n                    The possible recipes that can be chosen for this walker.\n                    ',
                        tunable=TunableReference(description='\n                        A recipe that can be chosen for the walker to have.\n                        ',
                        manager=(services.get_instance_manager(sims4.resources.Types.RECIPE)))),
                        locked_args={'creation_method': RECIPE_CREATION}),
                        create_via_object_definition=TunableTuple(description='\n                Create the object using an object definition\n                ',
                        possible_objects=TunableList(description='\n                    The possible objects that can be chosen for this walker.\n                    ',
                        tunable=TunableReference(description='\n                        A object that can be chosen for the walker to have.\n                        ',
                        manager=(services.definition_manager()))),
                        locked_args={'creation_method': DEFINITION_CREATION}),
                        default='create_via_recipe')}

    def __init__(self, *args, create_object, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._chosen_recipe = None
        self._chosen_object = None
        if create_object.creation_method == RECIPE_CREATION:
            self._chosen_recipe = random.choice(create_object.possible_recipes)
        else:
            self._chosen_object = random.choice(create_object.possible_objects)

    def _get_role_state_overrides(self, sim, job_type, role_state_type, role_affordance_target):
        target = self.owner.get_created_object()
        if target is None:
            if self._chosen_recipe is not None:
                target = create_craftable((self._chosen_recipe),
                  sim,
                  owning_household_id_override=(services.active_household_id()),
                  place_in_inventory=True)
                if target is None:
                    raise ValueError('No craftable created for {} on {}'.format(self._chosen_recipe, self))
            elif self._chosen_object is not None:
                target = self.owner._create_object_for_situation(sim, self._chosen_object)
                if target is None:
                    raise ValueError('No object created for {} on {}'.format(self._chosen_object, self))
            else:
                raise ValueError('No valid object to create for {}'.format(self))
            self.owner._created_object_id = target.id
        if target is not None:
            target.transient = True
        return (
         role_state_type, target)

    def on_activate(self, reader=None):
        super().on_activate(reader)
        for custom_key in self._interaction_of_interest.custom_keys_gen():
            self._test_event_register(TestEvent.InteractionStart, custom_key)

    def handle_event(self, sim_info, event, resolver):
        if event == TestEvent.InteractionStart:
            if resolver(self._interaction_of_interest):
                if self._additional_tests(sim_info, event, resolver):
                    self._on_interaction_of_interest_complete()

    def _on_interaction_of_interest_complete(self, **kwargs):
        self._change_state(self.owner._leave_state())

    def _additional_tests(self, sim_info, event, resolver):
        sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is None:
            return False
        return self.owner.is_sim_in_situation(sim)


LEAVE_STATE_TIMEOUT = 'leave_state_timeout'

class LeaveState(CommonSituationState):
    FACTORY_TUNABLES = {'timeout': TunableInterval(description='\n            Time amount of time in Sim Minutes that must pass before switching\n            into the next\n            state.\n            ',
                  tunable_type=TunableSimMinute,
                  default_lower=10,
                  default_upper=100,
                  minimum=0)}

    def __init__(self, *args, timeout=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._timeout = timeout

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        self._create_or_load_alarm(LEAVE_STATE_TIMEOUT, (self._timeout.random_float()),
          (self.timer_expired),
          should_persist=True,
          reader=reader)

    def timer_expired(self, _):
        if self.owner is None:
            return
        self.owner._change_state(self.owner._wait_a_bit_state())


WAIT_AROUND_STATE_TIMEOUT = 'wait_around_state_timeout'

class WaitAroundState(CommonSituationState):
    FACTORY_TUNABLES = {'timeout': TunableInterval(description='\n            Time amount of time that must pass before switching into the next\n            state.\n            ',
                  tunable_type=TunableSimMinute,
                  default_lower=5,
                  default_upper=10,
                  minimum=0)}

    def __init__(self, *args, timeout=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._timeout = timeout

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        self._create_or_load_alarm(WAIT_AROUND_STATE_TIMEOUT, (self._timeout.random_float()),
          (self.timer_expired),
          should_persist=True,
          reader=reader)

    def timer_expired(self, _):
        self.owner._change_state(self.owner._leave_state())

    def _on_set_sim_role_state(self, sim, *args, **kwargs):
        (super()._on_set_sim_role_state)(sim, *args, **kwargs)
        self.owner._cancel_leave_interaction(sim)


CREATED_OBJECT_TOKEN = 'created_object'

class WalkbyConsumerSituation(situations.situation_complex.SituationComplexCommon):
    INSTANCE_TUNABLES = {'_starting_state':StartingState.TunableFactory(description='\n            The initial starting state for this situation.  When this situation\n            starts the Sim will generate and begin consuming an item before\n            moving to the leave state.\n            ',
       locked_args={'allow_join_situation':True, 
      'time_out':None}), 
     '_leave_state':LeaveState.TunableFactory(description='\n            State for the Sim to leave.  At tuned intervals the sim will switch\n            into the wait a bit state.\n            ',
       locked_args={'allow_join_situation':True, 
      'time_out':None}), 
     '_wait_a_bit_state':WaitAroundState.TunableFactory(description='\n            The state where the Sims wait around and continue running their\n            consume interaction.  After a few sim minutes they will return to\n            the leave state.\n            ',
       locked_args={'allow_join_situation':True, 
      'time_out':None})}
    REMOVE_INSTANCE_TUNABLES = situations.situation.Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        reader = self._seed.custom_init_params_reader
        if reader is None:
            self._created_object_id = None
        else:
            self._created_object_id = reader.read_uint64(CREATED_OBJECT_TOKEN, None)
            if self._starting_state.create_object.creation_method == DEFINITION_CREATION:
                self._claim_object(self._created_object_id)

    @classmethod
    def _states(cls):
        return (SituationStateData(1, StartingState, factory=(cls._starting_state)),
         SituationStateData(2, LeaveState, factory=(cls._leave_state)),
         SituationStateData(3, WaitAroundState, factory=(cls._wait_a_bit_state)))

    @classmethod
    def default_job(cls):
        pass

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return list(cls._starting_state._tuned_values.job_and_role_changes.items())

    def start_situation(self):
        super().start_situation()
        self._change_state(self._starting_state())

    @classmethod
    def get_sims_expected_to_be_in_situation(cls):
        return 1

    @classmethod
    def _can_start_walkby(cls, lot_id: int):
        return True

    @classproperty
    def situation_serialization_option(cls):
        return situations.situation_types.SituationSerializationOption.OPEN_STREETS

    @property
    def _should_cancel_leave_interaction_on_premature_removal(self):
        return True

    def _save_custom_situation(self, writer):
        super()._save_custom_situation(writer)
        if self._created_object_id is not None:
            writer.write_uint64(CREATED_OBJECT_TOKEN, self._created_object_id)

    def get_created_object(self):
        created_object = None
        if self._created_object_id is not None:
            created_object = services.inventory_manager().get(self._created_object_id)
            if created_object is None:
                created_object = services.object_manager().get(self._created_object_id)
        return created_object

    def _on_set_sim_job(self, sim, job_type):
        super()._on_set_sim_job(sim, job_type)
        created_item = self.get_created_object()
        if created_item is not None:
            created_item.transient = True


sims4.tuning.instances.lock_instance_tunables(WalkbyConsumerSituation, exclusivity=(situations.bouncer.bouncer_types.BouncerExclusivityCategory.WALKBY),
  creation_ui_option=(situations.situation_types.SituationCreationUIOption.NOT_AVAILABLE))