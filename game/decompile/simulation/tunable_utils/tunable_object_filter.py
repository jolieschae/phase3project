# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\tunable_utils\tunable_object_filter.py
# Compiled at: 2020-10-09 17:02:40
# Size of source mod 2**32: 6178 bytes
import routing, services, sims4.resources
from routing import SurfaceType
from routing.portals.portal_tuning import PortalFlags
from sims4.tuning.tunable import TunableVariant, HasTunableSingletonFactory, AutoFactoryInit, TunableSet, TunableEnumEntry, TunableEnumFlags, TunableReference
from tag import Tag
from tunable_utils.tunable_whitelist import TunableWhitelist

class TunableObjectFilterVariant(TunableVariant):

    class _FilterByTags(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'tags': TunableSet(description='\n                The object must have any of these tags in order to satisfy the\n                requirement.\n                ',
                   tunable=TunableEnumEntry(tunable_type=Tag,
                   default=(Tag.INVALID),
                   invalid_enums=(
                  Tag.INVALID,),
                   pack_safe=True),
                   minlength=1)}

        def is_object_valid(self, obj, **kwargs):
            if not hasattr(obj, 'has_any_tag'):
                return False
            else:
                return obj.has_any_tag(self.tags) or False
            return True

    class _FilterBySim(HasTunableSingletonFactory, AutoFactoryInit):

        def is_object_valid(self, obj, **kwargs):
            return obj.is_sim

    class _FilterByTerrain(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'disallowed_surfaces': TunableSet(description='\n                Routing surfaces where the placement of this object should\n                fail.\n                ',
                                  tunable=TunableEnumEntry(tunable_type=SurfaceType,
                                  default=(SurfaceType.SURFACETYPE_POOL),
                                  invalid_enums=(
                                 SurfaceType.SURFACETYPE_UNKNOWN,)))}

        def is_object_valid(self, obj, sim=None):
            if not obj.is_terrain:
                return False
            else:
                routing_surface = obj.routing_surface
                if routing_surface.type in self.disallowed_surfaces:
                    return False
                if not routing.test_point_placement_in_navmesh(routing_surface, obj.position):
                    return False
                if sim is not None:
                    return routing.test_connectivity_permissions_for_handle(routing.connectivity.Handle(obj.position, obj.routing_surface), sim.routing_context) or False
            return True

    class _FilterByPortalFlags(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'portal_flags': TunableEnumFlags(description='\n                The object must have any of these portal flags in order to\n                satisfy the requirement.\n                ',
                           enum_type=PortalFlags)}

        def is_object_valid(self, obj, **kwargs):
            if getattr(obj, 'parts', None):
                return any((self.is_object_valid(part.part_definition) for part in obj.parts))
            surface_portal_constraint = getattr(obj, 'surface_portal_constraint', None)
            if surface_portal_constraint is None:
                return False
            if surface_portal_constraint.required_portal_flags is None:
                return False
            return surface_portal_constraint.required_portal_flags & self.portal_flags

    class _FilterByState(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'states': TunableWhitelist(description='\n                The required states to pass this test.\n                ',
                     tunable=TunableReference(description='\n                    The state value.\n                    ',
                     manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
                     class_restrictions=('ObjectStateValue', ),
                     pack_safe=True))}

        def is_object_valid(self, obj, **kwargs):
            if obj.state_component is None:
                return False
            return self.states.test_collection(set(obj.state_component.values()))

    class _FilterAllowAll(HasTunableSingletonFactory, AutoFactoryInit):

        def is_object_valid(self, obj, **kwargs):
            return True

    FILTER_ALL = 'allow_all'
    FILTER_SIM = 'filter_by_sim'

    def __init__(self, *args, default=FILTER_SIM, **kwargs):
        (super().__init__)(args, filter_by_sim=TunableObjectFilterVariant._FilterBySim.TunableFactory(), 
         filter_by_tags=TunableObjectFilterVariant._FilterByTags.TunableFactory(), 
         filter_by_terrain=TunableObjectFilterVariant._FilterByTerrain.TunableFactory(), 
         filter_by_portal_flags=TunableObjectFilterVariant._FilterByPortalFlags.TunableFactory(), 
         filter_by_state=TunableObjectFilterVariant._FilterByState.TunableFactory(), 
         allow_all=TunableObjectFilterVariant._FilterAllowAll.TunableFactory(), 
         default=default, **kwargs)