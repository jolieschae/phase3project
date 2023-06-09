# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\organizations\organization_loot_ops.py
# Compiled at: 2019-07-10 15:27:17
# Size of source mod 2**32: 2637 bytes
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableVariant
import services, sims4
logger = sims4.log.Logger('Organization Loot', default_owner='shipark')

class _JoinOrganizationOp(HasTunableSingletonFactory, AutoFactoryInit):

    def apply(self, subject, org_id):
        organization_service = services.organization_service()
        if organization_service is None:
            return False
        return organization_service.add_organization_member(subject, org_id)


class _LeaveOrganizationOp(HasTunableSingletonFactory, AutoFactoryInit):

    def apply(self, subject, org_id):
        organization_tracker = subject.organization_tracker
        if organization_tracker is None:
            return False
        organization_tracker.leave_organization(org_id)
        return True


class OrganizationMembershipLoot(BaseLootOperation):
    FACTORY_TUNABLES = {'organization':TunableReference(description='\n            The organization to join or leave.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SNIPPET),
       class_restrictions='Organization'), 
     'membership_action':TunableVariant(description='\n            Specify joining or leaving the tuned organization.\n            ',
       join=_JoinOrganizationOp.TunableFactory(),
       leave=_LeaveOrganizationOp.TunableFactory(),
       default='join')}

    def __init__(self, organization, membership_action, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.organization = organization
        self.membership_action = membership_action

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not subject.is_sim:
            logger.error('Attempting to run membership action on {} which is not a Sim.', subject)
        if not self.membership_action.apply(subject, self.organization.guid64):
            logger.error('Membership Loot Action failed on {}, org tracker or service were not available.', subject)