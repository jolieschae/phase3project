# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\celebrity_fans\fan_zone_director_mixin.py
# Compiled at: 2018-08-16 18:37:07
# Size of source mod 2**32: 3003 bytes
from celebrity_fans.fan_situation_manager import FanSituationManager
from celebrity_fans.fan_tuning import FanTuning
from sims4.tuning.tunable import OptionalTunable
import sims4.log, services
logger = sims4.log.Logger('FanZoneDirectorMixin', default_owner='jdimailig')

class FanZoneDirectorMixin:
    INSTANCE_TUNABLES = {'fan_situation_support': OptionalTunable(description='\n            If enabled, the zone director will track celebrities and try to\n            spawn fan and stan situations. \n            ',
                                tunable=(FanSituationManager.TunableFactory()),
                                tuning_group='Fans')}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._fan_situations_manager = None

    def on_startup(self):
        super().on_startup()
        if not FanTuning.are_fans_supported:
            return
        elif self.fan_situation_support is not None:
            self._fan_situations_manager = self.fan_situation_support()
        else:
            situation_manager = services.get_zone_situation_manager()
            fan_situations = situation_manager.get_situations_by_tags(set((FanTuning.FAN_SITUATION_TAG,)))
            for fan_situation in fan_situations:
                situation_manager.destroy_situation_by_id(fan_situation.id)

    def on_loading_screen_animation_finished(self):
        super().on_loading_screen_animation_finished()
        if self._fan_situations_manager is not None:
            self._fan_situations_manager.request_situations()

    def on_shutdown(self):
        if self._fan_situations_manager is not None:
            self._fan_situations_manager.on_destroy()
            self._fan_situations_manager = None
        super().on_shutdown()

    def _save_custom_zone_director(self, zone_director_proto, writer):
        super()._save_custom_zone_director(zone_director_proto, writer)
        if self._fan_situations_manager is not None:
            self._fan_situations_manager.save_fan_situations(writer)

    def _load_custom_zone_director(self, zone_director_proto, reader):
        if self._fan_situations_manager is not None:
            self._fan_situations_manager.load_fan_situations(reader)
        super()._load_custom_zone_director(zone_director_proto, reader)