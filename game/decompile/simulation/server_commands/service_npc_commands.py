# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\service_npc_commands.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 3461 bytes
from date_and_time import create_time_span
from sims4.commands import CommandType
import services, sims4.commands

@sims4.commands.Command('service_npc.request_service', command_type=(CommandType.Cheat))
def request_service(service_npc_type: str, household_id=None, _connection=None):
    service_npc_tuning = services.get_instance_manager(sims4.resources.Types.SERVICE_NPC).get(service_npc_type)
    if service_npc_tuning is not None:
        tgt_client = services.client_manager().get(_connection)
        if tgt_client is None:
            return False
        if household_id is None:
            household = tgt_client.household
        else:
            household_id = int(household_id)
            manager = services.household_manager()
            household = manager.get(household_id)
            if household is None:
                household = tgt_client.household
        services.current_zone().service_npc_service.request_service(household, service_npc_tuning)
        sims4.commands.output('Requesting service {0}'.format(service_npc_type), _connection)
        return True
    return False


@sims4.commands.Command('service_npc.fake_perform_service')
def fake_perform_service(service_npc_type: str, _connection=None):
    service_npc_tuning = services.get_instance_manager(sims4.resources.Types.SERVICE_NPC).get(service_npc_type)
    if service_npc_tuning is not None:
        tgt_client = services.client_manager().get(_connection)
        if tgt_client is None:
            return False
        household = tgt_client.household
        service_npc_tuning.fake_perform(household)
        return True
    return False


@sims4.commands.Command('service_npc.cancel_service', command_type=(CommandType.Automation))
def cancel_service(service_npc_type: str, max_duration: int=240, _connection=None):
    service_npc_tuning = services.get_instance_manager(sims4.resources.Types.SERVICE_NPC).get(service_npc_type)
    if service_npc_tuning is not None:
        tgt_client = services.client_manager().get(_connection)
        if tgt_client is None:
            return False
        household = tgt_client.household
        services.current_zone().service_npc_service.cancel_service(household, service_npc_tuning)
        return True
    return False


@sims4.commands.Command('service_npc.toggle_auto_scheduled_services', command_type=(CommandType.Automation))
def toggle_auto_scheduled_services(enable: bool=None, max_duration: int=240, _connection=None):
    service_npc_service = services.current_zone().service_npc_service
    enable_auto_scheduled_services = enable if enable is not None else not service_npc_service._auto_scheduled_services_enabled
    service_npc_service._auto_scheduled_services_enabled = enable_auto_scheduled_services
    return True