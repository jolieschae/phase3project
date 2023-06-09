# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\placement_commands.py
# Compiled at: 2020-03-05 21:08:01
# Size of source mod 2**32: 5982 bytes
from build_buy import get_object_slotset, test_location_for_object, get_object_buy_category_flags, BuyCategory
from carry.carry_utils import get_carried_objects_gen
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target
from sims4.math import Location, Transform
import objects.system, routing, services, sims4.commands, sims4.math

@sims4.commands.Command('placement.in_navmesh')
def in_navmesh_cmd(obj_id: int, _connection=None):
    obj = objects.system.find_object(obj_id)
    if obj is not None:
        if obj.is_in_navmesh:
            sims4.commands.output('Object is in NavMesh', _connection)
        else:
            sims4.commands.output('Object is not in NavMesh', _connection)
    else:
        sims4.commands.output('ObjectID is not valid.', _connection)


@sims4.commands.Command('placement.output_slot_set')
def output_slot_set(obj_id: int, _connection=None):
    obj = objects.system.find_object(obj_id)
    if obj is None:
        sims4.commands.output('Invalid object id', _connection)
        return False
    key = get_object_slotset(obj.definition.id)
    if key is None:
        sims4.commands.output('Object does not have a slot set defined', _connection)
        return False
    sims4.commands.output('Slot set key: {}'.format(key), _connection)
    return True


@sims4.commands.Command('placement.category_flags')
def output_category_flags(obj_id: int, _connection=None):
    obj = objects.system.find_object(obj_id)
    if obj is None:
        sims4.commands.output('Invalid object id', _connection)
        return False
    buy_category_flags = get_object_buy_category_flags(obj.definition.id)
    sims4.commands.output('\tBuy category flags: {}\n'.format(BuyCategory(buy_category_flags)), _connection)
    return True


@sims4.commands.Command('placement.test_placement')
def test_placement(obj_id, x, y, z, rotation, level, parent_obj_id, parent_slot_hash, _connection=None):
    output = sims4.commands.Output(_connection)
    obj = objects.system.find_object(obj_id)
    if obj is None:
        output('Invalid object id')
        return False
    else:
        zone_id = services.current_zone_id()
        surface = routing.SurfaceIdentifier(zone_id, level, routing.SurfaceType.SURFACETYPE_WORLD)
        position = sims4.math.Vector3(x, y, z)
        orientation = sims4.math.angle_to_yaw_quaternion(rotation)
        parent_obj = objects.system.find_object(parent_obj_id)
        transform = Transform(position, orientation)
        location = Location(transform, surface, parent_obj, parent_slot_hash, parent_slot_hash)
        result, errors = test_location_for_object(obj, location=location)
        if result:
            output('Placement is legal')
        else:
            output('Placement is NOT legal')
    if errors:
        for code, msg in errors:
            output('  {} ({})'.format(msg, code))

    return result


@sims4.commands.Command('placement.test_current_placement')
def test_current_placement(obj_id: int, _connection=None):
    output = sims4.commands.Output(_connection)
    obj = objects.system.find_object(obj_id)
    if obj is None:
        output('Invalid object id')
        return False
    else:
        args = (
         obj.id,
         obj.location.transform.translation.x,
         obj.location.transform.translation.y,
         obj.location.transform.translation.z,
         0,
         obj.location.level,
         obj.parent.id if obj.parent is not None else 0,
         obj.location.joint_name_or_hash or obj.location.slot_hash)
        output(('|placement.test_placement {} {} {} {} {} {} {} {}'.format)(*args))
        result, errors = test_location_for_object(obj)
        if result:
            output('Placement is legal')
        else:
            output('Placement is NOT legal')
    if errors:
        for code, msg in errors:
            output('  {} ({})'.format(msg, code))

    return result


@sims4.commands.Command('placement.has_floor')
def has_floor(x, y, z, level, _connection=None):
    position = sims4.math.Vector3(x, y, z)
    from build_buy import has_floor_at_location
    if has_floor_at_location(position, level):
        sims4.commands.output('Floor exists at location', _connection)
        return True
    sims4.commands.output('Floor does not exist at location', _connection)
    return False


@sims4.commands.Command('carry.get_carried_objects')
def get_carried_objects(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('Invalid Sim id: {}'.format(opt_sim), _connection)
        return False
    for hand, _, obj in get_carried_objects_gen(sim):
        sims4.commands.output('\t{}: {}'.format(hand, obj), _connection)

    return True