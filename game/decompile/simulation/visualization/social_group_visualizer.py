# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\visualization\social_group_visualizer.py
# Compiled at: 2015-11-18 20:03:00
# Size of source mod 2**32: 3349 bytes
from debugvis import Context
from sims4.color import pseudo_random_color, Color
from socials.jig_group import JigGroup
import sims4.color

class SocialGroupVisualizer:

    def __init__(self, sim, layer):
        self.sim = sim
        self.layer = layer
        self.start()

    def start(self):
        if self._on_social_group_changed not in self.sim.on_social_geometry_changed:
            self.sim.on_social_geometry_changed.append(self._on_social_group_changed)
        self._on_social_group_changed()

    def stop(self):
        if self._on_social_group_changed in self.sim.on_social_geometry_changed:
            self.sim.on_social_geometry_changed.remove(self._on_social_group_changed)
        self._on_social_group_changed()

    def redraw(self, sim):
        with Context((self.layer), altitude=0.1) as (layer):
            for group in sim.get_groups_for_sim_gen():
                if group is not None:
                    if self.sim in group:
                        if group.geometry:
                            for sim in group:
                                layer.routing_surface = sim.routing_surface
                                geometry = group.geometry.get(sim, None)
                                if geometry is not None:
                                    color = pseudo_random_color(sim.id)
                                    layer.add_polygon((geometry.field), color=color)
                                    layer.add_point((geometry.focus), color=color)
                                    layer.add_arrow_for_transform((sim.transform), color=color, altitude=0.05)

                            layer.routing_surface = group.routing_surface
                            color = pseudo_random_color(id(group))
                            layer.add_polygon((group.geometry.field), color=color, altitude=0.125)
                            layer.add_point((group.geometry.focus), color=color, size=0.2)
                            if group.radius is not None:
                                layer.add_circle((group.geometry.focus), (group.radius), color=color)
                        if group._focus is not None:
                            layer.add_point((group._focus.position), color=(sims4.color.Color.CYAN))
                        if isinstance(group, JigGroup):
                            if group.jig_polygon is not None:
                                color = pseudo_random_color(id(group))
                                layer.add_polygon((group.jig_polygon), color=color, altitude=0.125)
                    for index, sim in enumerate(group):
                        for i in range(index):
                            layer.add_point((sim.position), altitude=(2 + i * 0.15), size=0.025, color=(Color.RED))

    def _on_social_group_changed(self, *args, **kwargs):
        self.redraw(self.sim)