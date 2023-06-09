# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\npc_hosted\island_welcome_wagon.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 9000 bytes
import random
from sims4.tuning.tunable import TunableReference
from sims4.utils import classproperty
from situations.bouncer.bouncer_types import RequestSpawningOption, BouncerRequestPriority
from situations.npc_hosted.welcome_wagon import PreWelcomeWagon, WelcomeWagon
from situations.situation import Situation
from situations.situation_guest_list import SituationGuestList, SituationGuestInfo
import services, sims4.tuning.instances, situations.bouncer
logger = sims4.log.Logger('Island Welcome Wagon')

class IslandPreWelcomeWagon(PreWelcomeWagon):
    INSTANCE_TUNABLES = {'_lei_carrier_situation_job': TunableReference(description='\n            The job for the lei carrier.\n            ',
                                     manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)))}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classproperty
    def sets_welcome_wagon_flag(cls):
        return True

    @classmethod
    def get_predefined_guest_list(cls):
        active_sim_info = services.active_sim_info()
        door_knocker_results = services.sim_filter_service().submit_filter((cls._door_knocker_situation_job.filter), callback=None,
          requesting_sim_info=active_sim_info,
          allow_yielding=False,
          gsi_source_fn=(cls.get_sim_filter_gsi_name))
        if not door_knocker_results:
            return
        else:
            door_knocker = random.choice(door_knocker_results)
            guest_list = SituationGuestList(invite_only=True, host_sim_id=(door_knocker.sim_info.sim_id),
              filter_requesting_sim_id=(active_sim_info.sim_id))
            guest_list.add_guest_info(SituationGuestInfo((door_knocker.sim_info.sim_id), (cls._door_knocker_situation_job),
              (RequestSpawningOption.DONT_CARE),
              (BouncerRequestPriority.EVENT_VIP),
              expectation_preference=True))
            blacklist = set()
            blacklist.add(door_knocker.sim_info.sim_id)
            kava_carrier_results = services.sim_filter_service().submit_filter((cls._fruitcake_bearer_situation_job.filter), callback=None,
              requesting_sim_info=active_sim_info,
              allow_yielding=False,
              blacklist_sim_ids=blacklist,
              gsi_source_fn=(cls.get_sim_filter_gsi_name))
            if not kava_carrier_results:
                return
                kava_carrier = random.choice(kava_carrier_results)
                guest_list.add_guest_info(SituationGuestInfo((kava_carrier.sim_info.sim_id), (cls._fruitcake_bearer_situation_job),
                  (RequestSpawningOption.DONT_CARE),
                  (BouncerRequestPriority.EVENT_VIP),
                  expectation_preference=True))
                blacklist.add(kava_carrier.sim_info.sim_id)
                lei_carrier_results = services.sim_filter_service().submit_filter((cls._lei_carrier_situation_job.filter), callback=None,
                  requesting_sim_info=active_sim_info,
                  allow_yielding=False,
                  blacklist_sim_ids=blacklist,
                  gsi_source_fn=(cls.get_sim_filter_gsi_name))
                if not lei_carrier_results:
                    return
                lei_carrier = random.choice(lei_carrier_results)
                guest_list.add_guest_info(SituationGuestInfo((lei_carrier.sim_info.sim_id), (cls._lei_carrier_situation_job),
                  (RequestSpawningOption.DONT_CARE),
                  (BouncerRequestPriority.EVENT_VIP),
                  expectation_preference=True))
                blacklist.add(lei_carrier.sim_info.sim_id)
                other_neighbors_results = services.sim_filter_service().submit_filter((cls._other_neighbors_job.filter), callback=None,
                  requesting_sim_info=active_sim_info,
                  allow_yielding=False,
                  blacklist_sim_ids=blacklist,
                  gsi_source_fn=(cls.get_sim_filter_gsi_name))
                if not other_neighbors_results:
                    return guest_list
                if len(other_neighbors_results) > cls._number_of_neighbors:
                    neighbors = random.sample(other_neighbors_results, cls._number_of_neighbors)
            else:
                neighbors = other_neighbors_results
        for neighbor in neighbors:
            guest_list.add_guest_info(SituationGuestInfo((neighbor.sim_info.sim_id), (cls._other_neighbors_job),
              (RequestSpawningOption.DONT_CARE),
              (BouncerRequestPriority.EVENT_VIP),
              expectation_preference=True))

        return guest_list


sims4.tuning.instances.lock_instance_tunables(IslandPreWelcomeWagon, exclusivity=(situations.bouncer.bouncer_types.BouncerExclusivityCategory.NORMAL),
  creation_ui_option=(situations.situation_types.SituationCreationUIOption.NOT_AVAILABLE))

class IslandWelcomeWagon(WelcomeWagon):
    INSTANCE_TUNABLES = {'_lei_carrier_situation_job': TunableReference(description='\n            The job for the lei carrier.\n            ',
                                     manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)))}


sims4.tuning.instances.lock_instance_tunables(IslandWelcomeWagon, exclusivity=(situations.bouncer.bouncer_types.BouncerExclusivityCategory.NORMAL),
  creation_ui_option=(situations.situation_types.SituationCreationUIOption.NOT_AVAILABLE))