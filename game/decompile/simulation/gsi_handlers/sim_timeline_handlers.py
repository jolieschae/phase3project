# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\sim_timeline_handlers.py
# Compiled at: 2015-01-27 20:11:36
# Size of source mod 2**32: 3687 bytes
import contextlib
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
import services
sim_timeline_archive_schema = GsiGridSchema(label='Sim Time Line', sim_specific=True)
sim_timeline_archive_schema.add_field('game_time', label='GameTime', width=40)
sim_timeline_archive_schema.add_field('module', label='Module', width=35)
sim_timeline_archive_schema.add_field('status', label='Status', width=40)
sim_timeline_archive_schema.add_field('message', label='Message', width=35)
sim_timeline_archive_schema.add_field('interaction_id', label='Interaction ID', hidden=True, type=(GsiFieldVisualizers.INT))
sim_timeline_archive_schema.add_field('interaction', label='Interaction', width=40)
sim_timeline_archive_schema.add_field('target', label='Target', width=40)
sim_timeline_archive_schema.add_field('initiator', label='Initiator', width=30)
sim_timeline_archive_schema.add_field('duration', label='Duration(Sim Game Time Minutes)', width=50)
archiver = GameplayArchiver('sim_time_line_archive', sim_timeline_archive_schema)

@contextlib.contextmanager
def archive_sim_timeline_context_manager(sim, module, log_message, interaction=None):
    if not archiver.enabled:
        yield
    else:
        services_time_service = services.time_service()
        if services_time_service is not None and services_time_service.sim_timeline is not None:
            start_time = services_time_service.sim_timeline.now
        else:
            start_time = None
        try:
            archive_sim_timeline(sim, module, 'Start', log_message, interaction=interaction)
            yield
        finally:
            duration = None
            if start_time is not None:
                services_time_service = services.time_service()
                if services_time_service is not None:
                    if services_time_service.sim_timeline is not None:
                        duration = services_time_service.sim_timeline.now - start_time
            archive_sim_timeline(sim, module, 'Completed', log_message, interaction=interaction, duration=duration)


def archive_sim_timeline(sim, module, status, message_data, interaction=None, duration=None):
    services_time_service = services.time_service()
    if services_time_service is not None and services_time_service.sim_timeline is not None:
        now = services_time_service.sim_timeline.now
    else:
        now = None
    archive_data = {'game_time':str(now), 
     'module':module, 
     'message':message_data, 
     'duration':'{} min ({})'.format(str(duration.in_minutes()), str(duration)) if duration is not None else 'None', 
     'status':status}
    if interaction is not None:
        archive_data.update({'interaction_id':interaction.id, 
         'interaction':str(interaction.affordance.__name__), 
         'target':str(interaction.target), 
         'initiator':str(interaction.sim)})
    archiver.archive(data=archive_data, object_id=(sim.id))