# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\broadcasters\environment_score\environment_score_mixin.py
# Compiled at: 2020-04-09 19:54:52
# Size of source mod 2**32: 16644 bytes
from collections import Counter
import operator, weakref
from broadcasters.environment_score.environment_score_tuning import EnvironmentScoreTuning
import alarms, clock, gsi_handlers, services, sims4.log, sims4.reload
logger = sims4.log.Logger('Environment Score')
with sims4.reload.protected(globals()):
    environment_score_enabled = True
    environment_score_mood_commodities = []

def _initialize_environment_score_commodities(instance_manager=None):
    global environment_score_mood_commodities
    if instance_manager is None:
        instance_manager = services.get_instance_manager(sims4.resources.Types.MOOD)
    environment_score_mood_commodities = []
    for mood in instance_manager.types.values():
        if mood.environment_scoring_commodity is not None:
            environment_score_mood_commodities.append(mood.environment_scoring_commodity)


if not sims4.reload.currently_reloading:
    services.get_instance_manager(sims4.resources.Types.MOOD).add_on_load_complete(_initialize_environment_score_commodities)

class EnvironmentScoreMixin:

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._environment_score_commodity = None
        self._environment_score_broadcasters = weakref.WeakSet()
        self._environment_score_alarm_handle = None
        self._dirty = True

    def add_environment_score_broadcaster(self, broadcaster):
        self._remove_linked_broadcasters(broadcaster)
        self._environment_score_broadcasters.add(broadcaster)
        self._dirty = True
        self.schedule_environment_score_update()

    def _remove_linked_broadcasters(self, broadcaster):
        for linked_broadcaster in broadcaster.get_linked_broadcasters_gen():
            self._environment_score_broadcasters.discard(linked_broadcaster)

    def remove_environment_score_broadcaster(self, broadcaster):
        self._environment_score_broadcasters.discard(broadcaster)
        self._dirty = True
        self.schedule_environment_score_update()

    def _start_environment_score(self):
        self._clear_environment_score()
        self._dirty = True
        self.schedule_environment_score_update()

    def _stop_environment_score(self):
        self._clear_environment_score()
        self._dirty = True

    def on_build_objects_environment_score_update(self):
        self._dirty = True
        self.schedule_environment_score_update(force_run=True)

    def _get_build_objects_environment_score(self):
        negative_value = 0
        positive_value = 0
        if not services.get_zone_modifier_service().is_build_eco_effects_enabled:
            return (
             negative_value, positive_value)
        lot = services.current_zone().lot
        negative_stat_type = EnvironmentScoreTuning.BUILD_OBJECTS_ENVIRONMENT_SCORING.negative_environment_scoring
        negative_stat_tracker = lot.get_tracker(negative_stat_type)
        if negative_stat_tracker is not None:
            negative_value = negative_stat_tracker.get_value(negative_stat_type)
        positive_stat_type = EnvironmentScoreTuning.BUILD_OBJECTS_ENVIRONMENT_SCORING.positive_environment_scoring
        positive_stat_tracker = lot.get_tracker(positive_stat_type)
        if positive_stat_tracker is not None:
            positive_value = positive_stat_tracker.get_value(positive_stat_type)
        return (negative_value, positive_value)

    def _get_broadcasting_environment_score_objects_gen(self):
        for broadcaster in self._environment_score_broadcasters:
            if broadcaster.broadcasting_object is not None:
                yield broadcaster.broadcasting_object
            for linked_broadcaster in broadcaster.get_linked_broadcasters_gen():
                if linked_broadcaster.broadcasting_object is not None:
                    yield linked_broadcaster.broadcasting_object

    def schedule_environment_score_update(self, force_run=False):

        def _update_environment_score_callback(timeline):
            if not force_run:
                if self.queue is not None:
                    if self.transition_controller is not None:
                        self._environment_score_alarm_handle = None
                        return
            self._update_environment_score()

        if self._environment_score_alarm_handle is not None:
            if force_run:
                alarms.cancel_alarm(self._environment_score_alarm_handle)
                self._environment_score_alarm_handle = None
        if self._environment_score_alarm_handle is None:
            self._environment_score_alarm_handle = alarms.add_alarm(self, (clock.interval_in_real_seconds(1.0)),
              _update_environment_score_callback,
              repeating=False)

    def _update_mood_commodities(self, total_mood_scores):
        current_mood_commodity = self._environment_score_commodity
        largest_mood = None
        if total_mood_scores:
            largest_mood = total_mood_scores.most_common(1)[0][0]
        elif largest_mood is not None:
            self._environment_score_commodity = largest_mood.environment_scoring_commodity
            if self._environment_score_commodity is not None:
                new_value = total_mood_scores.get(largest_mood, 0)
                if self._environment_score_commodity is current_mood_commodity:
                    if self.commodity_tracker.get_value(self._environment_score_commodity) != new_value:
                        self.commodity_tracker.set_value(self._environment_score_commodity, new_value)
                else:
                    self.commodity_tracker.remove_statistic(current_mood_commodity)
                    self.commodity_tracker.add_statistic(self._environment_score_commodity)
                    self.commodity_tracker.set_value(self._environment_score_commodity, new_value)
            else:
                logger.error('Environment Scoring: {} has no commodity set for environment scoring.', largest_mood, owner='rmccord')
        elif current_mood_commodity is not None:
            self.commodity_tracker.remove_statistic(current_mood_commodity)
        return largest_mood

    def _update_positive_and_negative_commodities(self, negative_score, positive_score):
        negative_stat = self.commodity_tracker.get_statistic((EnvironmentScoreTuning.NEGATIVE_ENVIRONMENT_SCORING), add=True)
        positive_stat = self.commodity_tracker.get_statistic((EnvironmentScoreTuning.POSITIVE_ENVIRONMENT_SCORING), add=True)
        contribute_positive_scoring = True
        if negative_stat is not None:
            if negative_stat.get_value() != negative_score:
                negative_stat.set_value(negative_score)
            if negative_stat.buff_handle is not None:
                contribute_positive_scoring = False
        elif positive_stat is not None:
            if contribute_positive_scoring and positive_stat.get_value() != positive_score:
                positive_stat.set_value(positive_score)
            else:
                if not contribute_positive_scoring:
                    positive_stat.set_value(0)

    def _update_environment_score(self):
        try:
            if not self._dirty:
                return
            else:
                if not environment_score_enabled or self.is_hidden():
                    self._clear_environment_score()
                    return
                total_mood_scores = Counter()
                total_negative_score = 0
                total_positive_score = 0
                build_objs_negative_score, build_objs_positive_score = self._get_build_objects_environment_score()
                total_negative_score += build_objs_negative_score
                total_positive_score += build_objs_positive_score
                if gsi_handlers.sim_handlers_log.environment_score_archiver.enabled:
                    contributing_objects = []
                    object_contributions = []
                environment_score_objects = set(self._get_broadcasting_environment_score_objects_gen())
                for obj in environment_score_objects:
                    mood_scores, negative_score, positive_score, contributions = obj.get_environment_score(self)
                    total_negative_score += negative_score
                    total_positive_score += positive_score
                    total_mood_scores.update(mood_scores)
                    if gsi_handlers.sim_handlers_log.environment_score_archiver.enabled:
                        if sum(mood_scores.values()) != 0 or negative_score != 0 or positive_score != 0:
                            contributing_objects.append((obj, mood_scores, negative_score, positive_score))
                            object_contributions.extend(contributions)

                self._update_positive_and_negative_commodities(total_negative_score, total_positive_score)
                largest_mood = self._update_mood_commodities(total_mood_scores)
                if not gsi_handlers.sim_handlers_log.environment_score_archiver.enabled or contributing_objects or total_negative_score != 0 or total_positive_score != 0:
                    gsi_handlers.sim_handlers_log.log_environment_score(self.id, largest_mood, total_mood_scores.get(largest_mood, 0), self._environment_score_commodity, total_negative_score, EnvironmentScoreTuning.NEGATIVE_ENVIRONMENT_SCORING, total_positive_score, EnvironmentScoreTuning.POSITIVE_ENVIRONMENT_SCORING, contributing_objects, object_contributions)
            self._dirty = False
        finally:
            self._environment_score_alarm_handle = None

    def _clear_environment_score(self):
        for commodity in environment_score_mood_commodities:
            if self.commodity_tracker.has_statistic(commodity):
                self.commodity_tracker.remove_statistic(commodity)

        self._environment_score_broadcasters.clear()
        self._environment_score_commodity = None
        if self.commodity_tracker.has_statistic(EnvironmentScoreTuning.NEGATIVE_ENVIRONMENT_SCORING):
            self.commodity_tracker.remove_statistic(EnvironmentScoreTuning.NEGATIVE_ENVIRONMENT_SCORING)
        if self.commodity_tracker.has_statistic(EnvironmentScoreTuning.POSITIVE_ENVIRONMENT_SCORING):
            self.commodity_tracker.remove_statistic(EnvironmentScoreTuning.POSITIVE_ENVIRONMENT_SCORING)
        if self._environment_score_alarm_handle is not None:
            alarms.cancel_alarm(self._environment_score_alarm_handle)
            self._environment_score_alarm_handle = None