# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\favorite_object_situation_mixin.py
# Compiled at: 2019-08-07 19:09:08
# Size of source mod 2**32: 3096 bytes
from collections import defaultdict
import random, services
from sims4.tuning.tunable import TunableTuple, TunableList, TunableEnumEntry, TunableSet, TunableReference
from sims4.tuning.tunable_base import GroupNames
from tag import TunableTag

class FavoriteObjectSituationMixin:
    INSTANCE_TUNABLES = {'_favorite_objects': TunableList(description='\n            A list of favorites objects to give to Sims when they enter this\n            situation. These favorites will be removed from the Sim when the \n            situation ends.\n            ',
                            tunable=TunableTuple(description='\n                Favorite data to add to the Sim.\n                ',
                            favorite_tag=TunableTag(description='\n                    The tag for this favorite object.\n                    ',
                            filter_prefixes=('func', )),
                            potential_favorites=TunableSet(description='\n                    A set of potential objects. One of these will be chosen at\n                    random.\n                    ',
                            tunable=TunableReference(description='\n                        The definition of the favorite object.\n                        ',
                            manager=(services.definition_manager())),
                            minlength=1)),
                            tuning_group=(GroupNames.SITUATION))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._favorite_types_added = defaultdict(set)

    def _on_set_sim_job(self, sim, job_type):
        super()._on_set_sim_job(sim, job_type)
        favorites_tracker = sim.sim_info.favorites_tracker
        if favorites_tracker is None:
            return
        for favorite_data in self._favorite_objects:
            favorite_tag = favorite_data.favorite_tag
            if favorites_tracker.has_favorite(favorite_tag):
                continue
            self._favorite_types_added[sim.id].add(favorite_tag)
            favorite_object = random.choice(list(favorite_data.potential_favorites))
            favorites_tracker.set_favorite(favorite_tag, obj_def_id=(favorite_object.id))

    def _on_remove_sim_from_situation(self, sim):
        favorites = self._favorite_types_added.get(sim.id, None)
        if favorites:
            favorites_tracker = sim.sim_info.favorites_tracker
            for favorite in favorites:
                favorites_tracker.clear_favorite_type(favorite)

        super()._on_remove_sim_from_situation(sim)