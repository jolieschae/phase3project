# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\fire_commands.py
# Compiled at: 2019-05-06 20:13:51
# Size of source mod 2**32: 2510 bytes
from server_commands.argument_helpers import get_optional_target, OptionalTargetParam, RequiredTargetParam
from sims4.commands import CommandType
import services, sims4.commands

@sims4.commands.Command('fire.kill')
def kill(_connection=None):
    fire_service = services.get_fire_service()
    fire_service.kill()


@sims4.commands.Command('fire.toggle_enabled', command_type=(CommandType.Cheat))
def toggle_fire_enabled(enabled: bool=None, _connection=None):
    if enabled is None:
        services.fire_service.fire_enabled = not services.fire_service.fire_enabled
    else:
        services.fire_service.fire_enabled = enabled
    sims4.commands.output('Fire enabled = {}'.format(services.fire_service.fire_enabled), _connection)


@sims4.commands.Command('fire.alert_all_sims')
def alert_all_sims(_connection=None):
    fire_service = services.get_fire_service()
    fire_service.alert_all_sims()


@sims4.commands.Command('fire.singe_sim')
def singe_sim(opt_target: OptionalTargetParam=None, set_singed: bool=None, _connection=None):
    sim = get_optional_target(opt_target, _connection)
    if sim is None:
        return False
    else:
        sim_info = sim.sim_info
        if set_singed is None:
            sim_info.singed = not sim_info.singed
        else:
            sim_info.singed = set_singed


@sims4.commands.Command('fire.spawn_at_object')
def spawn_fire_at_object(target: RequiredTargetParam, num_fires: int=1, _connection=None):
    target_object = target.get_target()
    if target_object is None:
        sims4.commands.output(f"Invalid target object id {target_object}")
        return
    fire_service = services.get_fire_service()
    fire_service.spawn_fire_at_object(target_object, num_fires=num_fires)