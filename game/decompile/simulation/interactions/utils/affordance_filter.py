# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\affordance_filter.py
# Compiled at: 2020-03-12 18:10:14
# Size of source mod 2**32: 2356 bytes
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableList, TunableVariant
from snippets import TunableAffordanceFilterSnippet, TunableAffordanceListReference
from tag import TunableTags

class AffordanceFilterFactory(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'affordance_filter': TunableAffordanceFilterSnippet(description='\n            Affordances this modifier affects.\n            ')}

    def __call__(self, affordance):
        return self.affordance_filter(affordance)


class AffordanceTagFactory(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'interaction_tags':TunableTags(description='\n            Affordances with any of these tags to affect.\n            ',
       filter_prefixes=('Interaction', )), 
     'exceptions':TunableList(description='\n            Affordances that are not affected even if they have the specified\n            tags.\n            ',
       tunable=TunableAffordanceListReference(pack_safe=True))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        affordance_exceptions = frozenset((affordance for exception_list in self.exceptions for affordance in exception_list))
        self.affordance_exceptions = affordance_exceptions or None

    def __call__(self, affordance):
        if affordance.interaction_category_tags & self.interaction_tags:
            if self.affordance_exceptions is None or affordance not in self.affordance_exceptions:
                return False
        return True


class AffordanceFilterVariant(TunableVariant):

    def __init__(self, *_, description=None, **__):
        super().__init__(by_affordance_filter=(AffordanceFilterFactory.TunableFactory()),
          by_tags=(AffordanceTagFactory.TunableFactory()),
          default='by_affordance_filter',
          description=description)