# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\money_payout.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 7826 bytes
from protocolbuffers import Consts_pb2
import collections, interactions.utils, sims4
from interactions.liability import Liability
from interactions.utils.loot_basic_op import BaseLootOperation
from sims.funds import FundsSource
from sims4.localization import LocalizationHelperTuning
from sims4.tuning.tunable import Tunable, TunableList, TunableLiteralOrRandomValue, OptionalTunable
from tag import TunableTags
from singletons import DEFAULT
from tunable_multiplier import TunableStatisticModifierCurve
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
logger = sims4.log.Logger('MoneyPayout')

class MoneyLiability(Liability):
    LIABILITY_TOKEN = 'MoneyLiability'

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.amounts = collections.defaultdict(lambda: 0)


class MoneyChange(BaseLootOperation):
    FACTORY_TUNABLES = {'amount':TunableLiteralOrRandomValue(description='\n            The amount of Simoleons awarded. The value will be rounded to the\n            closest integer. When two integers are equally close, rounding is done\n            towards the even one (e.g. 0.5 -> 0, 1.5 -> 2).  Negative amounts allowed\n            and allow partial deductions (will only take balance to zero, not negative).\n            ',
       tunable_type=float,
       default=0,
       minimum=None), 
     'statistic_multipliers':TunableList(description='\n            Tunables for adding statistic based multipliers to the payout in the\n            format:\n            \n            amount *= statistic.value\n            ',
       tunable=TunableStatisticModifierCurve.TunableFactory()), 
     'display_to_user':Tunable(description='\n            If true, the amount will be displayed in the interaction name.\n            ',
       tunable_type=bool,
       default=False), 
     'notification':OptionalTunable(description='\n            If set and an amount is awarded, displays a dialog to the user.\n            \n            The notification will have access to the amount awarded as a localization token. e.g. {0.Money} \n            ',
       tunable=TunableUiDialogNotificationSnippet()), 
     'tags':OptionalTunable(description='\n            If enabled, the simoleons earned will be associated with the listed\n            tags which can be tested against using ObjectiveTests tuning.\n            ',
       tunable=TunableTags(description='\n                The tag associated with this payment\n                '))}

    def __init__(self, amount, statistic_multipliers, display_to_user, notification, tags, **kwargs):
        (super().__init__)(**kwargs)
        self._amount = amount
        self._statistic_multipliers = statistic_multipliers
        self._display_to_user = display_to_user
        self._random_amount = None
        self._notification = notification
        self._tags = tags

    @property
    def loot_type(self):
        return interactions.utils.LootType.SIMOLEONS

    def get_simoleon_delta(self, interaction, target=DEFAULT, context=DEFAULT, **interaction_parameters):
        if not self._display_to_user:
            return (
             0, FundsSource.HOUSEHOLD)
        else:
            return self._tests.run_tests((interaction.get_resolver)(target=target, context=context, **interaction_parameters)) or (
             0, FundsSource.HOUSEHOLD)
        sim = context.sim if context is not DEFAULT else DEFAULT
        recipients = (interaction.get_participants)(participant_type=self.subject, sim=sim, target=target, **interaction_parameters)
        skill_multiplier = 1 if context is DEFAULT else interaction.get_skill_multiplier(interaction.monetary_payout_multipliers, context.sim)
        return (
         self.amount * len(recipients) * skill_multiplier, FundsSource.HOUSEHOLD)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        interaction = resolver.interaction
        if interaction is not None:
            money_liability = interaction.get_liability(MoneyLiability.LIABILITY_TOKEN)
            if money_liability is None:
                money_liability = MoneyLiability()
                interaction.add_liability(MoneyLiability.LIABILITY_TOKEN, money_liability)
            skill_multiplier = interaction.get_skill_multiplier(interaction.monetary_payout_multipliers, interaction.sim)
        else:
            money_liability = None
            skill_multiplier = 1
        subject_obj = self._get_object_from_recipient(subject)
        amount_multiplier = self._get_multiplier(resolver, subject_obj) * skill_multiplier
        amount = round(self.amount * amount_multiplier)
        if amount:
            if money_liability is not None:
                money_liability.amounts[self.subject] += amount
            else:
                if interaction is not None:
                    interaction_category_tags = interaction.interaction_category_tags
                else:
                    interaction_category_tags = frozenset()
                if self._tags is not None:
                    interaction_category_tags = interaction_category_tags.union(self._tags)
                if amount < 0:
                    subject.household.funds.try_remove_amount((-amount), (Consts_pb2.TELEMETRY_INTERACTION_REWARD), subject_obj, require_full_amount=False)
                else:
                    subject.household.funds.add(amount, (Consts_pb2.TELEMETRY_INTERACTION_REWARD), subject_obj, tags=interaction_category_tags)
            if self._notification is not None:
                dialog = self._notification(subject, resolver=resolver)
                dialog.show_dialog(additional_tokens=(amount,))

    def _on_apply_completed(self):
        self._random_amount = None

    def _get_display_text(self, resolver=None):
        return (LocalizationHelperTuning.MONEY)(*self._get_display_text_tokens())

    def _get_display_text_tokens(self, resolver=None):
        return (
         self.amount,)

    def _get_multiplier(self, resolver, sim):
        amount_multiplier = 1
        if self._statistic_multipliers:
            for statistic_multiplier in self._statistic_multipliers:
                amount_multiplier *= statistic_multiplier.get_multiplier(resolver, sim)

        return amount_multiplier

    @property
    def amount(self):
        if self._random_amount is None:
            self._random_amount = self._amount.random_float()
        return self._random_amount