# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\away_actions\away_actions_util.py
# Compiled at: 2020-06-25 15:00:52
# Size of source mod 2**32: 5259 bytes
from interactions.utils.success_chance import SuccessChance
from sims4.tuning.tunable import HasTunableFactory, TunableList, TunableVariant
from statistics.statistic_conditions import TunableStatisticCondition, TunableTimeRangeCondition
from statistics.statistic_ops import DynamicSkillLootOp, DynamicVariantSkillLootOp, GAIN_TYPE_RATE, StatisticAddRelationship, StatisticChangeOp, StatisticOperation, RelationshipOperation, ChangeStatisticByCategory
import alarms, clock

class TunableAwayActionCondition(TunableVariant):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, stat_based=TunableStatisticCondition(description='\n                A condition based on the status of a statistic.\n                '), 
         time_based=TunableTimeRangeCondition(description='\n                The minimum and maximum amount of time required to satisfy this\n                condition.\n                '), 
         default='stat_based', **kwargs)


class PeriodicStatisticChange(HasTunableFactory):
    FACTORY_TUNABLES = {'operations': TunableList(description='\n            A list of statistic operations that occur at each interval.\n            ',
                     tunable=TunableVariant(dynamic_skill=DynamicSkillLootOp.TunableFactory(description='\n                    Dynamically adds to the defined skill.\n                    ',
                     locked_args={'chance':SuccessChance.ONE, 
                    'exclusive_to_owning_si':False}),
                     dynamic_variant_skill=DynamicVariantSkillLootOp.TunableFactory(description='\n                    Grabs a skill from another source of tuning and dynamically\n                    adds to it.\n                    ',
                     locked_args={'chance': SuccessChance.ONE}),
                     relationship_change=(StatisticAddRelationship.TunableFactory)(description='\n                    Adds to the relationship score statistic for this Super\n                    Interaction\n                    ', 
                    amount=GAIN_TYPE_RATE, 
                    locked_args={'chance':SuccessChance.ONE, 
 'stat':None}, **RelationshipOperation.DEFAULT_PARTICIPANT_ARGUMENTS),
                     statistic_change=(StatisticChangeOp.TunableFactory)(description='\n                    Modify the value of a statistic.\n                    ', 
                    amount=GAIN_TYPE_RATE, 
                    locked_args={'chance':SuccessChance.ONE, 
 'exclusive_to_owning_si':False, 
 'advertise':False}, 
                    statistic_override=StatisticChangeOp.get_statistic_override(pack_safe=True), **StatisticOperation.DEFAULT_PARTICIPANT_ARGUMENTS),
                     statistic_change_by_category=ChangeStatisticByCategory.TunableFactory(description='\n                    Change value of  all statistics of a specific category.\n                    ',
                     locked_args={'chance': SuccessChance.ONE})))}

    def __init__(self, away_action, operations):
        self._away_action = away_action
        self._operations = operations
        self._alarm_handle = None

    def _do_statistic_gain(self, _):
        resolver = self._away_action.get_resolver()
        for operation in self._operations:
            operation.apply_to_resolver(resolver)

    def run(self):
        if self._operations:
            if self._alarm_handle is None:
                time_span = clock.interval_in_sim_minutes(StatisticOperation.STATIC_CHANGE_INTERVAL)
                self._alarm_handle = alarms.add_alarm(self, time_span,
                  (self._do_statistic_gain),
                  repeating=True)

    def stop(self):
        if self._alarm_handle is not None:
            alarms.cancel_alarm(self._alarm_handle)
            self._alarm_handle = None