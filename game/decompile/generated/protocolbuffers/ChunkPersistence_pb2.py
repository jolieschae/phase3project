# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: /Users/sims4builder/build/Beta/_deploy/Client/MacRelease/The Sims 4.app/Contents/Python/Generated/protocolbuffers/ChunkPersistence_pb2.py
# Compiled at: 2023-04-20 22:46:30
# Size of source mod 2**32: 3237 bytes
from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
DESCRIPTOR = descriptor.FileDescriptor(name='ChunkPersistence.proto',
  package='EA.Sims4.Network',
  serialized_pb='\n\x16ChunkPersistence.proto\x12\x10EA.Sims4.Network":\n\x15ChunkPersistenceEntry\x12\x0f\n\x07dataCRC\x18\x01 \x01(\r\x12\x10\n\x08fileName\x18\x02 \x01(\t"P\n\x14ChunkPersistenceFile\x128\n\x07entries\x18\x01 \x03(\x0b2\'.EA.Sims4.Network.ChunkPersistenceEntry')
_CHUNKPERSISTENCEENTRY = descriptor.Descriptor(name='ChunkPersistenceEntry',
  full_name='EA.Sims4.Network.ChunkPersistenceEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='dataCRC',
   full_name='EA.Sims4.Network.ChunkPersistenceEntry.dataCRC',
   index=0,
   number=1,
   type=13,
   cpp_type=3,
   label=1,
   has_default_value=False,
   default_value=0,
   message_type=None,
   enum_type=None,
   containing_type=None,
   is_extension=False,
   extension_scope=None,
   options=None),
 descriptor.FieldDescriptor(name='fileName',
   full_name='EA.Sims4.Network.ChunkPersistenceEntry.fileName',
   index=1,
   number=2,
   type=9,
   cpp_type=9,
   label=1,
   has_default_value=False,
   default_value=((b'').decode('utf-8')),
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
  serialized_start=44,
  serialized_end=102)
_CHUNKPERSISTENCEFILE = descriptor.Descriptor(name='ChunkPersistenceFile',
  full_name='EA.Sims4.Network.ChunkPersistenceFile',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
 descriptor.FieldDescriptor(name='entries',
   full_name='EA.Sims4.Network.ChunkPersistenceFile.entries',
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
  serialized_start=104,
  serialized_end=184)
_CHUNKPERSISTENCEFILE.fields_by_name['entries'].message_type = _CHUNKPERSISTENCEENTRY
DESCRIPTOR.message_types_by_name['ChunkPersistenceEntry'] = _CHUNKPERSISTENCEENTRY
DESCRIPTOR.message_types_by_name['ChunkPersistenceFile'] = _CHUNKPERSISTENCEFILE

class ChunkPersistenceEntry(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _CHUNKPERSISTENCEENTRY


class ChunkPersistenceFile(message.Message, metaclass=reflection.GeneratedProtocolMessageType):
    DESCRIPTOR = _CHUNKPERSISTENCEFILE