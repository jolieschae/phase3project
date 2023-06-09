# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\zone_modifier\zone_modifier_commands.py
# Compiled at: 2019-10-22 18:13:39
# Size of source mod 2**32: 5680 bytes
from server_commands.argument_helpers import TunableInstanceParam, get_tunable_instance
import services, sims4.commands
ZONE_MODIFIER_CAP = 3

@sims4.commands.Command('zone_modifier.add_zone_modifier', command_type=(sims4.commands.CommandType.DebugOnly))
def add_zone_modifier(zone_modifier: TunableInstanceParam(sims4.resources.Types.ZONE_MODIFIER), target_zone_id: int=None, _connection=None):
    if target_zone_id is None:
        target_zone_id = services.current_zone_id()
    persistence_service = services.get_persistence_service()
    zone_data = persistence_service.get_zone_proto_buff(services.current_zone_id())
    if zone_data is None:
        return
    if len(zone_data.lot_traits) == ZONE_MODIFIER_CAP:
        sims4.commands.output('There are already {} lot traits on the lot.  Remove one first.'.format(ZONE_MODIFIER_CAP), _connection)
        return
    zone_modifier_id = zone_modifier.guid64
    if zone_modifier_id in zone_data.lot_traits:
        sims4.commands.output('{} is already a trait on the lot.'.format(zone_modifier), _connection)
        return
    zone_data.lot_traits.append(zone_modifier_id)
    services.get_zone_modifier_service().check_for_and_apply_new_zone_modifiers(target_zone_id)


@sims4.commands.Command('zone_modifier.remove_zone_modifier', command_type=(sims4.commands.CommandType.DebugOnly))
def remove_zone_modifier(zone_modifier: TunableInstanceParam(sims4.resources.Types.ZONE_MODIFIER), target_zone_id: int=None, _connection=None):
    if target_zone_id is None:
        target_zone_id = services.current_zone_id()
    persistence_service = services.get_persistence_service()
    zone_data = persistence_service.get_zone_proto_buff(services.current_zone_id())
    if zone_data is None:
        return
    zone_modifier_id = zone_modifier.guid64
    if zone_modifier_id not in zone_data.lot_traits:
        sims4.commands.output('{} is not a trait on the lot.'.format(zone_modifier), _connection)
        return
    zone_data.lot_traits.remove(zone_modifier_id)
    services.get_zone_modifier_service().check_for_and_apply_new_zone_modifiers(target_zone_id)


@sims4.commands.Command('zone_modifier.remove_all_zone_modifiers', command_type=(sims4.commands.CommandType.DebugOnly))
def remove_all_zone_modifiers(target_zone_id: int=None, _connection=None):
    if target_zone_id is None:
        target_zone_id = services.current_zone_id()
    persistence_service = services.get_persistence_service()
    zone_data = persistence_service.get_zone_proto_buff(services.current_zone_id())
    if zone_data is None:
        return
    traits_to_remove = list(zone_data.lot_traits)
    for trait in traits_to_remove:
        zone_data.lot_traits.remove(trait)

    services.get_zone_modifier_service().check_for_and_apply_new_zone_modifiers(target_zone_id)


def run_zone_modifier_entry(zone_modifier, schedule_entry_index, _connection):
    persistence_service = services.get_persistence_service()
    zone_data = persistence_service.get_zone_proto_buff(services.current_zone_id())
    if zone_data is None:
        return
    zone_modifier_id = zone_modifier.guid64
    if zone_modifier_id not in zone_data.lot_traits:
        sims4.commands.output('{} is not a trait on the lot.'.format(zone_modifier), _connection)
        return
    index = int(schedule_entry_index)
    schedule_entries = zone_modifier.schedule.schedule_entries
    if index < 0 or index >= len(schedule_entries):
        sims4.commands.output('{} is an invalid schedule entry index.'.format(index), _connection)
        return
    zone_modifier_service = services.get_zone_modifier_service()
    zone_modifier_service.run_zone_modifier_schedule_entry(schedule_entries[index])


@sims4.commands.Command('zone_modifier.run_schedule_entry', command_type=(sims4.commands.CommandType.DebugOnly))
def run_schedule_entry(zone_modifier: TunableInstanceParam(sims4.resources.Types.ZONE_MODIFIER), schedule_entry_index, _connection=None):
    run_zone_modifier_entry(zone_modifier, schedule_entry_index, _connection)


@sims4.commands.Command('volcanic_eruption', command_type=(sims4.commands.CommandType.Live))
def volcanic_eruption(eruption_size, _connection=None):
    size_to_schedule_entry_dict = {'large':'0', 
     'small':'1'}
    zone_modifier = get_tunable_instance(sims4.resources.Types.ZONE_MODIFIER, 'zoneModifier_lotTrait_VolcanicActivity')
    if zone_modifier is None:
        return
    schedule_entry_index = size_to_schedule_entry_dict.get(eruption_size.lower())
    if schedule_entry_index is None:
        return
    run_zone_modifier_entry(zone_modifier, schedule_entry_index, _connection)