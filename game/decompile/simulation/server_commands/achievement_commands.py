# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\achievement_commands.py
# Compiled at: 2015-05-05 20:43:29
# Size of source mod 2**32: 2575 bytes
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target, TunableInstanceParam
import services, sims4.commands

@sims4.commands.Command('achievements.reset_data')
def reset_achievements(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        account = services.account_service().get_account_by_id(sim.sim_info.account_id)
        account.achievement_tracker.reset_data()
        sims4.commands.output('Achievements reset complete', _connection)
    else:
        sims4.commands.output('Account not found, please check: |achievements.reset_data <sim id from desired account>', _connection)


@sims4.commands.Command('achievements.list_all_achievements')
def list_all_achievements(_connection=None):
    achievement_manager = services.get_instance_manager(sims4.resources.Types.ACHIEVEMENT)
    for achievement_id in achievement_manager.types:
        achievement = achievement_manager.get(achievement_id)
        sims4.commands.output('{}: {}'.format(achievement, int(achievement.guid64)), _connection)


@sims4.commands.Command('achievements.complete_achievement', command_type=(sims4.commands.CommandType.Automation))
def complete_achievement(achievement_type: TunableInstanceParam(sims4.resources.Types.ACHIEVEMENT), opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is not None:
        if achievement_type is not None:
            account = services.account_service().get_account_by_id(sim.sim_info.account_id)
            account.achievement_tracker.reset_milestone(achievement_type)
            account.achievement_tracker.complete_milestone(achievement_type, sim.sim_info)
            sims4.commands.output('Complete {} on {}'.format(achievement_type, sim), _connection)
            account.achievement_tracker.send_if_dirty()
        else:
            sims4.commands.output('Achievement {} not found, please check: |achievements.list_all_achievements'.format(achievement_type, sim), _connection)