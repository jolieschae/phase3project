# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\reset_handlers.py
# Compiled at: 2015-01-27 20:38:06
# Size of source mod 2**32: 3641 bytes
import sys, traceback
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
reset_log_schema = GsiGridSchema(label='Reset Service Log')
reset_log_schema.add_field('action', label='Action', type=(GsiFieldVisualizers.STRING))
reset_log_schema.add_field('target_object', label='Target', type=(GsiFieldVisualizers.STRING))
reset_log_schema.add_field('reset_reason', label='ResetReason', type=(GsiFieldVisualizers.STRING), width=1)
reset_log_schema.add_field('source_object', label='Source', type=(GsiFieldVisualizers.STRING))
reset_log_schema.add_field('cause', label='Cause', type=(GsiFieldVisualizers.STRING))
with reset_log_schema.add_has_many('Callstack', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('callstack', label='Callstack')
reset_log_archiver = GameplayArchiver('reset_log', reset_log_schema, enable_archive_by_default=True,
  max_records=500,
  add_to_archive_enable_functions=True)

def archive_reset_log_record(action, record, include_callstack=False):
    entry = {'action':action, 
     'target_object':str(record.obj), 
     'reset_reason':str(record.reset_reason), 
     'source_object':str(record.source), 
     'cause':str(record.cause)}
    if include_callstack:
        frame = sys._getframe(1)
        tb = traceback.format_stack(frame)
        lines = []
        for line in tb:
            index = line.find('Scripts')
            if index < 0:
                index = 0
            lines.append({'callstack': line[index:-1]})

        entry['Callstack'] = lines
    else:
        entry['Callstack'] = [
         {'callstack': ''}]
    reset_log_archiver.archive(data=entry)


def archive_reset_log_message(message):
    entry = {
     'action': 'message', 
     'target_object': "'*****'", 
     'reset_reason': "'*****'", 
     'source_object': "'*****'", 
     'cause': "'*****'"}
    entry['Callstack'] = [
     {'callstack': ''}]
    reset_log_archiver.archive(data=entry)


def archive_reset_log_entry(action, target, reason, source=None, cause=None, include_callstack=False):
    entry = {'action':action, 
     'target_object':str(target), 
     'reset_reason':str(reason), 
     'source_object':str(source), 
     'cause':cause}
    if include_callstack:
        frame = sys._getframe(1)
        tb = traceback.format_stack(frame)
        lines = []
        for line in tb:
            index = line.find('Scripts')
            if index < 0:
                index = 0
            lines.append({'callstack': line[index:-1]})

        entry['Callstack'] = lines
    else:
        entry['Callstack'] = [
         {'callstack': ''}]
    reset_log_archiver.archive(data=entry)