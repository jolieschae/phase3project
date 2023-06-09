# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relics\relic_tuning.py
# Compiled at: 2017-12-19 18:01:46
# Size of source mod 2**32: 10813 bytes
from sims4.localization import TunableLocalizedString
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.tunable import TunableTuple, TunableReference, TunableMapping, TunableEnumEntry, OptionalTunable, TunableSet
import services, sims4.resources
logger = sims4.log.Logger('Relic Tuning', default_owner='trevor')

class RelicComboId(DynamicEnum):
    INVALID = 0


class RelicTuning:
    RELIC_DISCOVERY_DATA = TunableMapping(description='\n        A mapping of Relic Combo IDs and the data associated with that relic\n        combination.\n        ',
      key_name='relic_combo_id',
      key_type=TunableEnumEntry(description='\n            The Relic Combination ID to use as a reference to this\n            combination.\n            ',
      tunable_type=RelicComboId,
      default=(RelicComboId.INVALID),
      invalid_enums=(
     RelicComboId.INVALID,)),
      value_name='relic_combo_data',
      value_type=TunableTuple(description='\n            The data about a set of fused objects.\n            ',
      object_a=TunableSet(description='\n                A set of objects that count towards this relic combination.\n                For examples, since all of the crystals do the same thing,\n                they can all be in one set instead of creating a new entry\n                for each crystal/relic combo.\n                ',
      tunable=TunableReference(description='\n                    A reference to the first part of the relic.\n                    ',
      manager=(services.definition_manager()),
      pack_safe=True)),
      object_b=TunableSet(description='\n                A set of objects that count towards this relic combination.\n                For examples, since all of the crystals do the same thing,\n                they can all be in one set instead of creating a new entry\n                for each crystal/relic combo.\n                ',
      tunable=TunableReference(description='\n                    A reference to the second part of the relic.\n                    ',
      manager=(services.definition_manager()),
      pack_safe=True)),
      object_a_state=OptionalTunable(description='\n                If enabled, the participant being checked against Object A\n                must also be in this state to qualify for this relic\n                combination. For example, a crystal is required to be in the\n                high quality state to count towards the high quality relic\n                discovery.\n                ',
      tunable=TunableReference(description='\n                    A state value Object A needs to be in to qualify for\n                    this relic combo.\n                    ',
      manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions=('ObjectStateValue', ),
      pack_safe=True)),
      object_b_state=OptionalTunable(description='\n                If enabled, the participant being checked against Object B\n                must also be in this state to qualify for this relic\n                combination. For example, a crystal is required to be in the\n                high quality state to count towards the high quality relic\n                discovery.\n                ',
      tunable=TunableReference(description='\n                    A state value Object A needs to be in to qualify for\n                    this relic combo.\n                    ',
      manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions=('ObjectStateValue', ),
      pack_safe=True)),
      undiscovered_picker_description_text=OptionalTunable(description='\n                If this is set to Link To Other Relic Data, instead of using\n                the Default Undiscovered Text, we\'ll use whatever text is\n                available for linked relic combination.\n                \n                For instance, if this is the tuning for the llama-chaos\n                relic being combined with a gem, this could be enabled and\n                point to the "llama top chaos bottom" combo so that data\n                will be provided if the Sim hasn\'t learned about this\n                specific combination yet.\n                ',
      enabled_name='link_to_other_relic_data',
      disabled_name='use_default_undiscovered_text',
      tunable=TunableEnumEntry(description='\n                    The Relic Combination ID to use as a reference to this\n                    combination.\n                    ',
      tunable_type=RelicComboId,
      default=(RelicComboId.INVALID),
      invalid_enums=(
     RelicComboId.INVALID,))),
      discovered_picker_description_text=TunableLocalizedString(description='\n                The relic description text to use if this relic/gem\n                combination is known by the Sim.\n                '),
      hovertip_data=OptionalTunable(description="\n                If enabled, this combination can also provide it's information\n                to the hovertip of the tuned object.\n                ",
      tunable=TunableTuple(description='\n                    The objects and potential required states.\n                    ',
      objects=TunableSet(description='\n                        A set of objects that will provide the information from\n                        this relic combo.\n                        ',
      tunable=TunableReference(description='\n                            A reference to the second part of the relic.\n                            ',
      manager=(services.definition_manager()),
      pack_safe=True)),
      object_state=OptionalTunable(description='\n                        If enabled, the participant being checked against Object A\n                        must also be in this state to qualify for this relic\n                        combination. For example, a crystal is required to be in the\n                        high quality state to count towards the high quality relic\n                        discovery.\n                        ',
      tunable=TunableReference(description='\n                            A state value Object A needs to be in to qualify for\n                            this relic combo.\n                            ',
      manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions=('ObjectStateValue', ),
      pack_safe=True))))))
    DEFAULT_UNDISCOVERED_TEXT = TunableLocalizedString(description="\n        The default text to use when something hasn't been discovered yet.\n        ")
    IN_WORLD_HOVERTIP_TEXT = TunableLocalizedString(description="\n        The hovertip text to show on relics when they're in the world. When\n        they're in the inventory, they'll use the hovertip text tuned on the\n        relic data.\n        ")

    @classmethod
    def get_relic_combo_id_data_tuple_for_objects(cls, object_a, object_b):
        for combo_id, combo_data in RelicTuning.RELIC_DISCOVERY_DATA.items():
            if object_a.definition in combo_data.object_a:
                if object_b.definition in combo_data.object_b:
                    if cls._objects_in_correct_states(object_a, combo_data.object_a_state, object_b, combo_data.object_b_state):
                        return (
                         combo_id, combo_data)
            if object_a.definition in combo_data.object_b and object_b.definition in combo_data.object_a and cls._objects_in_correct_states(object_a, combo_data.object_b_state, object_b, combo_data.object_a_state):
                return (
                 combo_id, combo_data)

        return (None, None)

    @classmethod
    def _objects_in_correct_states(cls, object_a, object_a_state, object_b, object_b_state):
        if object_a_state is not None:
            if not object_a.state_value_active(object_a_state):
                return False
        if object_b_state is not None:
            if not object_b.state_value_active(object_b_state):
                return False
        return True

    @classmethod
    def get_relic_combo_data_for_combo_id(cls, combo_id):
        return RelicTuning.RELIC_DISCOVERY_DATA.get(combo_id, None)

    @classmethod
    def get_relic_combo_id_data_tuple_for_hovertip(cls, hovertip_object):
        for combo_id, combo_data in RelicTuning.RELIC_DISCOVERY_DATA.items():
            hovertip_data = combo_data.hovertip_data
            if hovertip_data is None:
                continue
            if hovertip_object.definition in hovertip_data.objects:
                if hovertip_data.object_state is not None:
                    if not hovertip_object.state_value_active(hovertip_data.object_state):
                        continue
                return (
                 combo_id, combo_data)

        return (None, None)