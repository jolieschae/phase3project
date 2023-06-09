# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\temple\temple_tuning.py
# Compiled at: 2018-05-10 18:23:42
# Size of source mod 2**32: 5035 bytes
from interactions import ParticipantType
from interactions.utils.loot import LootActions
from interactions.utils.loot_ops import LockDoor, UnlockDoor
from sims4.tuning.tunable import TunableMapping, TunableTuple, TunableHouseDescription, TunablePackSafeReference, TunablePackSafeLotDescription, TunableSet
from situations.situation_complex import TunableInteractionOfInterest
from tag import TunableTag
from temple.temple_room_data import TunableTempleRoomData
import services, sims4.resources

class TempleTuning:
    TEMPLES = TunableMapping(description='\n        A Mapping of Temple Templates (house descriptions) and the data\n        associated with each temple.\n        ',
      key_name='Template House Description',
      key_type=TunableHouseDescription(pack_safe=True),
      value_name='Temple Data',
      value_type=TunableTuple(description='\n            The data associated with the mapped temple template.\n            ',
      rooms=TunableMapping(description='\n                A mapping of room number to the room data. Room number 0 will be\n                the entrance room to the temple, room 1 will be the first room\n                that needs to be unlocked, and so on.\n                ',
      key_name='Room Number',
      key_type=int,
      value_name='Room Data',
      value_type=TunableTempleRoomData(pack_safe=True)),
      enter_lot_loot=TunableSet(description='\n                Loot applied to Sims when they enter or spawn in to this Temple.\n                \n                NOTE: Exit Lot Loot is not guaranteed to be given. For example,\n                if the Sim walks onto the lot, player switches to a different\n                zone, then summons that Sim, that Sim will bypass getting the\n                exit loot.\n                ',
      tunable=LootActions.TunableReference(pack_safe=True)),
      exit_lot_loot=TunableSet(description='\n                Loot applied to Sims when they exit or spawn out of this Temple.\n                \n                NOTE: This loot is not guaranteed to be given after Enter Lot\n                Loot. For example, if the Sim walks onto the lot, player\n                switches to a different zone, then summons that Sim, that Sim\n                will bypass getting the exit loot.\n                ',
      tunable=LootActions.TunableReference(pack_safe=True))))
    GATE_TAG = TunableTag(description='\n        The tag used to find the gate objects inside Temples.\n        ',
      filter_prefixes=('func_temple', ))
    TRAP_TAG = TunableTag(description='\n        The tag used to identify traps inside temples. This will be used to find\n        placeholder traps as well.\n        ',
      filter_prefixes=('func_temple', ))
    CHEST_TAG = TunableTag(description="\n        The tag used to identify the final chest of a temple. If it's in the\n        open state, the temple will be considered solved.\n        ",
      filter_prefixes=('func_temple', ))
    CHEST_OPEN_STATE = TunablePackSafeReference(description='\n        The state that indicates the chest is open.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions='ObjectStateValue')
    GATE_STATE = TunablePackSafeReference(description='\n        The state for temple gates. Used for easy look up.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions='ObjectState')
    GATE_UNLOCK_STATE = TunablePackSafeReference(description='\n        The unlock state for temple gates.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions='ObjectStateValue')
    TEMPLE_LOT_DESCRIPTION = TunablePackSafeLotDescription(description='\n        A reference to the lot description file for the temple lot. This is used\n        for easier zone ID lookups.\n        ')
    GATE_LOCK_LOOT = LockDoor.TunableFactory(description='\n        The LockDoor loot to run on the gates in the temple on load when they\n        should be locked.\n        ')
    GATE_UNLOCK_LOOT = UnlockDoor.TunableFactory(description='\n        The UnlockDoor loot to run on the gates when they should be unlocked.\n        ')
    CHEST_OPEN_INTEARCTION = TunableInteractionOfInterest(description='\n        A reference to the open interaction for chests. This interaction will be\n        listened for to determine temple completion.\n        ')