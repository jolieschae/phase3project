# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\interaction_messages.py
# Compiled at: 2018-08-16 20:22:02
# Size of source mod 2**32: 9948 bytes
from protocolbuffers import Sims_pb2
from protocolbuffers.Consts_pb2 import MSG_SIM_INTERACTIONS_ADD, MSG_SIM_INTERACTIONS_REMOVE, MSG_SIM_INTERACTIONS_REMOVE_ALL, MSG_SIM_INTERACTIONS_UPDATE, MSG_SIM_INTERACTION_QUEUE_VIEW_ADD, MSG_SIM_INTERACTION_REPLACE
from distributor.rollback import ProtocolBufferRollback
from distributor.shared_messages import add_message_if_selectable, build_icon_info_msg, MessageOp, _IconInfoData, IconInfoData
from distributor.system import Distributor
import sims4.log
logger = sims4.log.Logger('InteractionMessages')

def send_interactions_remove_msg(sim, interactions, immediate=False):
    logger.debug('send_interactions_remove_msg({}), immediate={}', sim.id, immediate)
    msg = Sims_pb2.InteractionsRemove()
    if _build_interactions_remove_msg(sim, msg, interactions):
        logger.debug('    SENDING')
        add_message_if_selectable(sim, MSG_SIM_INTERACTIONS_REMOVE, msg, immediate)
    else:
        logger.debug('    NOT_SENDING')


def send_interactions_removeall_msg(sim, immediate=False):
    if sim is None:
        return
    else:
        logger.debug('send_interactions_removeall_msg({}, immediate={})', sim.id, immediate)
        msg = Sims_pb2.InteractionsRemove()
        if _build_interactions_removeall_msg(sim, msg):
            logger.debug('    SENDING')
            add_message_if_selectable(sim, MSG_SIM_INTERACTIONS_REMOVE_ALL, msg, immediate)
        else:
            logger.debug('    NOT_SENDING')


def _build_interactions_remove_msg(sim, msg, interactions):
    logger.debug('  _build_interactions_remove_msg({0})', sim.id)
    msg.sim_id = sim.id
    found_interaction = False
    for int_info in interactions:
        msg.interaction_ids.append(int_info.interaction_id)
        logger.debug('      interaction({0})={1})', int_info.interaction_id, int_info.display_name)
        found_interaction = True

    return found_interaction


def _build_interactions_removeall_msg(sim, msg):
    logger.debug('  _build_interactions_removeall_msg({})', sim.id)
    msg.sim_id = sim.id
    return True


def send_interaction_queue_view_add_msg(sim, super_interactions, immediate=False):
    logger.debug('send_interaction_queue_view_add_msg({}, immediate={}', sim.id, immediate)
    msg = Sims_pb2.InteractionQueueViewAdd()
    if _build_interaction_queue_view_add_msg(sim, super_interactions, msg):
        logger.debug('    SENDING')
        add_message_if_selectable(sim, MSG_SIM_INTERACTION_QUEUE_VIEW_ADD, msg, immediate)
    else:
        logger.debug('    NOT_SENDING')


def send_interaction_replace_message(sim, old_interaction_id, new_interaction_info, immediate=False):
    logger.debug('send_interaction_replace_message({}), old_id={}, new_id={}, immediate={})', sim.id, old_interaction_id, new_interaction_info.interaction_id, immediate)
    msg = Sims_pb2.InteractionReplace()
    msg.sim_id = sim.id
    msg.old_interaction_id = old_interaction_id
    _build_interaction_msg(new_interaction_info, msg.new_interaction)
    logger.debug('    SENDING')
    add_message_if_selectable(sim, MSG_SIM_INTERACTION_REPLACE, msg, immediate)


def send_interactions_update_msg(sim, super_interactions, immediate=False):
    logger.debug('send_interactions_update_msg({}), immediate={}', sim.id, immediate)
    msg = Sims_pb2.InteractionsUpdate()
    if _build_interactions_update_msg(sim, super_interactions, msg):
        logger.debug('    SENDING')
        add_message_if_selectable(sim, MSG_SIM_INTERACTIONS_UPDATE, msg, immediate)
    else:
        logger.debug('    NOT_SENDING')


def _build_interactions_update_msg(sim, super_interactions, msg):
    logger.debug('  _build_interactions_update_msg({0})', sim.id)
    msg.sim_id = sim.id
    if super_interactions:
        for si_interaction in super_interactions:
            with ProtocolBufferRollback(msg.interactions) as (msg_interaction):
                _build_interaction_msg(si_interaction, msg_interaction)

        return True
    return False


def _build_interaction_queue_view_add_msg(sim, super_interactions, msg):
    logger.debug('  _build_interaction_queue_view_add_msg({0})', sim.id)
    _build_interactions_add_msg(sim, super_interactions, msg.interactions)
    return True


def _build_interactions_add_msg(sim, super_interactions, msg):
    logger.debug('  _build_interactions_add_msg({0})', sim.id)
    msg.sim_id = sim.id
    if super_interactions:
        for si_interaction in super_interactions:
            with ProtocolBufferRollback(msg.interactions) as (msg_interaction):
                _build_interaction_msg(si_interaction, msg_interaction)

        return True
    return False


def send_interactions_add_msg(sim, interactions, immediate=False):
    logger.debug('send_interactions_add_msg({}), immediate={}', sim.id, immediate)
    msg = Sims_pb2.InteractionsAdd()
    if _build_interactions_add_msg(sim, interactions, msg):
        logger.debug('    SENDING')
        add_message_if_selectable(sim, MSG_SIM_INTERACTIONS_ADD, msg, immediate)
    else:
        logger.debug('    NOT_SENDING')


def _build_interaction_msg(interaction_info, msg):
    if not interaction_info:
        logger.debug('Why am I here with no interaction info???')
    else:
        logger.debug('  _build_interaction_msg({0})', interaction_info.interaction_id)
        msg.interaction_id = interaction_info.interaction_id
        msg.insert_after_id = interaction_info.insert_after_id
        if interaction_info.ui_visual_type != Sims_pb2.Interaction.SIMPLE:
            msg.super_id = interaction_info.super_id
            super_name, super_icon_info_data = interaction_info.get_super_icon_info()
            if super_name is not None:
                build_icon_info_msg(super_icon_info_data, super_name, msg.super_icon_info)
        else:
            msg.super_id = 0
        if interaction_info.icon_info:
            icon_info = interaction_info.icon_info
            if not issubclass(type(icon_info), _IconInfoData):
                logger.warn('All icon_info data types should be converted to the type IconInfoData. The tuple format found in interaction {} is no longer supported.', interaction_info, owner='shipark')
                icon_info_data = IconInfoData(icon_resource=(icon_info[0]), obj_instance=(icon_info[1]))
            else:
                icon_info_data = icon_info
            build_icon_info_msg(icon_info_data, interaction_info.display_name, msg.icon_info)
        if interaction_info.target is not None and interaction_info.target.id is not None:
            msg.target_manager_object_id.object_id = interaction_info.target.id
    if interaction_info.target is not None:
        msg.target_manager_object_id.manager_id = interaction_info.target.manager_id
    for participant in interaction_info.participants:
        if participant is not None:
            with ProtocolBufferRollback(msg.participant_manager_object_ids) as (participant_msg):
                participant_msg.manager_id = participant.manager_id
                participant_msg.object_id = participant.id

    msg.canceled = interaction_info.canceled
    msg.cancelable = interaction_info.user_cancelable
    msg.visual_type = interaction_info.ui_visual_type
    msg.queue_ui_state = interaction_info.ui_state
    for si_id in interaction_info.interactions_to_be_canceled:
        msg.interactions_to_be_canceled.append(si_id)

    if interaction_info.mood_list is not None:
        for mood in interaction_info.mood_list:
            msg.mood_list.append(mood.guid64)