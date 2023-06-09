# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\soak_commands.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 6608 bytes
import alarms, clock, services, sims4.tuning.tunable, situations
with sims4.reload.protected(globals()):
    _soak_alarm_handles = set()

class SoakCommandsTuning:
    SOAK_PARTY_SITUATION = sims4.tuning.tunable.TunableReference(description='\n        A party that stress the soak system.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.SITUATION)))
    SOAK_PARTY_COOLDOWN = sims4.tuning.tunable.TunableSimMinute(description='\n        Time in sim minutes between the start of one soak party situation and the next.\n        ',
      default=1380)
    SOAK_MAID_SERVICE_NPC = sims4.tuning.tunable.TunableReference(description='\n        The maid service NPC that creates the maid situation to clean your house.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.SERVICE_NPC)))
    SOAK_MAID_COOLDOWN = sims4.tuning.tunable.TunableSimMinute(description='\n        Time in sim minutes between the start of one soak maid situation and the next.\n        ',
      default=1140)
    SOAK_HANDYMAN_SERVICE_NPC = sims4.tuning.tunable.TunableReference(description='\n        The handyman/repairman service NPC that creates the handyman situation\n        to repair items in your house.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.SERVICE_NPC)))
    SOAK_HANDYMAN_COOLDOWN = sims4.tuning.tunable.TunableSimMinute(description='\n        Time in sim minutes between the start of one soak handman situation and the next.\n        ',
      default=1020)


def _request_service_npc(service_type):
    household = services.active_household()
    if household is None:
        return
    service_npc_manager = services.current_zone().service_npc_service
    if service_npc_manager is None:
        return
    service_npc_manager.request_service(household, service_type, from_load=True)


@sims4.commands.Command('soak.enable_soak_party_situation', command_type=(sims4.commands.CommandType.Automation))
def enable_soak_party_situation(_connection=None):
    alarm_handle = alarms.add_alarm(enable_soak_party_situation, (clock.interval_in_sim_minutes(SoakCommandsTuning.SOAK_PARTY_COOLDOWN)),
      _create_soak_party_situation,
      repeating=True)
    _soak_alarm_handles.add(alarm_handle)
    output = sims4.commands.CheatOutput(_connection)
    output('soak party enabled.')


@sims4.commands.Command('soak.create_soak_party_situation', command_type=(sims4.commands.CommandType.Automation))
def create_soak_party_situation(_connection=None):
    _create_soak_party_situation(None)


def _create_soak_party_situation(_):
    situation_manager = services.get_zone_situation_manager()
    guest_list = situations.situation_guest_list.SituationGuestList(invite_only=False)
    situation_id = situation_manager.create_situation((SoakCommandsTuning.SOAK_PARTY_SITUATION), guest_list=guest_list, user_facing=False)
    return situation_id


@sims4.commands.Command('soak.enable_soak_maid_situation', command_type=(sims4.commands.CommandType.Automation))
def enable_soak_maid_situation(_connection=None):
    alarm_handle = alarms.add_alarm(enable_soak_maid_situation, (clock.interval_in_sim_minutes(SoakCommandsTuning.SOAK_MAID_COOLDOWN)),
      _create_soak_maid_situation,
      repeating=True)
    _soak_alarm_handles.add(alarm_handle)
    output = sims4.commands.CheatOutput(_connection)
    output('soak maid enabled.')


@sims4.commands.Command('soak.create_soak_maid_situation', command_type=(sims4.commands.CommandType.Automation))
def create_soak_maid_situation(_connection=None):
    _create_soak_maid_situation(None)


def _create_soak_maid_situation(_):
    _request_service_npc(SoakCommandsTuning.SOAK_MAID_SERVICE_NPC)


@sims4.commands.Command('soak.enable_soak_handyman_situation', command_type=(sims4.commands.CommandType.Automation))
def enable_soak_handyman_situation(_connection=None):
    alarm_handle = alarms.add_alarm(enable_soak_handyman_situation, (clock.interval_in_sim_minutes(SoakCommandsTuning.SOAK_HANDYMAN_COOLDOWN)),
      _create_soak_handyman_situation,
      repeating=True)
    _soak_alarm_handles.add(alarm_handle)
    output = sims4.commands.CheatOutput(_connection)
    output('soak handyman enabled.')


@sims4.commands.Command('soak.create_soak_handyman_situation', command_type=(sims4.commands.CommandType.Automation))
def create_soak_handyman_situation(_connection=None):
    _create_soak_handyman_situation(None)


def _create_soak_handyman_situation(_):
    _request_service_npc(SoakCommandsTuning.SOAK_HANDYMAN_SERVICE_NPC)


@sims4.commands.Command('soak.super_size', command_type=(sims4.commands.CommandType.Automation))
def soak_super_size(_connection=None):
    enable_soak_handyman_situation(_connection=_connection)
    enable_soak_maid_situation(_connection=_connection)
    enable_soak_party_situation(_connection=_connection)


@sims4.commands.Command('soak.cancel_super_size', command_type=(sims4.commands.CommandType.Automation))
def soak_cancel_super_size(_connection=None):
    for alarm_handle in tuple(_soak_alarm_handles):
        alarms.cancel_alarm(alarm_handle)

    _soak_alarm_handles.clear()