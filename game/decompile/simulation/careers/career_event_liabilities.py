# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\career_event_liabilities.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 11154 bytes
import itertools
from interactions import ParticipantType
from interactions.liability import Liability
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableReference, HasTunableSingletonFactory, TunableVariant, OptionalTunable, TunableTuple, TunableMapping, TunableEnumEntry
import services, sims4.resources
from situations.situation_guest_list import SituationGuestList, SituationGuestInfo
from situations.bouncer.bouncer_types import BouncerRequestPriority, RequestSpawningOption
logger = sims4.log.Logger('CareerEventLiability', default_owner='tingyul')

class CareerEventTravelType(HasTunableSingletonFactory, AutoFactoryInit):

    def apply(self, career, resolver):
        raise NotImplementedError


class CareerEventTravelStartTopEvent(CareerEventTravelType):

    def apply(self, career, resolver):
        career.career_event_manager.start_top_career_event()


class _CareerEventTravelSubEvent(CareerEventTravelType):

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, value):
        start_situation = value.start_situation
        if start_situation is not None:
            valid_job_types = start_situation.situation.get_tuned_jobs()
            for situation_job_type in start_situation.job_assignments.values():
                if situation_job_type not in valid_job_types:
                    logger.error('{} is an assigned job in {} but {} does not have that job', situation_job_type, instance_class, start_situation.situation)

    FACTORY_TUNABLES = {'start_situation':OptionalTunable(description='\n            If enabled, then a specific situation is to be started once the\n            travel request has finished. Participants of the requesting\n            interaction can fulfill specific jobs within that situation.\n            \n            Unsupported for multisim active careers.\n            Use the scored situation in the event.\n            ',
       tunable=TunableTuple(description='\n                The situation data necessary to create a situation once the\n                travel request has ended.\n                ',
       situation=TunableReference(description='\n                    The situation to start.  \n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION))),
       job_assignments=TunableMapping(description='\n                    The assignments for participants in this interaction.\n                    ',
       key_type=TunableEnumEntry(description='\n                        The participant that is to take on the specified job.\n                        ',
       tunable_type=ParticipantType,
       default=(ParticipantType.Actor)),
       value_type=TunableReference(description='\n                        The situation job that is to be assigned to the\n                        specified participant.\n                        ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)))))), 
     'verify_tunable_callback':_verify_tunable_callback}

    def apply(self, career, additional_careers, resolver):
        start_situation = self.start_situation
        if start_situation is not None:
            if career.is_multi_sim_active:
                logger.error('start_situation unsupported for multisim career event travel liability')
                return

                def start_situation_fn(zone_id):
                    guest_list = SituationGuestList(invite_only=True)
                    for participant_type, situation_job_type in start_situation.job_assignments.items():
                        for participant in resolver.get_participants(participant_type):
                            guest_list.add_guest_info(SituationGuestInfo(participant.sim_id, situation_job_type, RequestSpawningOption.DONT_CARE, BouncerRequestPriority.EVENT_VIP))

                    situation_manager = services.get_zone_situation_manager()
                    return situation_manager.create_situation((start_situation.situation), guest_list=guest_list,
                      zone_id=zone_id,
                      spawn_sims_during_zone_spin_up=True,
                      user_facing=False,
                      travel_request_kwargs={'is_career_event': True})

            else:
                start_situation_fn = None
            if additional_careers:
                additional_sims = {additional_career.sim_info.id for additional_career in additional_careers}
                career.career_event_manager.start_top_career_event(start_situation_fn=start_situation_fn, additional_sims=additional_sims)
                for additional_career in additional_careers:
                    additional_career.career_event_manager.start_top_career_event(is_additional_sim=True)

        else:
            career.career_event_manager.start_top_career_event(start_situation_fn=start_situation_fn)

    def _get_additional_sim_careers(self, career):
        careers = []
        if career.is_multi_sim_active:
            career_sim_info = career.sim_info
            for sim_info in career_sim_info.household.sim_info_gen():
                if sim_info is career_sim_info:
                    continue
                if sim_info.career_tracker is None:
                    continue
                if not sim_info.is_instanced():
                    continue
                additional_career = sim_info.career_tracker.careers.get(career.guid64)
                if additional_career is not None and career.career_event_manager.is_same_current_event(additional_career):
                    careers.append(additional_career)

        return careers


class CareerEventTravelRequestSubEvent(_CareerEventTravelSubEvent):
    FACTORY_TUNABLES = {'career_event': TunableReference(description='\n            Career sub event to travel to and start upon arriving.\n            ',
                       manager=(services.get_instance_manager(sims4.resources.Types.CAREER_EVENT)))}

    def apply(self, career, resolver):
        careers = self._get_additional_sim_careers(career)
        for career_iter in itertools.chain((career,), careers):
            career_iter.career_event_manager.request_career_event(self.career_event)

        return super().apply(career, careers, resolver)


class CareerEventTravelUnrequestSubEvent(_CareerEventTravelSubEvent):

    def apply(self, career, resolver):
        careers = self._get_additional_sim_careers(career)
        for career_iter in itertools.chain((career,), careers):
            career_iter.career_event_manager.unrequest_career_event()

        return super().apply(career, careers, resolver)


class CareerEventTravelCrimeScene(_CareerEventTravelSubEvent):

    def apply(self, career, resolver):
        if not hasattr(career, 'get_crime_scene_career_event'):
            logger.error('Trying to use crime scene travel type without a career that has crime scenes')
            return
        career_event = career.get_crime_scene_career_event()
        career.career_event_manager.request_career_event(career_event)
        return super().apply(career, None, resolver)


class CareerEventTravelLiability(Liability, HasTunableFactory, AutoFactoryInit):
    LIABILITY_TOKEN = 'CareerEventTravelLiability'
    FACTORY_TUNABLES = {'travel_type': TunableVariant(description='\n            Which type of career event travel to do.\n            ',
                      start_work=(CareerEventTravelStartTopEvent.TunableFactory()),
                      start_sub_event=(CareerEventTravelRequestSubEvent.TunableFactory()),
                      end_sub_event=(CareerEventTravelUnrequestSubEvent.TunableFactory()),
                      crime_scene=(CareerEventTravelCrimeScene.TunableFactory()),
                      default='start_sub_event')}

    def __init__(self, interaction, **kwargs):
        (super().__init__)(**kwargs)
        self._interaction = interaction

    def should_transfer(self, continuation):
        return False

    def release(self):
        return self._interaction is None or self._interaction.allow_outcomes or None
        career = self._interaction.sim.sim_info.career_tracker.career_currently_within_hours
        if career is None:
            logger.error("Sim {} is currently not at work -- can't start career event travel liability", self._interaction.sim)
            return
        if career.career_event_manager is None:
            logger.error("Sim {} is currently not part of a career event -- can't start career event travel liability", self._interaction.sim)
            return
        self.travel_type.apply(career, self._interaction.get_resolver())