# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\crafting_cache.py
# Compiled at: 2015-07-28 18:35:20
# Size of source mod 2**32: 3661 bytes
from collections import Counter
import sims4.log
logger = sims4.log.Logger('CraftingCache', default_owner='rmccord')

class CraftingObjectCache:

    def __init__(self):
        self._user_directed_cache = Counter()
        self._autonomy_cache = Counter()

    def add_type(self, crafting_type, user_directed=True, autonomy=True):
        if user_directed:
            self._add_type_to_cache(crafting_type, self._user_directed_cache)
        if autonomy:
            self._add_type_to_cache(crafting_type, self._autonomy_cache)

    def _add_type_to_cache(self, crafting_type, cache):
        if crafting_type in cache:
            cache[crafting_type] += 1
        else:
            cache[crafting_type] = 1

    def remove_type(self, crafting_type, user_directed=True, autonomy=True):
        if user_directed:
            self._remove_type_from_cache(crafting_type, self._user_directed_cache)
        if autonomy:
            self._remove_type_from_cache(crafting_type, self._autonomy_cache)

    def _remove_type_from_cache(self, crafting_type, cache):
        ref_count = cache.get(crafting_type)
        if ref_count is not None:
            if ref_count <= 0:
                logger.error("Crafting cache has a ref count of {} for {}, which shoudn't be possible", ref_count, crafting_type, owner='rmccord')
                del cache[crafting_type]
            elif ref_count == 1:
                del cache[crafting_type]
            else:
                cache[crafting_type] -= 1
        else:
            logger.error('Attempting to remove object {} from cache that has never been added to it', crafting_type, owner='rmccord')

    def get_ref_count(self, crafting_type, from_autonomy=False):
        if from_autonomy:
            return self._autonomy_cache.get(crafting_type, 0)
        return self._user_directed_cache.get(crafting_type, 0)

    def __iter__(self):
        return self._user_directed_cache.items().__iter__()

    def clear(self):
        self._user_directed_cache.clear()
        self._autonomy_cache.clear()