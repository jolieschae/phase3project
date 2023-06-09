# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\tunable_provided_affordances.py
# Compiled at: 2017-04-06 17:29:14
# Size of source mod 2**32: 4383 bytes
from interactions import ParticipantType
from sims4.tuning.tunable import TunableList, TunableTuple, TunableReference, TunableEnumEntry, Tunable
from tunable_utils.tunable_object_filter import TunableObjectFilterVariant
import services, sims4.resources

class TunableProvidedAffordances(TunableList):

    def __init__(self, target_default=ParticipantType.Object, carry_target_default=ParticipantType.Object, locked_args=None, class_restrictions=(), **kwargs):
        (super().__init__)(tunable=TunableTuple(description='\n                Tunables related to a specific affordance we are providing,\n                with the ability to override specifics about targets,\n                restrictions, and dependencies.\n                ',
                    affordance=TunableReference(description='\n                    An affordance we make available. Pay attention to who this\n                    affordance is provided on. See the provided affordances\n                    description for more info.\n                    ',
                    manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
                    class_restrictions=class_restrictions,
                    pack_safe=True),
                    target=TunableEnumEntry(description='\n                    The participant the affordance will target. See the\n                    provided affordances description for more info.\n                    ',
                    tunable_type=ParticipantType,
                    default=target_default),
                    carry_target=TunableEnumEntry(description='\n                    The participant the affordance will set as a carry target.\n                    ',
                    tunable_type=ParticipantType,
                    default=carry_target_default),
                    allow_self=Tunable(description='\n                    If set, the Sim running the providing interaction is\n                    allowed to also run the provided interaction.\n                    ',
                    tunable_type=bool,
                    default=False),
                    is_linked=Tunable(description='\n                    When set to True if the original affordance is canceled,\n                    the provided affordance will be as well. \n                    \n                    If set to False then canceling the original affordance \n                    will not affect the provided affordance.\n                    ',
                    tunable_type=bool,
                    default=True),
                    unlink_if_running=Tunable(description='\n                    If checked, the provided interaction is not canceled if the\n                    interaction it depends on is canceled after the provided\n                    interaction has already started transitioning.\n                    \n                    This is useful if it is expected for the provided\n                    interaction to cancel the providing one (but we want to\n                    preserve the linked cancelation behavior in the queue.)\n                    \n                    e.g.: Sit on Toddler Bed provides Tuck In. Tuck In\n                    transitions the toddler from Sit to Relax (canceling Sit).\n                    We want the Tuck In to complete once the transition has\n                    started.\n                    ',
                    tunable_type=bool,
                    default=False),
                    object_filter=TunableObjectFilterVariant(description='\n                    Define the type of objects this affordance is provided on.\n                    '),
                    locked_args=(locked_args if locked_args is not None else {})), **kwargs)