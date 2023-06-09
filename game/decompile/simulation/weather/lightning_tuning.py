# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\weather\lightning_tuning.py
# Compiled at: 2018-03-05 17:39:24
# Size of source mod 2**32: 6366 bytes
from broadcasters.broadcaster_request import BroadcasterRequest
from sims4.tuning.tunable import TunableTuple, TunableRange, TunableReference, TunableList, TunablePercent, TunablePackSafeReference, TunableRealSecond
from tag import TunableTags
from vfx import PlayEffect
import services, sims4.resources

class LightningTuning:
    ACTIVE_LIGHTNING = TunableTuple(description='\n        Active Lightning Tuning\n        ',
      weights=TunableTuple(description='\n            Weights for striking various objects.\n            ',
      weight_terrain=TunableRange(description='\n                Weighted chance of striking terrain versus other locations.\n                ',
      tunable_type=float,
      default=1.0,
      minimum=0.0),
      weight_object=TunableRange(description='\n                Weighted chance of striking non-Sim objects versus other locations.\n                ',
      tunable_type=float,
      default=1.0,
      minimum=0.0),
      weight_sim=TunableRange(description='\n                Weighted chance of striking Sims versus other locations.\n                ',
      tunable_type=float,
      default=1.0,
      minimum=0.0)))
    STRIKE_TERRAIN_TUNING = TunableTuple(description='\n        Tuning for when we want a lightning bolt to strike the ground.\n        ',
      effect_off_lot=PlayEffect.TunableFactory(description='\n            The effect we want to spawn at the terrain location if it is off\n            lot.\n            '),
      effect_on_lot=PlayEffect.TunableFactory(description="\n            The effect we want to spawn at the object's location if it is on\n            lot. This will also have a scorch mark associated with it.\n            "),
      scorch_mark_delay=TunableRealSecond(description='\n            The delay, in real seconds, before we place a scorch mark for on-\n            lot lightning strikes.\n            ',
      default=0),
      create_object_tuning=TunableTuple(description='\n            Tuning related to creating objects when lightning strikes the\n            ground.\n            ',
      chance=TunablePercent(description='\n                Chance to spawn one of the objects tuned here when lightning\n                strikes the terrain.\n                ',
      default=10),
      definition_weights=TunableList(description='\n                List of definitions and their weighted chance of being created\n                at the location of the lightning strike.\n                ',
      tunable=TunableTuple(description='\n                    The object definition and weighted chance of it being\n                    created.\n                    ',
      weight=TunableRange(description='\n                        The weighted chance of creating this object.\n                        ',
      tunable_type=float,
      default=1.0,
      minimum=0.0),
      definition=TunableReference(description='\n                        The object we want to create at the strike location.\n                        ',
      manager=(services.definition_manager()))))),
      broadcaster=BroadcasterRequest.TunableFactory(description='\n            The broadcaster we want to fire when a lightning bolt strikes the\n            terrain.\n            '))
    STRIKE_OBJECT_TUNING = TunableTuple(description="\n        Tuning for when we want a lightning bolt to strike an object.\n        \n        For an object to be considered for a lightning strike, it must have one\n        of the tags tuned here. We will increase its chance based on lightning\n        multiplier tuning on it's Weather Aware Component if it has one, and\n        apply both the generic loot tuned here, as well as any loot that is\n        registered for Struck By Lightning.\n        ",
      effect=PlayEffect.TunableFactory(description="\n            The effect we want to spawn at the object's location.\n            "),
      scorch_mark_delay=TunableRealSecond(description='\n            The delay, in real seconds, before we place a scorch mark for on-\n            lot lightning strikes.\n            ',
      default=0),
      generic_loot_on_strike=TunableList(description='\n            Loot to apply to all objects when struck by lightning.\n            \n            Objects that have a weather aware component can tune loot when\n            listening for Struck By Lightning.\n            ',
      tunable=TunableReference(description='\n                A loot action to apply to the object struck by lightning.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.ACTION)))),
      tags=TunableTags(description='\n            A set of tags that determine if an object can be struck by\n            lightning. Each object has a weight of 1 to be struck by lightning,\n            but can be multiplied in the weather aware component to give\n            preference to electronics, etc.\n            '),
      broadcaster=BroadcasterRequest.TunableFactory(description='\n            The broadcaster we want to fire when a lightning bolt strikes an\n            object.\n            '))
    STRIKE_SIM_TUNING = TunableTuple(description='\n        Tuning for when we want a lightning bolt to strike a Sim.\n        ',
      affordance=TunablePackSafeReference(description='\n            The interaction to push on a Sim that is struck by lightning.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))))