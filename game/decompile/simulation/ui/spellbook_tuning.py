# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\ui\spellbook_tuning.py
# Compiled at: 2019-06-17 16:13:42
# Size of source mod 2**32: 9543 bytes
import services
from audio.tunable_audio import TunableAudioAllPacks
from interactions.utils.tunable_icon import TunableIconAllPacks
from sims4.localization import TunableLocalizedString, TunableLocalizedStringFactory
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableTuple, OptionalTunable, TunableRange, TunableVariant, TunableList, TunableReference, TunableEnumEntry, TunableMapping
from sims4.tuning.tunable_base import GroupNames
from ui.book_tuning import BookCategoryDisplayType

class SpellbookCategoryData(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'content_list':TunableTuple(description='\n            Tuning used for the content list.\n            ',
       icon=TunableIconAllPacks(description='\n                Icon used to display this category in the content list.\n                '),
       tooltip=OptionalTunable(description='\n                Tooltip used in the spellbook for this category.\n                If unset, no tooltip is shown.\n                ',
       tunable=(TunableLocalizedString()))), 
     'front_page':TunableTuple(description='\n            Tuning used for the first page of the category.\n            ',
       category_description=OptionalTunable(description='\n                Description used in the spellbook.\n                If unset, description is not shown.\n                ',
       tunable=(TunableLocalizedString())),
       icon=TunableIconAllPacks(description='\n                Icon used to display this category in first page.\n                ')), 
     'page':TunableTuple(description='\n            Tuning used for pages other than the front page of the category.\n            ',
       icon=OptionalTunable(description='\n                Icon shown on each page of this category.\n                ',
       tunable=(TunableIconAllPacks()))), 
     'tab':TunableTuple(description='\n            Tuning used to display the category on the tabs at the\n            top of the book.\n            ',
       icon=TunableIconAllPacks(description='\n                Icon used to display the category on a tab.\n                '),
       tooltip=OptionalTunable(description='\n                Tooltip used in the spellbook on the the tab for this category.\n                If unset, Category Name is used.\n                ',
       tunable=(TunableLocalizedString()))), 
     'category_name':TunableLocalizedString(description='Name of this category'), 
     'content':TunableVariant(spells=TunableTuple(entries=TunableList(description='\n                    List of spells in this category.\n                    ',
       tunable=TunableReference(description='The spell.',
       manager=(services.get_instance_manager(Types.SPELL)),
       pack_safe=True)),
       category_type=TunableEnumEntry(description='\n                    The category this corresponds to.\n                    ',
       tunable_type=BookCategoryDisplayType,
       default=(BookCategoryDisplayType.WITCH_PRACTICAL_SPELL),
       invalid_enums=(
      BookCategoryDisplayType.WITCH_POTION,))),
       potions=TunableTuple(entries=TunableList(description='\n                    List of potions in this category.\n                    ',
       tunable=TunableReference(description="The potion's recipe.",
       manager=(services.get_instance_manager(Types.RECIPE)),
       class_restrictions=('Recipe', ),
       pack_safe=True)),
       locked_args={'category_type': BookCategoryDisplayType.WITCH_POTION}),
       default='spells')}


class SpellbookRecipeData(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'potion_description':OptionalTunable(description='\n            Description used in the spellbook.\n            If unset, uses the recipe description.\n            ',
       tunable=TunableLocalizedString()), 
     'locked_description':OptionalTunable(description='\n            Description used in the spellbook if potion is not yet unlocked.\n            If unset, uses potion_description.\n            ',
       tunable=TunableLocalizedString()), 
     'icon':TunableIconAllPacks(description='\n            Icon used to display this recipe in the spellbook.\n            '), 
     'tooltip':OptionalTunable(description='\n            Tooltip used in the spellbook.\n            If unset, no tooltip is shown.\n            ',
       tunable=TunableLocalizedString())}


class SpellbookTuning:
    FRONT_PAGE_DATA = TunableTuple(description='\n        UI-specific data used to display front page.\n        ',
      title=TunableLocalizedStringFactory(description='\n            The title to use on the front page of the spellbook.\n            '),
      icon=OptionalTunable(description='\n            Image displayed on front page of spellbook.\n            If unset, image is not shown.\n            ',
      tunable=(TunableIconAllPacks())),
      page_description=OptionalTunable(description='\n            Description used for this page in the spellbook.\n            If unset, description is not shown.\n            ',
      tunable=(TunableLocalizedString())))
    CATEGORY_LIST_DATA = TunableTuple(description='\n        UI-specific data used to display second page of the spellbook.\n        ',
      title=TunableLocalizedStringFactory(description='\n            The title to use on the category list of the spellbook.\n            '),
      icon=OptionalTunable(description='\n            Icon used on the category list page of the spellbook.\n            ',
      tunable=(TunableIconAllPacks())),
      page_description=OptionalTunable(description='\n            Description used for this page in the spellbook.\n            If unset, description is not shown.\n            ',
      tunable=(TunableLocalizedString())))
    CATEGORY_DATAS = TunableList(description='\n        A list of a spellbook category data.\n        ',
      tunable=(SpellbookCategoryData.TunableFactory()),
      tuning_group=(GroupNames.UI))
    POTION_DISPLAY_DATA = TunableMapping(description="\n        A mapping of a potion's recipe to it's spellbook display data. \n        ",
      key_type=TunableReference(description="\n            The potion's recipe.\n            ",
      manager=(services.get_instance_manager(Types.RECIPE)),
      class_restrictions=('Recipe', ),
      pack_safe=True),
      value_type=(SpellbookRecipeData.TunableFactory()),
      tuning_group=(GroupNames.UI))
    INGREDIENTS_LABEL = TunableLocalizedString(description='\n        Text used to display ingredients label for a spell or potion.\n        \n        e.g. "Ingredients:"\n        ',
      tuning_group=(GroupNames.UI))
    PROGRESS_LABEL = TunableLocalizedString(description='\n        Text used to display field name for progress into a specific\n        category.\n        \n        e.g. "Learned:"\n        ',
      tuning_group=(GroupNames.UI))
    PROGRESS_TEXT_FORMAT = TunableLocalizedStringFactory(description='\n        Text used to display the progress towards completing a specific\n        category.  Takes current items learned and and total available.\n\n        e.g. "{0.Number}/{1.Number}"\n        ',
      tuning_group=(GroupNames.UI))
    CATEGORY_FRONT_PAGE_ENTRY_COUNT = TunableRange(description=',\n        Number of entries allotted for the front page of a category section.\n        ',
      tunable_type=int,
      minimum=0,
      tuning_group=(GroupNames.UI),
      default=2)
    CATEGORY_ENTRY_COUNT = TunableRange(description=',\n        Number of entries allotted for the subsequent pages of a category section.\n        ',
      tunable_type=int,
      minimum=1,
      tuning_group=(GroupNames.UI),
      default=4)
    INGREDIENT_FORMAT = TunableLocalizedStringFactory(description='\n        The format used for ingredients in the spellbook.\n        First parameter will be name of ingredient, second will be quantity required.\n        e.g. {0.String}({1.Number}) = "Frog(1)"\n        ',
      tuning_group=(GroupNames.UI))