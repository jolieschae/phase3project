# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\genre.py
# Compiled at: 2014-10-15 19:56:47
# Size of source mod 2**32: 2720 bytes
from sims4.localization import TunableLocalizedString, LocalizationHelperTuning, TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, TunableTuple
import sims4.reload, tag
with sims4.reload.protected(globals()):
    ALL_GENRE_SET = None

class Genre:
    TAG_TO_TUNING_MAP = TunableMapping(description='\n        Mapping between genres and their tuning. All tags added to this mapping\n        are automatically considered a genre tag.\n        ',
      key_type=TunableEnumEntry(description='\n            Tag of the genre.\n            ',
      tunable_type=(tag.Tag),
      default=(tag.Tag.INVALID),
      pack_safe=True),
      value_type=TunableTuple(description='\n            Tuning for the genre.\n            ',
      localized_name=TunableLocalizedString(description='\n                The name of the genre.\n                ')))
    GENRE_PREFIX_STRING_FACTORY = TunableLocalizedStringFactory(description='\n        The prefix that will be displayed. {0.String} will be the comma-\n        separated list of genres the object has.\n        ')

    @staticmethod
    def get_genres(obj):
        global ALL_GENRE_SET
        if ALL_GENRE_SET is None:
            ALL_GENRE_SET = frozenset(Genre.TAG_TO_TUNING_MAP.keys())
        object_tags = set(obj.get_tags())
        return ALL_GENRE_SET & object_tags

    @staticmethod
    def get_genre_localized_string(obj):
        genres = Genre.get_genres(obj)
        if not genres:
            return
        strings = tuple((Genre.TAG_TO_TUNING_MAP[genre].localized_name for genre in genres))
        comma_seperated_list = (LocalizationHelperTuning.get_comma_separated_list)(*strings)
        genre_text = Genre.GENRE_PREFIX_STRING_FACTORY(comma_seperated_list)
        return genre_text