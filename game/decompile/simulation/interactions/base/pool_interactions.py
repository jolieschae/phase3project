# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\base\pool_interactions.py
# Compiled at: 2019-01-25 19:35:35
# Size of source mod 2**32: 3842 bytes
from event_testing.results import TestResult
from interactions.constraints import create_constraint_set, OceanStartLocationConstraint, WaterDepthIntervals, ANYWHERE
from interactions.social.social_super_interaction import SocialSuperInteraction
from objects.pools import pool_utils
from routing import SurfaceType
from sims4.tuning.tunable import TunableRange
from sims4.utils import flexmethod
from terrain import get_water_depth
import build_buy, routing, sims4

class PoolEdgeSocialInteraction(SocialSuperInteraction):
    INSTANCE_TUNABLES = {'edge_constraint_width': TunableRange(description='\n            Constraint size around the edge of the pool where the sims will\n            go to.\n            ',
                                tunable_type=float,
                                default=2.0,
                                minimum=0.5,
                                maximum=5.0)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._edge_constraint = None

    @classmethod
    def _test(cls, target, context, **kwargs):
        if context.pick is None:
            return TestResult(False, 'Pool edge social has no picked location.')
        else:
            position = context.pick.location
            surface = context.pick.routing_surface
            routing_location = routing.Location(position, sims4.math.Quaternion.IDENTITY(), surface)
            return routing.test_connectivity_permissions_for_handle(routing.connectivity.Handle(routing_location), context.sim.routing_context) or TestResult(False, 'Cannot build constraint over an unroutable area.')
        return (super()._test)(target, context, **kwargs)

    @flexmethod
    def constraint_gen(cls, inst, sim, target, participant_type, *args, **kwargs):
        if inst is not None:
            if inst._edge_constraint is not None:
                yield inst._edge_constraint
                return
        else:
            inst_or_cls = cls if inst is None else inst
            pick_position = inst_or_cls.context.pick
            if pick_position is None:
                pick_position = target.position
            else:
                pick_position = pick_position.location
        pool_block_id = build_buy.get_block_id(sim.zone_id, pick_position, inst_or_cls.context.pick.level - 1)
        if pool_block_id == 0:
            if inst_or_cls.context.pick.routing_surface.type == SurfaceType.SURFACETYPE_POOL:
                if get_water_depth(sim.position.x, sim.position.z, sim.level) > 0:
                    pool_edge_constraints = ANYWHERE
                else:
                    pool_edge_constraints = OceanStartLocationConstraint.create_simple_constraint(WaterDepthIntervals.WET, 1, sim, target)
            else:
                return
        else:
            pool = pool_utils.get_pool_by_block_id(pool_block_id)
            if pool is None:
                return
            pool_edge_constraints = pool.get_edge_constraint(constraint_width=(inst_or_cls.edge_constraint_width), inward_dir=False,
              return_constraint_list=True,
              los_reference_point=pick_position)
        constraint_set = create_constraint_set(pool_edge_constraints)
        if inst is not None:
            inst._edge_constraint = constraint_set
        yield constraint_set