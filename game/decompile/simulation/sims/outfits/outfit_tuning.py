# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\outfits\outfit_tuning.py
# Compiled at: 2018-05-01 19:56:28
# Size of source mod 2**32: 6366 bytes
from animation.animation_element import AnimationElement
from buffs.tunable import TunableBuffReference
from event_testing.tests import TunableTestSet
from interactions.utils.loot import LootActions
from sims.outfits.outfit_enums import OutfitCategory, OutfitChangeReason
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableList, TunableEnumEntry, TunableMapping, TunableTuple, OptionalTunable, TunableEnumWithFilter
from tag import Tag
import services, sims4.resources
logger = sims4.log.Logger('OutfitTuning')

class OutfitTuning:

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, value, **kwargs):
        from sims.outfits.outfit_interactions import OutfitChangeSelfInteraction
        interaction_manager = services.get_instance_manager(sims4.resources.Types.INTERACTION)
        outfit_tags = set()
        for interaction in interaction_manager.types.values():
            if issubclass(interaction, OutfitChangeSelfInteraction):
                outfit_tags.update(interaction.outfit_change_type.get_outfit_tags())

        if not outfit_tags:
            return
        missing_keys = outfit_tags - value.keys()
        if missing_keys:
            logger.error('Outfit Tags {} tuned in a OutfitChangeSelfInteraction are missing from COSTUMES_LOCALIZATION_TUNING', missing_keys, owner='camilogarcia')

    INAPPROPRIATE_STREETWEAR = TunableList(description='\n        A list of outfit categories inappropriate for wearing on open streets.\n        If the Sim is in one of these categories when they first decided to go\n        off-lot, they will switch out of it beforehand.\n        ',
      tunable=TunableEnumEntry(tunable_type=OutfitCategory,
      default=(OutfitCategory.EVERYDAY)))
    OUTFIT_CATEGORY_TUNING = TunableMapping(description='\n        Define attributes specific to each of the existing outfit categories.\n        ',
      key_type=OutfitCategory,
      value_type=TunableTuple(description='\n            Data specific to the outfit category.\n            ',
      save_outfit_category=OptionalTunable(description="\n                If set to 'save_this_category', a Sim saved while wearing this\n                outfit category will change back into this outfit category on\n                load.\n                \n                e.g.: you're tuning Everyday outfit, which is set as\n                save_this_category, meaning a sim wearing everyday will still be\n                wearing everyday on load.\n                \n                Otherwise, you can set to save_as_different_category, which\n                allows you to specific another outfit category for the sim to be\n                saved in instead of this category.\n                \n                e.g.: if tuning Bathing category, if the sim is in the bathing\n                category, set this to Everyday so that when the sim loads back\n                up, the sim will be in Everyday wear instead of naked.\n                ",
      tunable=TunableEnumEntry(description='\n                    The outfit category to save as instead of this category.\n                    ',
      tunable_type=OutfitCategory,
      default=(OutfitCategory.EVERYDAY)),
      disabled_name='save_this_category',
      enabled_name='save_as_different_category'),
      buffs=TunableList(description='\n                List of buffs given to sim while in this outfit category.\n                ',
      tunable=TunableBuffReference(description='\n                    Buff that will get added to sim.\n                    ',
      pack_safe=True))))
    COSTUMES_LOCALIZATION_TUNING = TunableMapping(description='\n        Mapping of tags for sim costumes to localization strings.  This will be\n        used for pie menu interactions when we want to switch to this specific\n        custom costume tags.\n        ',
      key_type=TunableEnumWithFilter(tunable_type=Tag,
      filter_prefixes=('uniform', 'outfitcategory', 'style'),
      default=(Tag.INVALID),
      pack_safe=True),
      value_type=(TunableLocalizedStringFactory()),
      verify_tunable_callback=_verify_tunable_callback)
    OUTFIT_CHANGE_ANIMATION = AnimationElement.TunableReference(description='\n        An animation to use when switching into an outfit.\n        ')
    OUTFIT_CHANGE_REASONS = TunableMapping(description='\n        Define the outfits that correspond to specific Outfit Change Reasons.\n        ',
      key_type=OutfitChangeReason,
      value_type=TunableList(description='\n            A list of test and Outfit Category pairs. The outfit corresponding to the\n            first passing test is selected.\n            ',
      tunable=TunableTuple(description='\n                A test and Outfit Category pair.\n                ',
      tests=(TunableTestSet()),
      outfit_category=TunableEnumEntry(description='\n                    Should the associated test pass, the Outfit Category to\n                    switch into for the specified reason.\n                    ',
      tunable_type=OutfitCategory,
      default=(OutfitCategory.EVERYDAY)))),
      key_name='OutfitChangeReason',
      value_name='TunableMappings')
    LOOT_ON_OUTFIT_CHANGE = TunableList(description='\n        Loot that will be applied every time a Sim changes their outfit.\n        ',
      tunable=LootActions.TunableReference(pack_safe=True),
      unique_entries=True)