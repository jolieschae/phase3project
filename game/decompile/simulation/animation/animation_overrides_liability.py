# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\animation_overrides_liability.py
# Compiled at: 2019-07-10 19:30:00
# Size of source mod 2**32: 2445 bytes
import weakref
from animation.tunable_animation_overrides import TunableAnimationObjectOverrides
from interactions import ParticipantTypeReaction
from interactions.liability import Liability
from sims4.tuning.tunable import HasTunableFactory, TunableEnumEntry, AutoFactoryInit

class AnimationOverridesLiability(Liability, HasTunableFactory, AutoFactoryInit):
    LIABILITY_TOKEN = 'AnimationOverridesLiability'
    FACTORY_TUNABLES = {'participants':TunableEnumEntry(description='\n            The Sims or objects to apply these overrides to.\n            ',
       tunable_type=ParticipantTypeReaction,
       default=ParticipantTypeReaction.Actor), 
     'animation_overrides':TunableAnimationObjectOverrides(description='\n            The overrides to apply.\n            ')}

    def __init__(self, interaction, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._participants = weakref.WeakSet()

    def on_add(self, interaction):
        for obj in interaction.get_participants(self.participants):
            if obj is None:
                continue
            self._participants.add(obj)
            obj.add_dynamic_animation_overrides(self.animation_overrides)
            if not obj.is_sim:
                continue
            for si in obj.si_state:
                animation_context = si.animation_context
                if animation_context is not None:
                    for asm in animation_context.get_asms_gen():
                        actor_name = asm.get_actor_name(obj)
                        if actor_name is not None:
                            overrides = obj.get_anim_overrides(actor_name)
                            if overrides is not None:
                                overrides.override_asm(asm, actor=obj)

    def release(self):
        for obj in self._participants:
            obj.remove_dynamic_animation_overrides(self.animation_overrides)