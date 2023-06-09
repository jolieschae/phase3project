# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\animation_sleep_element.py
# Compiled at: 2016-08-18 19:57:13
# Size of source mod 2**32: 3761 bytes
import clock, element_utils, elements
from animation.animation_drift_monitor import build_animation_drift_monitor_sequence

class AnimationSleepElement(elements.SubclassableGeneratorElement):

    def __init__(self, duration_must_run, duration_interrupt, duration_repeat, enable_optional_sleep_time=True, arbs=()):
        if duration_interrupt != 0:
            if duration_repeat != 0:
                raise AssertionError('An animation with both interrupt and repeat duration is not allowed.')
        super().__init__()
        self._duration_must_run = duration_must_run
        self._duration_interrupt = duration_interrupt
        self._duration_repeat = duration_repeat
        self._stop_requested = False
        self.enable_optional_sleep_time = enable_optional_sleep_time
        self._optional_time_elapsed = 0
        self._arbs = arbs

    @classmethod
    def shortname(cls):
        return 'AnimSleep'

    @property
    def arbs(self):
        return tuple(self._arbs)

    @property
    def optional_time_elapsed(self):
        return self._optional_time_elapsed

    def _run_gen(self, timeline):
        if self._duration_must_run > 0:
            sequence = build_animation_drift_monitor_sequence(self, elements.SleepElement(clock.interval_in_real_seconds(self._duration_must_run)))
            yield from element_utils.run_child(timeline, sequence)
        if self._stop_requested:
            return False
            if self._duration_repeat > 0.0:
                while not self._stop_requested:
                    yield from element_utils.run_child(timeline, elements.SleepElement(clock.interval_in_real_seconds(self._duration_repeat)))

        elif self.enable_optional_sleep_time and self._duration_interrupt > 0:
            then = timeline.now
            yield from element_utils.run_child(timeline, elements.SoftSleepElement(clock.interval_in_real_seconds(self._duration_interrupt)))
            now = timeline.now
            self._optional_time_elapsed = (now - then).in_real_world_seconds()
        else:
            yield from element_utils.run_child(timeline, element_utils.sleep_until_next_tick_element())
        return True
        if False:
            yield None

    def _soft_stop(self):
        super()._soft_stop()
        self._stop_requested = True