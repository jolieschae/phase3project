# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\visualization\transition_constraint_visualizer.py
# Compiled at: 2013-03-14 17:25:45
# Size of source mod 2**32: 1461 bytes
from debugvis import Context
from sims4.color import pseudo_random_color
from visualization.constraint_visualizer import _draw_constraint
import services

class TransitionConstraintVisualizer:

    def __init__(self, layer):
        self.layer = layer
        self._start()

    def _start(self):
        zone = services.current_zone()
        zone.on_transition_constraint_history_changed.append(self._on_transition_constraints_changed)
        self._on_transition_constraints_changed(zone.transition_constraint_history)

    def stop(self):
        services.current_zone().on_transition_constraint_history_changed.remove(self._on_transition_constraints_changed)

    def _on_transition_constraints_changed(self, constraint_history):
        with Context(self.layer) as (layer):
            for constraint in constraint_history:
                color = pseudo_random_color(id(constraint))
                _draw_constraint(layer, constraint, color)