# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_travel_behavior.py
# Compiled at: 2017-06-13 20:32:42
# Size of source mod 2**32: 3468 bytes
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, OptionalTunable, TunableVariant
from ui.ui_dialog import UiDialogOk, UiDialogOkCancel
import enum, services

class SituationTravelRequestType(enum.Int):
    ALLOW = ...
    CAREER_EVENT = ...
    DISALLOW = ...


class _SituationTravelRequestDisallow(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'dialog': OptionalTunable(description='\n            If enabled, show a dialog informing the player of the travel\n            prohibition. If disabled, silently fail.\n            ',
                 tunable=UiDialogOk.TunableFactory(description='\n                The dialog to show when an incoming request is denied.\n                '))}

    def __call__(self, user_facing_situation, travel_situation_type, travel_request_fn, **kwargs):
        if self.dialog is not None:
            dialog = self.dialog(services.active_sim_info())
            dialog.show_dialog()

    @property
    def restrict(self):
        return SituationTravelRequestType.DISALLOW


class _SituationTravelRequestAllow(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'dialog': OptionalTunable(description='\n            If enabled, display a prompt requiring player confirmation. If\n            disabled, immediately end this situation and allow the travel\n            request to go through.\n            ',
                 tunable=(UiDialogOkCancel.TunableFactory()))}

    def __call__(self, user_facing_situation, travel_situation_type, travel_request_fn, **kwargs):
        if self.dialog is None:
            return travel_request_fn()

        def on_response(dialog):
            if dialog.accepted:
                travel_request_fn()

        dialog = self.dialog(services.active_sim_info())
        dialog.show_dialog(on_response=on_response)

    @property
    def restrict(self):
        return SituationTravelRequestType.ALLOW


class TunableSituationTravelRequestBehaviorVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, disallow=_SituationTravelRequestDisallow.TunableFactory(), 
         allow=_SituationTravelRequestAllow.TunableFactory(), 
         default='disallow', **kwargs)