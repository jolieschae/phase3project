# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\sim_filter_service_handlers.py
# Compiled at: 2022-03-10 20:35:09
# Size of source mod 2**32: 6643 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
import services, sims4.log
logger = sims4.log.Logger('SimFilterServiceGSIHandlers', default_owner='skorman')

class SimFilterServiceGSILoggingData:

    def __init__(self, request_type, sim_filter_type, yielding, gsi_source_fn):
        self.request_type = request_type
        self.sim_filter_type = sim_filter_type
        self.yielding = yielding
        if gsi_source_fn is None:
            logger.warn('{} filter request for {} did not specify a gsi_source_fn. Please make sure the filter request is provided with this argument.', request_type, sim_filter_type)
        self.gsi_source_fn = gsi_source_fn
        self.rejected_sim_infos = []
        self.created_sim_infos = []
        self.metadata = []

    def add_created_household(self, household, was_successful=True):
        for sim_info in household:
            self.created_sim_infos.append({'sim_info':str(sim_info),  'was successful':str(was_successful)})

    def add_rejected_sim_info(self, sim_info, reason, filter_term):
        self.rejected_sim_infos.append({'sim_info':str(sim_info),  'reason':reason, 
         'filter_term':str(filter_term)})

    def add_metadata(self, num_sims, allow_instanced_sims, club, blacklist_sims, optional, required_story_progression_arc):
        if len(blacklist_sims):
            blacklist_sims = str(blacklist_sims)
        else:
            blacklist_sims = None
        if required_story_progression_arc is not None:
            required_story_progression_rules = str(required_story_progression_arc.required_rules)
        else:
            required_story_progression_rules = None
        self.metadata = [num_sims, allow_instanced_sims, str(club), blacklist_sims, optional, required_story_progression_rules]


sim_filter_service_archive_schema = GsiGridSchema(label='Sim Filter Service Archive')
sim_filter_service_archive_schema.add_field('game_time', label='Game Time', type=(GsiFieldVisualizers.TIME))
sim_filter_service_archive_schema.add_field('source', label='Source', width=3)
sim_filter_service_archive_schema.add_field('request_type', label='Request Type')
sim_filter_service_archive_schema.add_field('yielding', label='Yielding')
sim_filter_service_archive_schema.add_field('matching_results', label='Num Matching', type=(GsiFieldVisualizers.INT))
sim_filter_service_archive_schema.add_field('created_sims', label='Num Created', type=(GsiFieldVisualizers.INT))
sim_filter_service_archive_schema.add_field('filter_type', label='Filter Type', width=2.5)
with sim_filter_service_archive_schema.add_has_many('FilterResult', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('sim_info', label='Sim Info', width=1)
    sub_schema.add_field('score', label='Score', type=(GsiFieldVisualizers.FLOAT), width=0.5)
    sub_schema.add_field('filter_tag', label='Tag', type=(GsiFieldVisualizers.STRING), width=0.5)
with sim_filter_service_archive_schema.add_has_many('Created', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('sim_info', label='Sim Info', width=3)
    sub_schema.add_field('was successful', label='Was Successful', width=3)
with sim_filter_service_archive_schema.add_has_many('Rejected', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('sim_info', label='Sim Info', width=1)
    sub_schema.add_field('reason', label='Reason', width=1)
    sub_schema.add_field('filter_term', label='Filter Fail', width=2)
with sim_filter_service_archive_schema.add_has_many('Metadata', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('club', label='Club', width=1)
    sub_schema.add_field('blacklist_sim_ids', label='Blacklist Sim Ids', width=1)
    sub_schema.add_field('optional', label='Optional', width=1)
    sub_schema.add_field('num_sims_seeking', label='Number of Sims Seeking', type=(GsiFieldVisualizers.INT), width=1)
    sub_schema.add_field('allow_instanced_sims', label='Allow Instanced Sims', width=1)
    sub_schema.add_field('required_story_progression_rules', label='Required Story Progression Rules', width=1)
archiver = GameplayArchiver('sim_filter_service_archive', sim_filter_service_archive_schema)

def archive_filter_request(filter_results, gsi_logging_data):
    entry = {}
    entry['game_time'] = str(services.time_service().sim_now)
    entry['request_type'] = str(gsi_logging_data.request_type)
    entry['yielding'] = str(gsi_logging_data.yielding)
    entry['filter_type'] = str(gsi_logging_data.sim_filter_type)
    entry['matching_results'] = len(filter_results)
    entry['created_sims'] = len(gsi_logging_data.created_sim_infos)
    if gsi_logging_data.gsi_source_fn is not None:
        entry['source'] = gsi_logging_data.gsi_source_fn()
    else:
        entry['source'] = 'Not Specified'
    filter_results_list = []
    for filter_result in filter_results:
        filter_results_list.append({'sim_info':str(filter_result.sim_info),  'score':filter_result.score, 
         'reason':filter_result.reason, 
         'filter_tag':str(filter_result.tag)})

    entry['FilterResult'] = filter_results_list
    entry['Created'] = list(gsi_logging_data.created_sim_infos)
    entry['Rejected'] = list(gsi_logging_data.rejected_sim_infos)
    entry['Metadata'] = [
     {'num_sims_seeking':gsi_logging_data.metadata[0],  'allow_instanced_sims':gsi_logging_data.metadata[1], 
      'club':gsi_logging_data.metadata[2], 
      'blacklist_sim_ids':gsi_logging_data.metadata[3], 
      'optional':gsi_logging_data.metadata[4], 
      'required_story_progression_rules':gsi_logging_data.metadata[5]}]
    archiver.archive(data=entry)