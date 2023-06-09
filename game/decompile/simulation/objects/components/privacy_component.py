# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\privacy_component.py
# Compiled at: 2018-11-30 15:44:19
# Size of source mod 2**32: 2114 bytes
from interactions.privacy import TunablePrivacySnippet
from objects.components import Component
from objects.components.types import PRIVACY_COMPONENT
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit
import sims4.log
logger = sims4.log.Logger('Privacy Component', default_owner='jdimailig')

class PrivacyComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=PRIVACY_COMPONENT):
    FACTORY_TUNABLES = {'privacy_settings': TunablePrivacySnippet(description='\n            The privacy region to start up.\n            ')}

    def __init__(self, owner, *args, **kwargs):
        (super().__init__)(owner, *args, **kwargs)
        self._privacy_instance = self.privacy_settings(central_object=(self.owner), add_to_privacy_service=False, persistent_instance=True)

    def on_finalize_load(self):
        if self.owner.is_in_inventory():
            return
        self._privacy_instance.build_privacy()
        self._privacy_instance.add_privacy()

    def on_add(self, *_, **__):
        if self.owner.is_in_inventory():
            return
        self._privacy_instance.build_privacy()
        self._privacy_instance.add_privacy()

    def on_remove(self, *_, **__):
        if self.owner.is_in_inventory():
            return
        self._privacy_instance.remove_privacy()

    def on_added_to_inventory(self):
        self._privacy_instance.remove_privacy()

    def on_removed_from_inventory(self):
        self._privacy_instance.build_privacy()
        self._privacy_instance.add_privacy()

    def on_location_changed(self, *_, **__):
        if self.owner.is_in_inventory():
            return
        self._privacy_instance.build_privacy()