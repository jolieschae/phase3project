# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\cache_commands.py
# Compiled at: 2017-03-30 16:48:15
# Size of source mod 2**32: 2518 bytes
import itertools
from animation.asm import get_boundary_condition_cache_debug_information
from interactions.constraints import RequiredSlot
from interactions.interaction_instance_manager import get_animation_constraint_cache_debug_information
from sims4.commands import CommandType
import caches, sims4.commands, sims4.log
logger = sims4.log.Logger('CacheCommand')

@sims4.commands.Command('caches.enable_all_caches', command_type=(sims4.commands.CommandType.Automation))
def enable_all_caches(enable: bool=True, _connection=None):
    caches.skip_cache = not enable
    caches.clear_all_caches(force=True)
    output = sims4.commands.CheatOutput(_connection)
    output('Caches are now on.'.format(enable) if enable is True else 'Caches are off.')


@sims4.commands.Command('caches.enable_constraints_cache')
def enable_constraints_cache(enable: bool=True, _connection=None):
    caches.use_constraints_cache = True


@sims4.commands.Command('caches.disable_constraints_cache')
def disable_constraints_cache(enable: bool=True, _connection=None):
    caches.use_constraints_cache = False


@sims4.commands.Command('caches.status', command_type=(CommandType.Cheat))
def cache_status(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output('Boundary Condition Cache Live   : {}'.format(caches.USE_ACC_AND_BCC))
    output('Animation Constraint Cache Live : {}'.format(caches.USE_ACC_AND_BCC))
    for token, value, description in itertools.chain(get_animation_constraint_cache_debug_information(), get_boundary_condition_cache_debug_information()):
        output('{:31} : {:<5} ({:45})'.format(token, value, description))


@sims4.commands.Command('caches.clear_required_slot_cache')
def cache_clear_required_slot_cache(_connection=None):
    RequiredSlot.clear_required_slot_cache()