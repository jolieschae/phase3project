# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\civic_policies\street_civic_policy_commands.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 21484 bytes
import sims4
from civic_policies.base_civic_policy_provider import BaseCivicPolicyProvider
from civic_policies.base_civic_policy_utilities import CivicPolicyProviderListSelector, debug_automation_output_policy_name_list, debug_automation_output_vote_info
from civic_policies.street_civic_policy_provider import StreetProvider
from distributor.ops import CommunityBoardDialog
from distributor.system import Distributor
from event_testing.game_option_tests import TestableGameOptions
from event_testing.test_events import TestEvent
from google.protobuf import text_format
from protocolbuffers import UI_pb2
from server_commands.argument_helpers import OptionalSimInfoParam, get_optional_target, TunableInstanceParam, extract_ints, OptionalTargetParam
from sims4.common import Pack
import camera, services, world.street

@sims4.commands.Command('civic_policy.street.enact', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def street_civic_policy_enact(policy: TunableInstanceParam(sims4.resources.Types.SNIPPET), opt_target: OptionalSimInfoParam=None, _connection=None):
    street_service = services.street_service()
    if street_service is None:
        sims4.commands.automation_output('Pack not loaded', _connection)
        sims4.commands.cheat_output('Pack not loaded', _connection)
        return
    sim = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    world_id = sim.household.get_home_world_id()
    street = world.street.get_street_instance_from_world_id(world_id)
    if street_service.enact(street, policy):
        sims4.commands.automation_output('Status; Result:Success', _connection)
    else:
        sims4.commands.automation_output('Status; Result:Failed', _connection)
        sims4.commands.cheat_output('{} not enacted'.format(policy), _connection)


@sims4.commands.Command('civic_policy.street.repeal', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def street_civic_policy_repeal(policy: TunableInstanceParam(sims4.resources.Types.SNIPPET), opt_target: OptionalSimInfoParam=None, _connection=None):
    street_service = services.street_service()
    if street_service is None:
        sims4.commands.automation_output('Pack not loaded', _connection)
        sims4.commands.cheat_output('Pack not loaded', _connection)
        return
    sim = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    world_id = sim.household.get_home_world_id()
    street = world.street.get_street_instance_from_world_id(world_id)
    if street_service.repeal(street, policy):
        sims4.commands.automation_output('Status; Result:Success', _connection)
    else:
        sims4.commands.automation_output('Status; Result:Failed', _connection)
        sims4.commands.cheat_output('{} not repealed'.format(policy), _connection)


@sims4.commands.Command('civic_policy.street.vote', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def street_civic_policy_vote(policy: TunableInstanceParam(sims4.resources.Types.SNIPPET), opt_target: OptionalSimInfoParam=None, count: int=1, user_directed: bool=False, lobby_interaction: bool=False, _connection=None):
    street_service = services.street_service()
    if street_service is None:
        sims4.commands.automation_output('Pack not loaded', _connection)
        sims4.commands.cheat_output('Pack not loaded', _connection)
        return
    count = int(count)
    sim = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    world_id = sim.household.get_home_world_id()
    street = world.street.get_street_instance_from_world_id(world_id)
    if street_service.vote(street, policy, count, user_directed, lobby_interaction):
        sims4.commands.automation_output('Status; Result:Success', _connection)
    else:
        sims4.commands.cheat_output('Could not add vote to {}'.format(policy), _connection)
        sims4.commands.automation_output('Status; Result:Failed', _connection)


@sims4.commands.Command('civic_policy.street.begin_repeal', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def street_civic_policy_begin_repeal(policy: TunableInstanceParam(sims4.resources.Types.SNIPPET), opt_target: OptionalSimInfoParam=None, _connection=None):
    street_service = services.street_service()
    if street_service is None:
        sims4.commands.automation_output('Pack not loaded', _connection)
        sims4.commands.cheat_output('Pack not loaded', _connection)
        return
    sim = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    world_id = sim.household.get_home_world_id()
    street = world.street.get_street_instance_from_world_id(world_id)
    if not street_service.add_for_repeal(street, policy):
        sims4.commands.automation_output('{} not added to up for repeal policies'.format(policy), _connection)
        sims4.commands.cheat_output('{} not added to up for repeal policies'.format(policy), _connection)


@sims4.commands.Command('civic_policy.street.end_repeal', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def street_civic_policy_end_repeal(policy: TunableInstanceParam(sims4.resources.Types.SNIPPET), opt_target: OptionalSimInfoParam=None, _connection=None):
    street_service = services.street_service()
    if street_service is None:
        sims4.commands.automation_output('Pack not loaded', _connection)
        sims4.commands.cheat_output('Pack not loaded', _connection)
        return
    sim = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    world_id = sim.household.get_home_world_id()
    street = world.street.get_street_instance_from_world_id(world_id)
    if not street_service.remove_from_repeal(street, policy):
        sims4.commands.automation_output('{} not removed from up for repeal policies'.format(policy), _connection)
        sims4.commands.cheat_output('{} not removed from up for repeal policies'.format(policy), _connection)


@sims4.commands.Command('civic_policy.street.show_community_board', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def street_civic_policy_show_community_board(current_street: bool=True, opt_sim: OptionalSimInfoParam=None, opt_target_id: int=0, _connection=None):
    street_service = services.street_service()
    if street_service is None:
        sims4.commands.automation_output('StreetShowCommunityBoardInfo; Status:Failed, Message:Pack not loaded', _connection)
        sims4.commands.cheat_output('Pack not loaded', _connection)
        return False
    else:
        sim_info = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
        if current_street:
            street = services.current_zone().street
        else:
            world_id = sim_info.household.get_home_world_id()
            street = world.street.get_street_instance_from_world_id(world_id)
        provider = street_service.get_provider(street)
        if provider is not None:
            op = CommunityBoardDialog(provider, sim_info, opt_target_id)
            Distributor.instance().add_op_with_no_owner(op)
            sims4.commands.automation_output('StreetShowCommunityBoardInfo; Status:Success', _connection)
        else:
            sims4.commands.automation_output('StreetShowCommunityBoardInfo; Status:Failed, Message:Street has no provider', _connection)


@sims4.commands.Command('civic_policy.focus_camera_on_community_board', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def focus_camera_on_community_board(_connection=None):
    for board in services.object_manager().get_objects_with_tag_gen(BaseCivicPolicyProvider.COMMUNITY_BOARD_TAG):
        if not board.is_on_active_lot():
            camera.focus_on_position(board.position, services.client_manager().get(_connection))
            return
    else:
        sims4.commands.output('There are no offlot community boards in the object manager.', _connection)


@sims4.commands.Command('civic_policy.handle_community_board', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def handle_community_board(community_board_response: str, _connection=None):
    proto = UI_pb2.CommunityBoardResponse()
    text_format.Merge(community_board_response, proto)
    sim_info = services.sim_info_manager().get(proto.sim_id)
    if sim_info is None:
        return
    if proto.provider_type == StreetProvider.provider_type_id:
        street_civic_policy_service = services.street_service()
        if street_civic_policy_service is None:
            sims4.commands.automation_output('Pack not loaded', _connection)
            sims4.commands.cheat_output('Pack not loaded', _connection)
            return
        world_id = sim_info.household.get_home_world_id()
        street = world.street.get_street_instance_from_world_id(world_id)
        provider = street_civic_policy_service.get_provider(street)
    else:
        source_venue = services.venue_service().source_venue
        if source_venue is None:
            return
        provider = source_venue.civic_policy_provider
    if provider is not None:
        for policy in proto.balloted_policies:
            policy_instance = provider.get_policy_instance_for_tuning(policy.policy_id)
            if policy_instance is None:
                continue
            provider.add_to_ballot(policy_instance)
            provider.vote_by_instance(policy_instance, (policy.count), user_directed=True)

        provider.modify_influence(sim_info, -proto.influence_points)
        provider.handle_vote_interaction(sim_info, proto.target_id, bool(proto.balloted_policies))


@sims4.commands.Command('civic_policy.street.request_add_picker', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def street_civic_policy_request_add_picker(opt_target: OptionalSimInfoParam=None, added_policies_string: str='', _connection=None):
    street_service = services.street_service()
    if street_service is None:
        sims4.commands.automation_output('Pack not loaded', _connection)
        sims4.commands.cheat_output('Pack not loaded', _connection)
        return False
    else:
        sim_info = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
        return sim_info is None or sim_info.is_selected or None
    world_id = sim_info.household.get_home_world_id()
    street = world.street.get_street_instance_from_world_id(world_id)
    provider = street_service.get_provider(street)
    if provider is not None:
        used_policy_ids = extract_ints(added_policies_string)
        provider.create_add_policy_picker(sim_info, set(used_policy_ids))


@sims4.commands.Command('civic_policy.street.force_end_voting', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Automation))
def street_civic_policy_force_end_voting(all_streets: bool=False, opt_target: OptionalSimInfoParam=None, _connection=None):
    street_civic_policy_service = services.street_service()
    if street_civic_policy_service is None:
        sims4.commands.automation_output('Pack not loaded', _connection)
        sims4.commands.cheat_output('Pack not loaded', _connection)
        return
    if all_streets:
        sims4.commands.cheat_output('Updating all streets', _connection)
        street_civic_policy_service.force_end_voting(street=None)
        return
    sim = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    world_id = sim.household.get_home_world_id()
    street = world.street.get_street_instance_from_world_id(world_id)
    provider = street_civic_policy_service.get_provider(street)
    if provider is None:
        sims4.commands.automation_output('Street has no provider', _connection)
        sims4.commands.cheat_output('Street has no provider', _connection)
        return

    def output_enacted_policy_list():
        policies = provider.get_enacted_policies()
        for policy in policies:
            sims4.commands.cheat_output('    {}'.format(policy), _connection)

    sims4.commands.cheat_output('Before Enacted Policies', _connection)
    output_enacted_policy_list()
    if not street_civic_policy_service.force_end_voting(street):
        sims4.commands.cheat_output('Could not force end of voting', _connection)
    sims4.commands.cheat_output('After Enacted Policies', _connection)
    output_enacted_policy_list()


@sims4.commands.Command('civic_policy.open_voting', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Automation))
def street_civic_policy_force_open_voting(open_voting: bool=True, _connection=None):
    street_civic_policy_service = services.street_service()
    if street_civic_policy_service is None:
        sims4.commands.automation_output('Status; Result : Pack not loaded', _connection)
        sims4.commands.cheat_output('Pack not loaded', _connection)
        return
    street_civic_policy_service._force_voting_open = open_voting
    if open_voting:
        msg = 'Voting open, vote counts reset to 0'
        sims4.commands.automation_output('Status; Result : Success', _connection)
        sims4.commands.cheat_output('Voting open, vote counts reset to 0', _connection)
        street_civic_policy_service._open_voting()


@sims4.commands.Command('civic_policy.force_daily_vote', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Automation))
def street_civic_policy_force_daily_vote(_connection=None):
    street_civic_policy_service = services.street_service()
    if street_civic_policy_service is None:
        sims4.commands.automation_output('Status; Result : Pack not loaded', _connection)
        sims4.commands.cheat_output('Pack not loaded', _connection)
        return
    services.get_event_manager().process_event(TestEvent.CivicPolicyDailyRandomVoting)
    sims4.commands.automation_output('Status; Result : Success', _connection)


@sims4.commands.Command('civic_policy.add_influence', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Automation))
def street_civic_policy_add_influence(count: int=1, opt_target: OptionalSimInfoParam=None, _connection=None):
    street_civic_policy_service = services.street_service()
    if street_civic_policy_service is None:
        sims4.commands.automation_output('Pack not loaded', _connection)
        sims4.commands.automation_output('SimAddInfluenceInfo; Status:Failed, Message:Pack not loaded', _connection)
        sims4.commands.cheat_output('Pack not loaded', _connection)
        return
    sim = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    world_id = sim.household.get_home_world_id()
    street = world.street.get_street_instance_from_world_id(world_id)
    provider = street_civic_policy_service.get_provider(street)
    if provider is None:
        sims4.commands.automation_output('SimAddInfluenceInfo; Status:Failed, Message:Street has no provider', _connection)
        sims4.commands.cheat_output('Street has no provider', _connection)
        return
    provider.modify_influence(sim.sim_info, count)
    sims4.commands.automation_output('SimAddInfluenceInfo; Status:Success', _connection)


@sims4.commands.Command('civic_policy.set_npc_voting_enabled', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def set_npc_voting_enabled(enabled: bool=False, _connection=None):
    street_civic_policy_service = services.street_service()
    if street_civic_policy_service is None:
        sims4.commands.automation_output('Pack not loaded', _connection)
        sims4.commands.cheat_output('Pack not loaded', _connection)
        return
    street_civic_policy_service.enable_automatic_voting = enabled
    services.get_event_manager().process_event((TestEvent.TestedGameOptionChanged), custom_keys=(
     TestableGameOptions.CIVIC_POLICY_NPC_VOTING_ENABLED,))


@sims4.commands.Command('civic_policy.street.policy_list', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Automation))
def civic_policy_list(selector: CivicPolicyProviderListSelector=None, _connection=None):
    street_civic_policy_service = services.street_service()
    if street_civic_policy_service is None:
        sims4.commands.cheat_output('Pack not loaded', _connection)
        street_civic_policy_provider = None
    else:
        street = services.current_zone().street
        street_civic_policy_provider = street_civic_policy_service.get_provider(street)
    debug_automation_output_policy_name_list(street_civic_policy_provider, selector, _connection)


@sims4.commands.Command('civic_policy.street.vote_count', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Automation))
def street_civic_policy_vote_count(policy: TunableInstanceParam(sims4.resources.Types.SNIPPET), _connection=None):
    street_civic_policy_provider = None
    street_civic_policy_service = services.street_service()
    if street_civic_policy_service is None:
        sims4.commands.cheat_output('Pack not loaded', _connection)
    else:
        street = services.current_zone().street
        street_civic_policy_provider = street_civic_policy_service.get_provider(street)
        if not street_civic_policy_provider:
            sims4.commands.cheat_output('Street has no civic policies', _connection)
    debug_automation_output_vote_info(street_civic_policy_provider, policy, _connection)


@sims4.commands.Command('civic_policy.street.policy_add_to_ballot', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Automation))
def street_add_policy_to_ballot(policy: TunableInstanceParam(sims4.resources.Types.SNIPPET), opt_target: OptionalSimInfoParam=None, _connection=None):
    street_civic_policy_service = services.street_service()
    if street_civic_policy_service is None:
        sims4.commands.automation_output('StreetAddPolicyToBallotInfo; Status:Failed, Message:Pack not loaded', _connection)
        return
    street = services.current_zone().street
    provider = street_civic_policy_service.get_provider(street)
    sim = get_optional_target(opt_target, _connection, target_type=OptionalSimInfoParam)
    if not provider.is_new_policy_allowed(sim):
        sims4.commands.automation_output('StreetAddPolicyToBallotInfo; Status:Failed, Message:No new policy allowed, Ballot is full', _connection)
        return
    if policy in provider.get_balloted_policies():
        sims4.commands.automation_output('StreetAddPolicyToBallotInfo; Status:Failed, Message:Policy {0} exist in Ballot board'.format(policy), _connection)
        return
    provider.add_to_ballot(policy)
    sims4.commands.automation_output('StreetAddPolicyToBallotInfo; Status:Success', _connection)