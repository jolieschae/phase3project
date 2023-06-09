# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\culling\culling_commands.py
# Compiled at: 2017-08-22 16:25:30
# Size of source mod 2**32: 2004 bytes
from server_commands.argument_helpers import OptionalHouseholdParam, get_optional_target
from sims.sim_info_lod import SimInfoLODLevel
from sims4.commands import Output
import services, sims4.commands

@sims4.commands.Command('culling.cull_household')
def cull_household(household_id: OptionalHouseholdParam, _connection=None):
    culling_service = services.get_culling_service()
    if culling_service is None:
        return
    household = get_optional_target(household_id, target_type=OptionalHouseholdParam, _connection=_connection)
    if household is None:
        return False
    culling_service.cull_household(household, is_important_fn=(lambda _: False))
    return True


@sims4.commands.Command('culling.set_max_player_population', command_type=(sims4.commands.CommandType.Live))
def set_max_player_population(max_player_population: int=0, _connection=None):
    culling_service = services.get_culling_service()
    culling_service.set_max_player_population(max_player_population)
    return True


@sims4.commands.Command('culling.print_scores')
def print_culling_scores(_connection=None):
    sim_info_manager = services.sim_info_manager()
    if sim_info_manager is None:
        return False
    culling_service = services.get_culling_service()
    if culling_service is None:
        return False
    output = Output(_connection)
    sim_infos = sim_info_manager.get_sim_infos_with_lod(SimInfoLODLevel.BASE)
    for sim_info in sim_infos:
        culling_service.get_culling_score_for_sim_info(sim_info, output=output)

    return True