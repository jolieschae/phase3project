# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\lighting_commands.py
# Compiled at: 2020-04-29 13:47:24
# Size of source mod 2**32: 4418 bytes
from build_buy import get_room_id
from objects.components.lighting_component import LightingComponent
from objects.components.types import LIGHTING_COMPONENT
from objects.lighting.lighting_dialog import UiDialogLightColorAndIntensity
from objects.lighting.lighting_utils import all_lights_gen, lights_in_target_room_gen
import services, sims4.color, sims4.commands

@sims4.commands.Command('lighting.set_color_and_intensity', command_type=(sims4.commands.CommandType.Live))
def set_color_and_intensity(response_id, r=None, g=None, b=None, intensity=1.0, _connection=None):
    ui_dialog_service = services.ui_dialog_service()
    if ui_dialog_service is not None:
        dialog = ui_dialog_service.get_dialog(response_id)
        if dialog is not None:
            color = sims4.color.from_rgba_as_int(r, g, b)
            dialog.update_dialog_data(color=color, intensity=intensity)
    return True


def single_light_gen(target):
    yield target


@sims4.commands.Command('lighting.showlighteditor', command_type=(sims4.commands.CommandType.Live))
def show_light_editor(light_object_id: int, light_target_type: int=0, _connection=None):
    light_object = services.object_manager().get(light_object_id)
    if light_object is None:
        sims4.commands.output('Invalid object ID specified. Please try again with a valid object ID.', _connection)
        return
    elif not light_object.has_component(LIGHTING_COMPONENT):
        sims4.commands.output('Specified object {} does not have a lighting component'.foramt(light_object), _connection)
        return
        light_gen = None
        if light_target_type == 0:
            light_gen = single_light_gen
        else:
            if light_target_type == 1:
                light_gen = lights_in_target_room_gen
            else:
                if light_target_type == 2:
                    light_gen = all_lights_gen
                else:
                    sims4.commands.output('Invalid value for light_target_type specified: {}. Expecting a 0 (Current Light), 1 (All Lights in Room of target), or 2 (all lights).'.format(light_target_type), _connection)
                    return

        def _on_update(*, color, intensity):
            if light_gen is not None:
                for light in light_gen(light_object):
                    light.set_user_intensity_override(intensity)
                    light.set_light_color(color)

        color = light_object.get_light_color()
        if color is not None:
            r, g, b, _ = sims4.color.to_rgba_as_int(color)
    else:
        r = g = b = sims4.color.MAX_INT_COLOR_VALUE
    intensity = light_object.get_user_intensity_overrides()
    dialog = UiDialogLightColorAndIntensity(light_object, r, g, b, intensity, on_update=_on_update)
    dialog.show_dialog()


@sims4.commands.Command('lighting.auto_room_light_status', command_type=(sims4.commands.CommandType.Live))
def auto_room_light_status(room_id: int, on: bool, _connection=None):
    zone_id = services.current_zone_id()
    for obj in services.object_manager().get_all_objects_with_component_gen(LIGHTING_COMPONENT):
        if obj.get_light_dimmer_value() != LightingComponent.LIGHT_AUTOMATION_DIMMER_VALUE:
            continue
        obj_room_id = get_room_id(zone_id, obj.position, obj.level)
        if obj_room_id != room_id:
            continue
        obj.on_light_changed(on)