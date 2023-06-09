# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\name_component.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 20605 bytes
import random
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from interactions import ParticipantType
from interactions.utils.interaction_elements import XevtTriggeredElement
from interactions.utils.loot_basic_op import BaseLootOperation, BaseTargetedLootOperation
from objects.client_object_mixin import ClientObjectMixin
from objects.components import Component, types, componentmethod, componentmethod_with_fallback
from objects.hovertip import TooltipFieldsComplete
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import HasTunableFactory, Tunable, TunableReference, OptionalTunable, TunableList, TunableTuple, AutoFactoryInit, TunableEnumEntry
from singletons import DEFAULT
import profanity, services, sims4.callback_utils, sims4.log
logger = sims4.log.Logger('NameComponent', default_owner='shipark')
NAME_COMPONENT_TOOLTIP_PRIORITY = 1

class NameComponent(Component, HasTunableFactory, component_name=types.NAME_COMPONENT, persistence_key=protocols.PersistenceMaster.PersistableData.NameComponent):
    DEFAULT_AFFORDANCE = TunableReference((services.get_instance_manager(sims4.resources.Types.INTERACTION)), description='The affordance generated by all NameComponents.')
    FACTORY_TUNABLES = {'allow_name':Tunable(description='\n            If set, the user is allowed to give a custom name to this\n            object.\n            ',
       tunable_type=bool,
       default=True), 
     'allow_description':Tunable(description='\n            If set, the user is allowed to give a custom description to this\n            object.\n            ',
       tunable_type=bool,
       default=False), 
     'affordance':OptionalTunable(tunable=TunableReference(description='\n                The affordance provided by this Name component. Use it if you want\n                to provide a custom affordance instead of the default one, which\n                will not be used if this is set.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
       disabled_name='use_default'), 
     'templates':TunableList(description='\n            The list of the template content for this component.\n            ',
       tunable=TunableTuple(template_name=TunableLocalizedStringFactory(description='\n                    The template name for the component.\n                    ',
       allow_none=True),
       template_description=TunableLocalizedStringFactory(description='\n                    The template description for the component.\n                    ',
       allow_none=True)))}

    def __init__(self, *args, allow_name=None, allow_description=None, affordance=None, templates=[], **kwargs):
        (super().__init__)(*args, **kwargs)
        self.allow_name = allow_name
        self.allow_description = allow_description
        self._affordance = affordance
        self._templates = templates
        self._template_name = None
        self._template_description = None
        self._on_name_changed = None

    def get_template_name_and_description(self):
        if self._template_name is None or self._template_description is None:
            self._set_template_content()
        template_name, template_description = self.owner.get_template_content_overrides()
        template_name = template_name if template_name is not DEFAULT else self._template_name
        template_description = template_description if template_description is not DEFAULT else self._template_description
        return (
         template_name, template_description)

    def _set_template_content(self):
        if self._templates:
            selected_template = random.choice(self._templates)
            self._template_name = selected_template.template_name
            self._template_description = selected_template.template_description

    def save(self, persistence_master_message):
        if self.owner.custom_name is None:
            if self.owner.custom_description is None:
                return
        persistable_data = protocols.PersistenceMaster.PersistableData()
        persistable_data.type = protocols.PersistenceMaster.PersistableData.NameComponent
        name_component_data = persistable_data.Extensions[protocols.PersistableNameComponent.persistable_data]
        if self.owner.custom_name is not None:
            name_component_data.name = self.owner.custom_name
        if self.owner.custom_description is not None:
            name_component_data.description = self.owner.custom_description
        persistence_master_message.data.extend([persistable_data])

    def load(self, persistable_data):
        name_component_data = persistable_data.Extensions[protocols.PersistableNameComponent.persistable_data]
        if name_component_data.HasField('name'):
            self.set_custom_name(self._get_filtered_text(name_component_data.name))
        if name_component_data.HasField('description'):
            self.set_custom_description(self._get_filtered_text(name_component_data.description))
        self.owner.update_object_tooltip()

    def _get_filtered_text(self, text):
        if self.owner.is_from_gallery:
            _, filtered_text = profanity.check(text)
            return filtered_text
        return text

    @componentmethod_with_fallback((lambda: False))
    def has_custom_name(self):
        if self.owner.custom_name:
            return True
        return False

    @componentmethod_with_fallback((lambda: False))
    def has_custom_description(self):
        if self.owner.custom_description:
            return True
        return False

    @componentmethod
    def set_custom_name(self, name, actor_sim_id=None):
        if self.allow_name:
            self.owner.custom_name = name if name else None
            if isinstance(self.owner, ClientObjectMixin):
                self.owner.update_tooltip_field((TooltipFieldsComplete.custom_name), name, priority=NAME_COMPONENT_TOOLTIP_PRIORITY, should_update=True, immediate=True)
            if actor_sim_id is not None:
                if services.relationship_service().get_mapped_tag_set_of_id(self.owner.definition.id):
                    services.relationship_service().update_object_type_name(name, actor_sim_id, self.owner.definition.id, self.owner)
            self._call_name_changed_callback()
            return True
        return False

    @componentmethod
    def remove_custom_name(self):
        if not self.set_custom_name(''):
            logger.warn('Failed to reset Custom Name on {}. Please check Allow Name on Name Component.', self.owner)

    @componentmethod
    def set_custom_description(self, description, force_set=False, update_tooltip=True):
        if self.allow_description or force_set:
            self.owner.custom_description = description if description else None
            self._call_name_changed_callback()
            if update_tooltip:
                if isinstance(self.owner, ClientObjectMixin):
                    self.owner.update_tooltip_field((TooltipFieldsComplete.custom_description), description, priority=NAME_COMPONENT_TOOLTIP_PRIORITY, should_update=True)
            return True
        return False

    @componentmethod
    def remove_custom_description(self):
        if not self.set_custom_description(''):
            logger.warn('Failed to reset Custom Description on {}. Please check Allow Description on Name Component.', self.owner)

    @componentmethod_with_fallback((lambda *_, **__: None))
    def add_name_changed_callback(self, callback):
        if self._on_name_changed is None:
            self._on_name_changed = sims4.callback_utils.CallableList()
        self._on_name_changed.append(callback)

    @componentmethod_with_fallback((lambda *_, **__: None))
    def remove_name_changed_callback(self, callback):
        if self._on_name_changed is not None:
            if callback in self._on_name_changed:
                self._on_name_changed.remove(callback)
                if not self._on_name_changed:
                    self._on_name_changed = None

    def _call_name_changed_callback(self):
        if self._on_name_changed is not None:
            self._on_name_changed(self.owner)

    def component_super_affordances_gen(self, **kwargs):
        yield self._affordance or self.DEFAULT_AFFORDANCE

    def component_interactable_gen(self):
        yield self

    def populate_localization_token(self, token):
        if self.owner.custom_name is not None:
            token.custom_name = self.owner.custom_name
        if self.owner.custom_description is not None:
            token.custom_description = self.owner.custom_description


class NameTransfer(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'description':'Transfer name between two participants at the beginning/end of an interaction or on XEvent.', 
     'participant_sending_name':TunableEnumEntry(description='\n            The participant who has the name that is being transferred.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'participant_receiving_name':TunableEnumEntry(description='\n            The participant who is receiving the name being transferred.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Object), 
     'transfer_description':Tunable(description='\n            If checked, the description will also be transferred along with the name.\n            ',
       tunable_type=bool,
       default=True)}

    def _do_behavior(self):
        sender = self.interaction.get_participant(self.participant_sending_name)
        receiver = self.interaction.get_participant(self.participant_receiving_name)
        if sender is None or receiver is None:
            logger.error(('Cannot transfer name between None participants. Sender: {}, Receiver: {}, Interaction: {}'.format(sender, receiver, self.interaction)), owner='rmccord')
            return
        sender_name_component = sender.name_component
        receiver_name_component = receiver.name_component
        if receiver_name_component is None:
            logger.error(('Receiver of Name Transfer does not have a Name Component. Receiver: {}, Interaction: {}'.format(sender, receiver, self.interaction)), owner='rmccord')
            return
        if sender_name_component.has_custom_name():
            receiver_name_component.set_custom_name(sender.custom_name)
        if self.transfer_description:
            if sender_name_component.has_custom_description():
                receiver_name_component.set_custom_description(sender.custom_description)


class NameResetLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'reset_name':Tunable(description='\n            If checked, it will reset the custom name of the name component.\n            ',
       tunable_type=bool,
       default=True), 
     'reset_description':Tunable(description='\n            If checked, it will reset the custom description of the name \n            component.\n            ',
       tunable_type=bool,
       default=False)}

    def __init__(self, reset_name, reset_description, **kwargs):
        (super().__init__)(**kwargs)
        self.reset_name = reset_name
        self.reset_description = reset_description

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            logger.error('Invalid subject specified for this loot operation. Please fix {} in tuning.', self)
            return
        if subject.name_component is None:
            logger.error('Subject {} has no object relationship component. Please fix {} in tuning.', subject, self)
            return
        if self.reset_name:
            subject.remove_custom_name()
        if self.reset_description:
            subject.remove_custom_description()


class TransferNameLootOp(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'transfer_name':Tunable(description='\n            If checked, it will transfer the custom name of the name component\n            from the subject to the target.\n            ',
       tunable_type=bool,
       default=True), 
     'transfer_description':Tunable(description='\n            If checked, it will transfer the custom description of the name \n            component from the subject to the target.\n            ',
       tunable_type=bool,
       default=True), 
     'clear_subject_name':Tunable(description="\n            If False, the subject's name will not be cleared. If True, then\n            the subject's name will be cleared. This will only happen if\n            transfer name is set to True. \n            ",
       tunable_type=bool,
       default=False), 
     'clear_subject_description':Tunable(description="\n            If False, the subject's description will not be cleared. If True, then\n            the subject's description will be cleared. This will only happen if\n            transfer description is set to True.\n            ",
       tunable_type=bool,
       default=False)}

    def __init__(self, *args, transfer_name, transfer_description, clear_subject_name, clear_subject_description, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._transfer_name = transfer_name
        self._transfer_description = transfer_description
        self._clear_subject_name = clear_subject_name
        self._clear_subject_description = clear_subject_description

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            logger.error("The Transfer Name Loot tuned on: '{}' has a subject participant of None value.", self)
            return
            subject_name_component = subject.get_component(types.NAME_COMPONENT)
            if subject_name_component is None:
                logger.error("The Transfer Name Loot tuned on:'{}' has a subject with no name component.", self)
                return
            if target is None:
                logger.error("The Transfer Name Loot tuned on: '{}' has a target participant of None value.", self)
                return
            target_name_component = target.get_component(types.NAME_COMPONENT)
            if target_name_component is None:
                logger.error("The Transfer Name Loot tuned on: '{}' has a target with no name component", self)
                return
            if self._transfer_name:
                target_name_component.remove_custom_name()
                if subject_name_component.has_custom_name():
                    target_name_component.set_custom_name(subject.custom_name)
                    if self._clear_subject_name:
                        subject_name_component.remove_custom_name()
        elif self._transfer_description:
            target_name_component.remove_custom_description()
            if subject_name_component.has_custom_description():
                target_name_component.set_custom_description(subject.custom_description)
                if self._clear_subject_description:
                    subject_name_component.remove_custom_description()


class SetNameFromObjectRelationship(BaseTargetedLootOperation):

    def _apply_to_subject_and_target(self, subject, target, resolver):
        ownable_component = target.get_component(types.OWNABLE_COMPONENT)
        name_component = target.get_component(types.NAME_COMPONENT)
        if ownable_component is not None and name_component is not None:
            sim_owner_id = ownable_component.get_sim_owner_id()
            obj_def_id = target.definition.id
            relationship_service = services.relationship_service()
            obj_tag_set = relationship_service.get_mapped_tag_set_of_id(obj_def_id)
            if obj_tag_set is not None:
                obj_relationship = relationship_service.get_object_relationship(sim_owner_id, obj_tag_set)
                if obj_relationship is not None and obj_relationship.get_object_rel_name() is not None:
                    name_component.set_custom_name(obj_relationship.get_object_rel_name())
        else:
            logger.error('Target {} needs to have both ownable and name components. Please fix {} in tuning.', target, self)
            return