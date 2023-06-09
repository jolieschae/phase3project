# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\vfx\vfx_mask.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 2846 bytes
from distributor.system import Distributor
import distributor, enum, sims4
logger = sims4.log.Logger('VFXMask', default_owner='camilogarcia')

class VFXMask(enum.IntFlags):
    MASK_BABY = 1
    MASK_TODDLER = 2
    MASK_CHILD = 4
    MASK_TEEN = 8
    MASK_YOUNGADULT = 16
    MASK_ADULT = 32
    MASK_ELDER = 64
    MASK_SKILL_LEVEL_1 = 128
    MASK_SKILL_LEVEL_2 = 256
    MASK_SKILL_LEVEL_3 = 512
    MASK_SKILL_LEVEL_4 = 1024
    MASK_SKILL_LEVEL_5 = 2048
    MASK_DREAM_BIG = 4096
    MASK_VAMPIRE = 8192
    MASK_PARENTING_SKILL = 16384
    MASK_CURSED = 32768
    MASK_SKILL_LEVEL_HIGH = 65536
    MASK_WITCH_MOTES = 131072
    MASK_SECRET_SOCIETY = 262144
    MASK_SPRITE_LOW = 524288
    MASK_SPRITE_MEDIUM = 1048576
    MASK_SPRITE_HIGH = 2097152
    MASK_WEREWOLF = 4194304


class ExcludeVFXMask(enum.IntFlags):
    MASK_PHOTOGRAPHY = 1
    MASK_MISSION = 2


def notify_client_mask_update(new_active_sim_info):
    if new_active_sim_info is None:
        return
    vfx_mask = new_active_sim_info.trait_tracker.trait_vfx_mask
    if vfx_mask:
        generate_mask_message(vfx_mask, new_active_sim_info)
    exclude_vfx_mask = new_active_sim_info.trait_tracker.trait_exclude_vfx_mask
    if exclude_vfx_mask:
        generate_mask_message(exclude_vfx_mask, new_active_sim_info, exclude=True)


def generate_mask_message(mask, owner, exclude=False):
    if exclude:
        mask_message = distributor.ops.SetExcludeVFXMask(mask)
    else:
        mask_message = distributor.ops.SetVFXMask(mask)
    distributor_system = Distributor.instance()
    distributor_system.add_op(owner, mask_message)