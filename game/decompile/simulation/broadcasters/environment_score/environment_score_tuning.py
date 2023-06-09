# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\broadcasters\environment_score\environment_score_tuning.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 4599 bytes
from broadcasters.environment_score.environment_score_broadcaster import BroadcasterEnvironmentScore
from objects.components.state import ObjectStateValue
from sims4.resources import Types
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, TunableReference, TunableTuple
from statistics.commodity import Commodity
from statistics.mood import Mood
import services, tag

class EnvironmentScoreTuning:
    ENVIRONMENT_SCORE_BROADCASTER = BroadcasterEnvironmentScore.TunableReference(description='\n        The singleton broadcaster that groups all scoring objects. The\n        constraints on this broadcaster determine the constraint within which a\n        Sim is affected by environment score.\n        ')
    ENVIRONMENT_SCORE_MOODS = TunableMapping(description="\n        Tags on Objects correspond to a particular Mood.\n                \n        When an object is going to contribute to the environment score, put a\n        tag in it's catalog object, and make sure that tag points to a Mood\n        here.\n        ",
      key_type=TunableEnumEntry(description='\n            The Tag that corresponds to mood and environmental scoring data.\n            ',
      tunable_type=(tag.Tag),
      default=(tag.Tag.INVALID)),
      value_type=Mood.TunableReference(description='\n            The mood that the Sim must be in for an object that emits this mood\n            to score. Corresponds to the mood_tag.\n            '),
      key_name='object_tag',
      value_name='mood')
    NEGATIVE_ENVIRONMENT_SCORING = Commodity.TunableReference(description='\n        Defines the ranges and corresponding buffs to apply for negative\n        environmental contribution.\n        \n        Be sure to tune min, max, and the different states. The convergence\n        value is what will remove the buff. Suggested to be 0.\n        ')
    POSITIVE_ENVIRONMENT_SCORING = Commodity.TunableReference(description='\n        Defines the ranges and corresponding buffs to apply for positive\n        environmental contribution.\n        \n        Be sure to tune min, max, and the different states. The convergence\n        value is what will remove the buff. Suggested to be 0.\n        ')
    BUILD_OBJECTS_ENVIRONMENT_SCORING = TunableTuple(description='\n        Defines the statistics which track the value of positive and negative\n        environmental contribution from build objects.\n        ',
      negative_environment_scoring=TunableReference(description='\n            Negative environmental statistic.\n            ',
      manager=(services.get_instance_manager(Types.STATISTIC)),
      class_restrictions=('Statistic', )),
      positive_environment_scoring=TunableReference(description='\n            Positive environmental statistic.\n            ',
      manager=(services.get_instance_manager(Types.STATISTIC)),
      class_restrictions=('Statistic', )))
    ENABLE_AFFORDANCE = TunableReference(description='\n        The interaction that will turn on Environment Score for a particular\n        object. This interaction should set a state on the object that will\n        have multipliers of 1 and adders of 0 for all moods.\n        ',
      manager=(services.get_instance_manager(Types.INTERACTION)))
    DISABLE_AFFORDANCE = TunableReference(description='\n        The interaction that will turn off Environment Score for a particular\n        object. This interaction should set a state on the object that will\n        have multipliers of 0 and adders of 0 for all moods.\n        ',
      manager=(services.get_instance_manager(Types.INTERACTION)))
    ENABLED_STATE_VALUE = ObjectStateValue.TunableReference(description='\n        A state value that indicates the object should be contributing\n        Environment Score.\n        ')
    DISABLED_STATE_VALUE = ObjectStateValue.TunableReference(description='\n        A state value that indicates the object should not be contributing\n        Environment Score.\n        ')