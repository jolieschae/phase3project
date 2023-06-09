# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: /Users/sims4builder/build/Beta/_deploy/Client/MacRelease/The Sims 4.app/Contents/Python/Generated/protocolbuffers/Memories_pb2.py
# Compiled at: 2023-04-20 22:46:30
# Size of source mod 2**32: 3894 bytes
from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
DESCRIPTOR = descriptor.FileDescriptor(name='Memories.proto',
  package='EA.Sims4.Network',
  serialized_pb='\n\x0eMemories.proto\x12\x10EA.Sims4.Network"^\n\x0cMemoriesList\x12\r\n\x05simId\x18\x01 \x01(\x04\x12\x13\n\x0bhouseholdId\x18\x02 \x01(\x04\x12\x13\n\x0bisFavorites\x18\x03 \x01(\x08\x12\x15\n\tmemoryIds\x18\x04 \x03(\x04B\x02\x10\x01"C\n\x12MemoriesFilterFile\x12-\n\x05lists\x18\x01 \x03(\x0b2\x1e.EA.Sims4.Network.MemoriesList')
_MEMORIESLIST = descriptor.Descriptor(name='MemoriesList',
  full_name='EA.Sims4.Network.MemoriesList',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='simId',
   full_name='EA.Sims4.Network.MemoriesList.simId',
   index=0,
   number=1,
   type=4,
   cpp_type=4,
   label=1,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='householdId',
   full_name='EA.Sims4.Network.MemoriesList.householdId',
   index=1,
   number=2,
   type=4,
   cpp_type=4,
   label=1,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='isFavorites',
   full_name='EA.Sims4.Network.MemoriesList.isFavorites',
   index=2,
   number=3,
   type=8,
   cpp_type=7,
   label=1,
   has_default_value=False,
   default_value=False,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='memoryIds',
   full_name='EA.Sims4.Network.MemoriesList.memoryIds',
   index=3,
   number=4,
   type=4,
   cpp_type=4,
   label=3,
   has_default_value=False,
   default_value=[],
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=(descriptor._ParseOptions(descriptor_pb2.FieldOptions(), '\x10\x01')))],
  extensions=[],
  nested_types=[],
  enum_types=[],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=36,
  serialized_end=130)
_MEMORIESFILTERFILE = descriptor.Descriptor(name='MemoriesFilterFile',
  full_name='EA.Sims4.Network.MemoriesFilterFile',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='lists',
   full_name='EA.Sims4.Network.MemoriesFilterFile.lists',
   index=0,
   number=1,
   type=11,
   cpp_type=10,
   label=3,
   has_default_value=False,
   default_value=[],
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None)],
  extensions=[],
  nested_types=[],
  enum_types=[],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=132,
  serialized_end=199)
_MEMORIESFILTERFILE.fields_by_name['lists'].message_type = _MEMORIESLIST
DESCRIPTOR.message_types_by_name['MemoriesList'] = _MEMORIESLIST
DESCRIPTOR.message_types_by_name['MemoriesFilterFile'] = _MEMORIESFILTERFILE

class MemoriesList(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _MEMORIESLIST


class MemoriesFilterFile(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _MEMORIESFILTERFILE