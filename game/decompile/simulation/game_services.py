# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\game_services.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 8479 bytes
from protocolbuffers.Consts_pb2 import MGR_CLIENT, MGR_HOUSEHOLD, MGR_SIM_INFO
import sims4.reload, sims4.service_manager
with sims4.reload.protected(globals()):
    service_manager = None

class GameServiceManager(sims4.service_manager.ServiceManager):

    def __init__(self):
        super().__init__()
        self.allow_shutdown = True
        self.client_object_managers = set()

    @property
    def is_traveling(self):
        return not self.allow_shutdown

    def on_all_households_and_sim_infos_loaded(self, client):
        global service_manager
        if service_manager.allow_shutdown:
            super().on_all_households_and_sim_infos_loaded(client)

    def load_all_services(self, zone_data=None):
        if service_manager.allow_shutdown:
            super().load_all_services(zone_data=zone_data)

    def save_all_services(self, persistence_service, **kwargs):
        if service_manager.allow_shutdown:
            (super().save_all_services)(persistence_service, **kwargs)


def start_services(save_slot_data):
    global service_manager
    if service_manager is None:
        service_manager = GameServiceManager()
        from apartments.landlord_service import LandlordService
        from business.business_service import BusinessService
        from call_to_action.call_to_action_service import CallToActionService
        from clock import GameClock
        from clubs.club_service import ClubService
        from event_testing.event_manager_service import EventManagerService
        from objects.animals.animal_service import AnimalService
        from server.clientmanager import ClientManager
        from server.config_service import ConfigService
        from services.cheat_service import CheatService
        from services.roommate_service import RoommateService
        from services.style_service import StyleService
        from sims.household_utilities.utilities_manager import UtilitiesManager
        from sims.household_manager import HouseholdManager
        from sims.aging.aging_service import AgingService
        from services.relgraph_service import RelgraphService
        from sims.sim_info_manager import SimInfoManager
        from time_service import TimeService
        from tutorials.tutorial_service import TutorialService
        from curfew.curfew_service import CurfewService
        from sickness.sickness_service import SicknessService
        from trends.trend_service import TrendService
        from relationships.relationship_service import RelationshipService
        from sims.hidden_sim_service import HiddenSimService
        from holidays.holiday_service import HolidayService
        from seasons.season_service import SeasonService
        from weather.weather_service import WeatherService
        from services.rabbit_hole_service import RabbitHoleService
        from lot_decoration.lot_decoration_service import LotDecorationService
        from narrative.narrative_service import NarrativeService
        from organizations.organization_service import OrganizationService
        from services.object_lost_and_found_service import ObjectLostAndFoundService
        from civic_policies.street_civic_policy_service import StreetService
        from venues.venue_service import VenueGameService
        from global_policies.global_policy_service import GlobalPolicyService
        from world.region_service import RegionService
        from statistics.lifestyle_service import LifestyleService
        from sims.culling.culling_service import CullingService
        from live_events.live_event_service import LiveEventService
        from services.zone_reservation_service import ZoneReservationService
        from interactions.picker.purchase_picker_service import PurchasePickerService
        from fashion_trends.fashion_trend_service import FashionTrendService
        from global_flags.global_flag_service import GlobalFlagService
        from gameplay_options.misc_options_service import MiscOptionsService
        from lunar_cycle.lunar_cycle_service import LunarCycleService
        from clans.clan_service import ClanService
        from social_media.social_media_service import SocialMediaService
        from services.prom_service import PromService
        from high_school_graduation.graduation_service import GraduationService
        service_list = [
         GlobalFlagService(),
         ZoneReservationService(),
         LifestyleService(),
         BusinessService(),
         CallToActionService(),
         GameClock(),
         TimeService(),
         ConfigService(),
         CheatService(),
         EventManagerService(),
         ClientManager(manager_id=MGR_CLIENT),
         UtilitiesManager(),
         HouseholdManager(manager_id=MGR_HOUSEHOLD),
         RelationshipService(),
         RelgraphService.get_relgraph_service(),
         AgingService(),
         SimInfoManager(manager_id=MGR_SIM_INFO),
         CurfewService(),
         SicknessService(),
         HiddenSimService(),
         HolidayService(),
         SeasonService(),
         WeatherService(),
         NarrativeService(),
         GlobalPolicyService(),
         ClubService(),
         RabbitHoleService(),
         LotDecorationService(),
         StyleService(),
         TutorialService(),
         TrendService(),
         ObjectLostAndFoundService(),
         AnimalService(),
         LandlordService(),
         RoommateService(),
         OrganizationService(),
         StreetService(),
         VenueGameService(),
         RegionService(),
         CullingService(),
         LiveEventService(),
         PurchasePickerService(),
         MiscOptionsService(),
         LunarCycleService(),
         ClanService(),
         SocialMediaService(),
         PromService(),
         GraduationService(),
         FashionTrendService()]
        for service in service_list:
            if service is not None:
                service_manager.register_service(service)

        service_manager.start_services(container=service_manager, save_slot_data=save_slot_data)


def stop_services():
    global service_manager
    if service_manager.allow_shutdown:
        service_manager.stop_services()
        service_manager = None


def disable_shutdown():
    if service_manager is not None:
        service_manager.allow_shutdown = False


def enable_shutdown():
    if service_manager is not None:
        service_manager.allow_shutdown = True


def on_tick():
    pass