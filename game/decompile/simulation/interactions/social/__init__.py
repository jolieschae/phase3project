# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\social\__init__.py
# Compiled at: 2016-09-15 21:36:00
# Size of source mod 2**32: 4046 bytes
from date_and_time import create_time_span
from event_testing import test_events
from interactions import ParticipantType
from sims4.sim_irq_service import yield_to_irq
from sims4.tuning.tunable import Tunable
import alarms, services

class SocialInteractionMixin:
    INSTANCE_TUNABLES = {'_acquire_listeners_as_resource': Tunable(description='\n            If checked, all listener Sims will be acquired as part of this\n            interaction.  If unchecked, listeners running interactions that\n            ignore socials will not play reactionlets.\n            \n            Most interactions will want not to acquire listener Sims.  Not\n            acquiring listener Sims will allow for smoother gameplay when Sims\n            are multitasking while socializing. However, interactions with\n            visually defining reactionlets, such as Tell Joke or Make Toast\n            might want to acquire all listeners and have them react.\n            ',
                                         tunable_type=bool,
                                         default=False)}

    def __init__(self, *args, picked_object=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._picked_object_ref = picked_object.ref() if picked_object is not None else None
        self._target_interaction_event_alarm_handle = None

    @property
    def picked_object(self):
        if self._picked_object_ref is not None:
            return self._picked_object_ref()

    @property
    def acquire_listeners_as_resource(self):
        return self._acquire_listeners_as_resource

    def _trigger_interaction_start_event(self):
        super()._trigger_interaction_start_event()
        if self.social_group is not None:
            self.social_group._on_interaction_start(self)

    def _trigger_interaction_complete_test_event(self):
        yield_to_irq()
        super()._trigger_interaction_complete_test_event()
        self._remove_target_event_auto_update()

    def _register_target_event_auto_update(self):
        target_sim = self.get_participant(ParticipantType.TargetSim)
        if target_sim is not None:
            if self._target_interaction_event_alarm_handle is not None:
                self._remove_target_event_auto_update()
            self._target_interaction_event_alarm_handle = alarms.add_alarm(self, create_time_span(minutes=15), lambda _, sim_info=target_sim.sim_info, interaction=self, custom_keys=self.get_keys_to_process_events(): services.get_event_manager().process_event((test_events.TestEvent.InteractionUpdate), sim_info=sim_info,
              interaction=self,
              custom_keys=custom_keys), True)

    def _remove_target_event_auto_update(self):
        if self._target_interaction_event_alarm_handle is not None:
            alarms.cancel_alarm(self._target_interaction_event_alarm_handle)
            self._target_interaction_event_alarm_handle = None

    def setup_asm_default(self, asm, *args, **kwargs):
        result = (super().setup_asm_default)(asm, *args, **kwargs)
        if self.social_group is not None:
            (self.social_group.setup_asm_default)(asm, *args, **kwargs)
        return result