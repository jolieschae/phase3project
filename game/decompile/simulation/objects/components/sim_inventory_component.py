# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\sim_inventory_component.py
# Compiled at: 2020-03-02 21:25:50
# Size of source mod 2**32: 12283 bytes
import weakref
from protocolbuffers import FileSerialization_pb2, SimObjectAttributes_pb2
import sims4.log
from animation.posture_manifest_constants import STAND_OR_SIT_CONSTRAINT
from interactions.constraints import Constraint
from objects.components import componentmethod, types
from objects.components.inventory import InventoryComponent
from objects.components.inventory_enums import InventoryType
from objects.components.inventory_item import InventoryItemComponent
from objects.mixins import InventoryProvidedAfforanceData, AffordanceCacheMixin
from objects.object_enums import ItemLocation
from postures.posture_state_spec import create_body_posture_state_spec
from sims.sim_info_types import Species
import services
from singletons import EMPTY_SET
logger = sims4.log.Logger('Inventory', default_owner='tingyul')

class SimInventoryComponent(InventoryComponent, AffordanceCacheMixin, component_name=types.INVENTORY_COMPONENT):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._shelved_objects = None
        self._object_providing_affordances = None
        self._vehicle_objects = None

    @property
    def inventory_type(self):
        return InventoryType.SIM

    @property
    def default_item_location(self):
        return ItemLocation.SIM_INVENTORY

    @componentmethod
    def get_inventory_access_constraint(self, sim, is_put, carry_target, use_owner_as_target_for_resolver=False):
        carry_posture = self.owner.posture_state.get_carry_posture(carry_target)
        if carry_posture is not None:
            posture_manifest = carry_posture.get_provided_postures(species=(sim.species))
            if sim.species != Species.DOG:
                posture_manifest = posture_manifest.__class__((e for e in posture_manifest if e.specific != 'swim'))
            posture_manifest = posture_manifest.replace_actor(for_actor=(self.owner))
            posture_state_spec = create_body_posture_state_spec(posture_manifest)
            return Constraint(posture_state_spec=posture_state_spec)
        return STAND_OR_SIT_CONSTRAINT

    @componentmethod
    def get_inventory_access_animation(self, *args, **kwargs):
        pass

    def can_add(self, obj, hidden=False):
        if self.owner.sim_info.is_pet:
            return False
        return super().can_add(obj, hidden=hidden)

    @property
    def allow_ui(self):
        return self.owner.household is services.active_household()

    def should_save_parented_item_to_inventory(self, obj):
        return self.can_add(obj) and self.owner.household.id == obj.get_household_owner_id()

    def get_shelved_object_count(self):
        if self._shelved_objects:
            return len(self._shelved_objects.objects)
        return 0

    def get_shelved_object_data(self):
        if self._shelved_objects is None:
            return EMPTY_SET
        shelved = []
        persist_data_protocol = SimObjectAttributes_pb2.PersistableInventoryItemComponent.persistable_data
        for object_data in self._shelved_objects.objects:
            save_data = SimObjectAttributes_pb2.PersistenceMaster()
            save_data.ParseFromString(object_data.attributes)
            stack_count = -1
            for persist_data in save_data.data:
                if persist_data.type != persist_data.InventoryItemComponent:
                    continue
                item_data = persist_data.Extensions[persist_data_protocol]
                stack_count = item_data.stack_count

            shelved.append({'guid':object_data.guid, 
             'objectCount':stack_count})

        return tuple(shelved)

    def _on_save_items(self, object_list):
        if self._shelved_objects is None:
            return
        else:
            return self.owner.is_player_sim or None
        logger.info('Merging Inventory {} (size: {}) with saved inventory {}.', self, len(self), self.get_shelved_object_count())
        for shelved_obj in self._shelved_objects.objects:
            object_list.objects.append(shelved_obj)

    def _on_load_items(self):
        logger.info('Loaded {}. #Created: {}. #Shelved: {}.', self, len(self), self.get_shelved_object_count())

    def _load_item(self, definition_id, obj_data):
        if self._should_create_object(definition_id):
            self._create_inventory_object(definition_id, obj_data)
        else:
            if self._shelved_objects is None:
                self._shelved_objects = FileSerialization_pb2.ObjectList()
            self._shelved_objects.objects.append(obj_data)

    def _update_provided_affordances(self, obj):
        provided_affordances = []
        obj_id = obj.id
        for provided_affordance in obj.inventoryitem_component.target_super_affordances:
            provided_affordance_data = InventoryProvidedAfforanceData(provided_affordance.affordance, provided_affordance.object_filter, provided_affordance.allow_self, obj_id)
            provided_affordances.append(provided_affordance_data)

        self.add_to_affordance_caches(obj.inventoryitem_component.super_affordances, provided_affordances)

    @componentmethod
    def get_super_affordance_availability_gen(self):
        yield from self.get_cached_super_affordances_gen()
        if False:
            yield None

    @componentmethod
    def get_target_provided_affordances_data_gen(self):
        yield from self.get_cached_target_provided_affordances_data_gen()
        if False:
            yield None

    def get_provided_super_affordances(self):
        affordances, target_affordances = set(), list()
        if self._object_providing_affordances is not None:
            for obj in self._object_providing_affordances:
                affordances.update(obj.inventoryitem_component.super_affordances)
                for provided_affordance in obj.inventoryitem_component.target_super_affordances:
                    provided_affordance_data = InventoryProvidedAfforanceData(provided_affordance.affordance, provided_affordance.object_filter, provided_affordance.allow_self, obj.id)
                    target_affordances.append(provided_affordance_data)

        return (
         affordances, target_affordances)

    def get_sim_info_from_provider(self):
        return self.owner.sim_info

    def add_affordance_provider_object(self, obj):
        if self._object_providing_affordances is None:
            self._object_providing_affordances = weakref.WeakSet()
        self._object_providing_affordances.add(obj)
        self._update_provided_affordances(obj)

    def remove_affordance_provider_object(self, obj):
        if self._object_providing_affordances is not None:
            self._object_providing_affordances.remove(obj)
            if not self._object_providing_affordances:
                self._object_providing_affordances = None
            self.update_affordance_caches()

    def vehicle_objects_gen(self):
        if self._vehicle_objects is not None:
            yield from self._vehicle_objects
        if False:
            yield None

    def add_vehicle_object(self, obj):
        if self._vehicle_objects is None:
            self._vehicle_objects = weakref.WeakSet()
        self._vehicle_objects.add(obj)

    def remove_vehicle_object(self, obj):
        if self._vehicle_objects is not None:
            self._vehicle_objects.remove(obj)
            if not self._vehicle_objects:
                self._vehicle_objects = None

    def _should_create_object(self, definition_id):
        if self.owner.household.id == services.active_household_id():
            return services.inventory_manager().is_inventory_item_available(services.definition_manager().get(definition_id))
        if InventoryItemComponent.should_item_be_removed_from_inventory(definition_id):
            return False
        return True