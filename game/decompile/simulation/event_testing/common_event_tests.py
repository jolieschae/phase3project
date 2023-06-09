# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\common_event_tests.py
# Compiled at: 2020-08-07 16:38:45
# Size of source mod 2**32: 9515 bytes
import enum
from aspirations.aspiration_tests import SelectedAspirationTest, SelectedAspirationTrackTest
from clubs.club_tests import ClubTest
from crafting.photography_tests import TookPhotoTest
from drama_scheduler.drama_node_tests import FestivalRunningTest
from event_testing.statistic_tests import StatThresholdTest, RankedStatThresholdTest
from event_testing.test_variants import AtWorkTest, BucksPerkTest, CareerPromotedTest, TunableCareerTest, CollectedItemTest, TunableCollectionThresholdTest, EventRanSuccessfullyTest, HouseholdSizeTest, PurchasePerkTest, TunableSimoleonsTest, TunableSituationRunningTest, TunableUnlockedTest
from event_testing.tests_with_data import GenerationTest, OffspringCreatedTest, TunableParticipantRanAwayActionTest, TunableParticipantRanInteractionTest, TunableSimoleonsEarnedTest, WhimCompletedTest
from interactions import ParticipantType, ParticipantTypeSim, ParticipantTypeActorTargetSim, ParticipantTypeSingleSim
from objects.object_tests import CraftedItemTest, InventoryTest, ObjectCriteriaTest, ObjectPurchasedTest
from relationships.relationship_tests import TunableRelationshipTest, RelationshipBitTest
from seasons.season_tests import SeasonTest
from sims.household_utilities.utility_tests import UtilityTest
from sims.sim_info_tests import BuffAddedTest, BuffTest, MoodTest, TraitTest
from sims.unlock_tracker_tests import UnlockTrackerAmountTest
from sims4.tuning.tunable import TunableVariant
from statistics.skill_tests import SkillTagThresholdTest
from world.world_tests import LocationTest
from zone_tests import ZoneTest

class ParticipantTypeActorHousehold(enum.IntFlags):
    Actor = ParticipantType.Actor
    ActiveHousehold = ParticipantType.ActiveHousehold


class ParticipantTypeTargetAllRelationships(enum.IntFlags):
    TargetSim = ParticipantType.TargetSim
    AllRelationships = ParticipantType.AllRelationships


class CommonEventTestVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, at_work=AtWorkTest.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
 'tooltip':None}), 
         bucks_perk_unlocked=BucksPerkTest.TunableFactory(description='\n                A test for which kind of bucks perk is being unlocked\n                ',
  locked_args={'tooltip': None}), 
         buff_added=BuffAddedTest.TunableFactory(locked_args={'tooltip': None}), 
         career_promoted=CareerPromotedTest.TunableFactory(locked_args={'tooltip': None}), 
         career_test=TunableCareerTest.TunableFactory(locked_args={'subjects':ParticipantType.Actor, 
 'tooltip':None}), 
         club_tests=ClubTest.TunableFactory(locked_args={'tooltip':None, 
 'club':ClubTest.CLUB_FROM_EVENT_DATA, 
 'room_for_new_members':None, 
 'subject_passes_membership_criteria':None, 
 'subject_can_join_more_clubs':None}), 
         collected_item_test=CollectedItemTest.TunableFactory(locked_args={'tooltip': None}), 
         collection_test=TunableCollectionThresholdTest(locked_args={'who':ParticipantType.Actor, 
 'tooltip':None}), 
         crafted_item=CraftedItemTest.TunableFactory(locked_args={'tooltip': None}), 
         event_ran_successfully=EventRanSuccessfullyTest.TunableFactory(description='\n                This is a simple test that always returns true whenever one of\n                the tuned test events is processed.\n                ',
  locked_args={'tooltip': None}), 
         festival_running=FestivalRunningTest.TunableFactory(description='\n                This is a test that triggers when the festival begins.\n                ',
  locked_args={'tooltip': None}), 
         generation_created=GenerationTest.TunableFactory(locked_args={'tooltip': None}), 
         has_buff=BuffTest.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
 'tooltip':None}), 
         household_size=HouseholdSizeTest.TunableFactory(locked_args={'participant':ParticipantType.Actor, 
 'tooltip':None}), 
         inventory=InventoryTest.TunableFactory(locked_args={'tooltip': None}), 
         location_test=LocationTest.TunableFactory(location_tests={
 'is_outside': False, 
 'is_natural_ground': False, 
 'is_in_slot': False, 
 'is_on_active_lot': False, 
 'is_on_level': False}), 
         mood_test=MoodTest.TunableFactory(locked_args={'who':ParticipantTypeSim.Actor, 
 'tooltip':None}), 
         object_criteria=ObjectCriteriaTest.TunableFactory(locked_args={'tooltip': None}), 
         object_purchase_test=ObjectPurchasedTest.TunableFactory(locked_args={'tooltip': None}), 
         offspring_created_test=OffspringCreatedTest.TunableFactory(locked_args={'tooltip': None}), 
         purchase_perk_test=PurchasePerkTest.TunableFactory(description='\n                A test for which kind of perk is being purchased.\n                '), 
         photo_taken=TookPhotoTest.TunableFactory(description='\n                A test for player taken photos.\n                '), 
         ran_away_action_test=TunableParticipantRanAwayActionTest(locked_args={'participant':ParticipantTypeActorTargetSim.Actor, 
 'tooltip':None}), 
         ran_interaction_test=TunableParticipantRanInteractionTest(locked_args={'participant':ParticipantType.Actor, 
 'tooltip':None}), 
         relationship=TunableRelationshipTest(participant_type_override=(
 ParticipantTypeTargetAllRelationships,
 ParticipantTypeTargetAllRelationships.AllRelationships),
  locked_args={'tooltip': None}), 
         relationship_bit=RelationshipBitTest.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
 'target':ParticipantType.TargetSim, 
 'tooltip':None}), 
         season_test=SeasonTest.TunableFactory(locked_args={'tooltip': None}), 
         selected_aspiration_test=SelectedAspirationTest.TunableFactory(locked_args={'who':ParticipantTypeSingleSim.Actor, 
 'tooltip':None}), 
         selected_aspiration_track_test=SelectedAspirationTrackTest.TunableFactory(locked_args={'who':ParticipantTypeSingleSim.Actor, 
 'tooltip':None}), 
         simoleons_earned=TunableSimoleonsEarnedTest(locked_args={'tooltip': None}), 
         simoleon_value=TunableSimoleonsTest(locked_args={'tooltip': None}), 
         situation_running_test=TunableSituationRunningTest(locked_args={'tooltip': None}), 
         skill_tag=SkillTagThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor, 
 'tooltip':None}), 
         statistic=StatThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor, 
 'tooltip':None}), 
         ranked_statistic=RankedStatThresholdTest.TunableFactory(locked_args={'who':ParticipantType.Actor, 
 'tooltip':None}), 
         trait=TraitTest.TunableFactory(participant_type_override=(
 ParticipantTypeActorHousehold,
 ParticipantTypeActorHousehold.Actor),
  locked_args={'tooltip': None}), 
         unlock_earned=TunableUnlockedTest(locked_args={'participant':ParticipantType.Actor, 
 'tooltip':None}), 
         unlock_tracker_amount=UnlockTrackerAmountTest.TunableFactory(locked_args={'subject':ParticipantType.Actor, 
 'tooltip':None}), 
         utility=UtilityTest.TunableFactory(), 
         whim_completed_test=WhimCompletedTest.TunableFactory(locked_args={'tooltip': None}), 
         zone=ZoneTest.TunableFactory(locked_args={'tooltip': None}), 
         default='ran_interaction_test', **kwargs)