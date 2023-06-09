# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\fire_brigade_situation.py
# Compiled at: 2020-03-09 19:49:50
# Size of source mod 2**32: 8773 bytes
import random
from buffs.tunable import TunablePackSafeBuffReference
from event_testing.tests_with_data import TunableParticipantRanInteractionTest
from sims4.tuning.tunable import Tunable, TunableList, TunableRegionDescription, TunableRange, TunablePercent, TunableReference
from sims4.tuning.tunable_base import GroupNames
from situations.bouncer.bouncer_types import RequestSpawningOption, BouncerRequestPriority
from situations.situation_complex import SituationComplexCommon, CommonSituationState, SituationState, SituationStateData
from situations.situation_guest_list import SituationGuestInfo, SituationGuestList
from world.region import Region
import event_testing, services, sims4

class _FireOutState(SituationState):

    def on_activate(self, reader):
        super().on_activate(reader)
        if self.owner.neighor_saved_me_buff:
            if self.owner._fire_brigade_put_out_fire:
                for sim_info in services.active_household().instanced_sims_gen():
                    sim_info.add_buff_from_op(self.owner.neighor_saved_me_buff.buff_type, self.owner.neighor_saved_me_buff.buff_reason)

        if self.owner.visit_afterwards:
            for fire_brigade_volunteer in self.owner.get_fire_brigade_sim_infos():
                services.get_zone_situation_manager().create_visit_situation(fire_brigade_volunteer)

        self.owner._self_destruct()


class _FindFireState(CommonSituationState):

    def on_activate(self, reader):
        super().on_activate(reader)
        for fire_panic_tests in self.owner.fire_panic_interactions:
            for _, custom_key in fire_panic_tests.get_custom_event_registration_keys():
                self._test_event_register(event_testing.test_events.TestEvent.InteractionComplete, custom_key)

    def _test_event(self, event, sim_info, resolver, test):
        if event in test.test_events:
            if sim_info in self.owner.get_fire_brigade_sim_infos():
                return resolver(test)
        return False

    def handle_event(self, sim_info, event, resolver):
        if self.owner._fire_brigade_put_out_fire:
            return
        for fire_panic_interaction_test in self.owner.fire_panic_interactions:
            if self._test_event(event, sim_info, resolver, fire_panic_interaction_test):
                self.owner._fire_brigade_put_out_fire = True
                break


class FireBrigadeSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'_find_fire_state':_FindFireState.TunableFactory(description='\n            The situation state used to put the fire brigade volunteers in\n            the role that directs them to put out active fires.\n            ',
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP), 
     'fire_panic_interactions':TunableList(description='\n            A list of interactions that, if completed by the fire brigade volunteer,\n            marks that the volunteers have helped to put out the fire. If the volunteer\n            completes a fire-panic-interaction by the time the situation ends\n            every instanced member of the active household will get the \n            helped-by-neighbor buff.\n            ',
       tunable=TunableParticipantRanInteractionTest(),
       tuning_group=GroupNames.SITUATION), 
     'number_of_volunteers':TunableRange(description='\n            The number of brigade volunteers the situation will attempt\n            to get when creating the fire service.\n            ',
       tunable_type=int,
       default=2,
       minimum=0,
       tuning_group=GroupNames.SITUATION), 
     'neighor_saved_me_buff':TunablePackSafeBuffReference(description='\n            The buff given to all members of the active household once the fire\n            situation has finished. The buff is given only if a fire brigade\n            member helped put out the fire.                    \n            ',
       tuning_group=GroupNames.SITUATION), 
     'visit_afterwards':Tunable(description='\n            Boolean to control whether sim will visit after the fire is out or not.             \n            ',
       tunable_type=bool,
       default=False), 
     'fire_brigade_job':TunableReference(description='\n            The job that a fire brigade volunteer will use.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION_JOB),
       tuning_group=GroupNames.ROLES)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._fire_brigade_put_out_fire = False
        self._fire_brigade_sim_infos = []

    @classmethod
    def _states(cls):
        return [SituationStateData(1, _FindFireState, factory=(cls._find_fire_state)),
         SituationStateData(2, _FireOutState)]

    def get_fire_brigade_sim_infos(self):
        return self._fire_brigade_sim_infos

    def _on_set_sim_job(self, sim, job_type):
        super()._on_set_sim_job(sim, job_type)
        self._fire_brigade_sim_infos.append(sim.sim_info)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return list(cls._find_fire_state._tuned_values.job_and_role_changes.items())

    @classmethod
    def default_job(cls):
        return cls.fire_brigade_job

    def start_situation(self):
        super().start_situation()
        self._change_state(self._find_fire_state())

    @classmethod
    def get_predefined_guest_list(cls):
        active_sim_info = services.active_sim_info()
        fire_brigade_volunteers = services.sim_filter_service().submit_matching_filter(number_of_sims_to_find=(cls.number_of_volunteers), sim_filter=(cls.fire_brigade_job.filter),
          requesting_sim_info=active_sim_info,
          allow_yielding=False,
          blacklist_sim_ids={sim_info.sim_id for sim_info in services.active_household()},
          gsi_source_fn=(cls.get_sim_filter_gsi_name))
        if len(fire_brigade_volunteers) < cls.number_of_volunteers:
            return
        guest_list = SituationGuestList(invite_only=True, host_sim_id=(fire_brigade_volunteers[0].sim_info.sim_id),
          filter_requesting_sim_id=(active_sim_info.sim_id))
        for volunteer in fire_brigade_volunteers:
            guest_list.add_guest_info(SituationGuestInfo((volunteer.sim_info.sim_id), (cls.fire_brigade_job),
              (RequestSpawningOption.DONT_CARE),
              (BouncerRequestPriority.EVENT_VIP),
              expectation_preference=True))

        return guest_list

    def advance_to_post_fire(self):
        self._change_state(_FireOutState())