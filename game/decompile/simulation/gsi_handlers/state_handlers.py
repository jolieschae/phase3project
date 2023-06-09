# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\state_handlers.py
# Compiled at: 2021-02-03 20:14:29
# Size of source mod 2**32: 2895 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema
import gsi_handlers
state_trigger_schema = GsiGridSchema(label='State Triggers/State Trigger Log')
state_trigger_schema.add_field('objId', label='Object Id', unique_field=True, width=1.2)
state_trigger_schema.add_field('def', label='Definition', width=2)
state_trigger_schema.add_field('parent', label='Parent', width=1.5)
state_trigger_schema.add_field('state', label='Trigger State', width=1.5)
state_trigger_schema.add_field('state_value', label='Trigger State Value', width=2)
state_trigger_schema.add_field('at_state', label='Triggered At State', width=2.5)
state_trigger_schema.add_field('at_states', label='At States', width=2.5)
state_trigger_schema.add_field('src', label='Source', width=1.3)
state_trigger_archiver = GameplayArchiver('StateTriggerLog', state_trigger_schema)

def archive_state_trigger(obj, triggered_state, at_state, at_states, source=''):
    archive_data = {'objId':hex(obj.id), 
     'def':obj.definition.name, 
     'state':str(triggered_state.state), 
     'state_value':str(triggered_state), 
     'at_state':str(at_state), 
     'at_states':str(at_states), 
     'src':source}
    if obj.parent is not None:
        archive_data['parent'] = gsi_handlers.gsi_utils.format_object_name(obj.parent)
    state_trigger_archiver.archive(data=archive_data)


timed_state_trigger_schema = GsiGridSchema(label='State Triggers/Timed State Trigger Log')
timed_state_trigger_schema.add_field('objId', label='Object Id', unique_field=True)
timed_state_trigger_schema.add_field('def', label='Definition', width=2)
timed_state_trigger_schema.add_field('state', label='Trigger State', width=2)
timed_state_trigger_schema.add_field('state_value', label='Trigger State Value', width=2)
timed_state_trigger_schema.add_field('at_state', label='At State', width=2)
timed_state_trigger_schema.add_field('trigger_time', label='Trigger Time')
timed_state_trigger_archiver = GameplayArchiver('TimedStateTriggerLog', timed_state_trigger_schema)

def archive_timed_state_trigger(obj, triggered_state, at_state, trigger_time):
    archive_data = {'objId':hex(obj.id), 
     'def':obj.definition.name, 
     'state':str(triggered_state.state), 
     'state_value':str(triggered_state), 
     'at_state':str(at_state), 
     'trigger_time':round(trigger_time, 2)}
    timed_state_trigger_archiver.archive(data=archive_data)