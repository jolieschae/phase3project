# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_set.py
# Compiled at: 2015-01-07 21:19:11
# Size of source mod 2**32: 2118 bytes
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableEnumEntry, TunableList, TunableTuple, TunableReference, Tunable, TunableSet, HasTunableReference
from situations.situation_goal import TunableWeightedSituationGoalReference
from tag import Tag
import services, sims4.resources
logger = sims4.log.Logger('SituationGoalSet', default_owner='tingyul')

class TunableWeightedSituationGoalSetReference(TunableTuple):

    def __init__(self, **kwargs):
        super().__init__(weight=Tunable(float, 1.0, description='Higher number means higher chance of being selected.'), goal_set=TunableReference((services.get_instance_manager(sims4.resources.Types.SITUATION_GOAL_SET)), description='A goal set.'))


class SituationGoalSet(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SITUATION_GOAL_SET)):
    INSTANCE_TUNABLES = {'goals':TunableList(TunableWeightedSituationGoalReference(), description='List of weighted goals.'), 
     'chained_goal_sets':TunableList(TunableReference(services.get_instance_manager(sims4.resources.Types.SITUATION_GOAL_SET)), description='List of chained goal sets in priority order.'), 
     'role_tags':TunableSet(TunableEnumEntry(Tag, Tag.INVALID), description='Goals from this set will only be given to Sims in SituationJobs or Role States marked with one of these tags.')}

    @classmethod
    def _verify_tuning_callback(cls):
        if any((weighted_goal_ref.goal is None for weighted_goal_ref in cls.goals)):
            logger.error('Goals has an empty goal reference in tunable {}', cls)