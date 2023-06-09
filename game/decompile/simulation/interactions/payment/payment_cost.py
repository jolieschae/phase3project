# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\payment\payment_cost.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 30586 bytes
from objects.components.object_marketplace_component import ObjectMarketplaceComponent
from objects.components.object_fashion_marketplace_component import ObjectFashionMarketplaceComponent
from sims.funds import get_funds_for_source
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableVariant, Tunable, HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, OptionalTunable, TunableList, TunableFactory, TunableReference, TunableTuple
import sims4.log
from interactions import ParticipantType, ParticipantTypeActorTargetSim, ParticipantTypeSingle, ParticipantTypeObject, ParticipantTypeSingleSim
from interactions.context import InteractionContext
from interactions.payment.payment_dest import PaymentDestTuningFlags, PaymentDestNone, PaymentDestActiveHousehold, PaymentDestParticipantHousehold, PaymentDestBusiness, PaymentDestStatistic
from interactions.payment.payment_info import BusinessPaymentInfo, PaymentInfo, PaymentBusinessRevenueType
from interactions.payment_liability import PaymentLiability
from interactions.priority import Priority
from restaurants.restaurant_tuning import get_restaurant_zone_director
from sims.household_utilities.utility_types import Utilities
from ui.ui_dialog_generic import UiDialogTextInputOkCancel
import objects.components.types, services
logger = sims4.log.Logger('Payment', default_owner='rmccord')

class _Payment(HasTunableSingletonFactory, AutoFactoryInit):

    @TunableFactory.factory_option
    def payment_destination_option(available_dest_flags=PaymentDestTuningFlags.ALL):
        dest_kwargs = {'no_dest': PaymentDestNone.TunableFactory()}
        default = 'no_dest'
        if available_dest_flags & PaymentDestTuningFlags.ACTIVE_HOUSEHOLD:
            dest_kwargs['active_household'] = PaymentDestActiveHousehold.TunableFactory()
            default = 'active_household'
        if available_dest_flags & PaymentDestTuningFlags.PARTICIPANT_HOUSEHOLD:
            dest_kwargs['participant_household'] = PaymentDestParticipantHousehold.TunableFactory()
            default = 'participant_household'
        if available_dest_flags & PaymentDestTuningFlags.BUSINESS:
            dest_kwargs['business'] = PaymentDestBusiness.TunableFactory()
            default = 'business'
        if available_dest_flags & PaymentDestTuningFlags.STATISTIC:
            dest_kwargs['statistic'] = PaymentDestStatistic.TunableFactory()
            default = 'statistic'
        return {'payment_destinations': TunableList(description='\n                List of destinations for the payment cost to be given, which are\n                resolved in order until one successfully accepts the payment.\n                ',
                                   tunable=TunableVariant(description='\n                    Defines where the cost goes when it is paid for by the payment\n                    source.\n                    ', 
                                  default=default, **dest_kwargs))}

    def get_amount(self, resolver):
        raise NotImplementedError

    def on_payment(self, amount, resolver, payment_info_override=None):
        if payment_info_override is None:
            cost_info = self.get_payment_info(amount, resolver)
        else:
            cost_info = payment_info_override
        for dest in self.payment_destinations:
            if dest.give_payment(cost_info):
                return True

        if self.payment_destinations:
            logger.warn('Payment Destinations tuned on {}, but funds never made it there.', self)
        return True

    def try_deduct_payment(self, resolver, sim, fail_callback, source, cost_modifiers):
        return self.make_payment(resolver, sim, source, cost_modifiers)

    def make_payment(self, resolver, sim, source, cost_modifiers, override_amount=None):
        delta, _ = self.get_simoleon_delta(resolver, source, cost_modifiers, override_amount)
        if source.allow_credits:
            amount = -delta
        else:
            amount = max(-delta, 0)
        paid_amount = source.try_remove_funds(sim, amount, resolver)
        if paid_amount is not None:
            return self.on_payment(paid_amount, resolver)
        return False

    def get_simoleon_delta(self, resolver, source, cost_modifiers, override_amount=None):
        if override_amount is None:
            payment_owed = self.get_amount(resolver)
            if payment_owed is None:
                logger.warn('Payment for {} has an invalid cost.', self)
                payment_owed = 0
        else:
            payment_owed = override_amount
        if payment_owed:
            payment_owed *= -cost_modifiers.get_multiplier(resolver)
        return (
         round(payment_owed), source.funds_source)

    def get_payment_info(self, amount, resolver):
        return PaymentInfo(amount, resolver)


class PaymentAmount(_Payment):
    FACTORY_TUNABLES = {'amount': Tunable(description='\n            The amount to pay.\n            ',
                 tunable_type=int,
                 default=0)}

    def get_amount(self, resolver):
        return self.amount


class PaymentAmountUpTo(PaymentAmount):
    FACTORY_TUNABLES = {'participant': TunableEnumEntry(description="\n            The participant Sim from whom we'll collect the amount.\n            ",
                      tunable_type=ParticipantTypeActorTargetSim,
                      default=(ParticipantTypeActorTargetSim.Actor))}

    def get_amount(self, resolver):
        participant = resolver.get_participant(self.participant)
        if participant is not None:
            if participant is not None:
                return min(self.amount, participant.household.funds.money)
        return self.amount


class PaymentBills(_Payment):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            The participant for whom we need to pay bills.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'locked_args':{'payment_destinations': None}}

    def __init__(self, *args, payment_destinations=None, **kwargs):
        (super().__init__)(args, payment_destinations=[], **kwargs)

    def _get_bills_manager(self, resolver):
        participant = resolver.get_participant(self.participant)
        if participant is not None:
            household = participant.household
            if household is not None:
                return household.bills_manager

    def get_amount(self, resolver):
        bills_manager = self._get_bills_manager(resolver)
        if bills_manager is not None:
            return bills_manager.current_payment_owed

    def on_payment(self, amount, resolver, payment_info_override=None):
        bills_manager = self._get_bills_manager(resolver)
        if bills_manager is not None:
            if bills_manager.current_payment_owed != amount:
                return False
            bills_manager.pay_bill()
            return True
        return False


class PaymentUtility(PaymentBills):
    FACTORY_TUNABLES = {'utility':TunableEnumEntry(description='\n            The household utility we want to modify.\n            ',
       tunable_type=Utilities,
       default=Utilities.POWER), 
     'override_keep_excess_production':OptionalTunable(description='\n            If enabled then ignore the results of the Keep Excess Production test\n            that would normally be used to compute the amount of the utility available\n            for payout.\n            ',
       tunable=Tunable(description='\n                Use this value and ignore the results of the Keep Excess Production test\n                that would normally be used to compute the amount of the utility available\n                for payout.\n                ',
       tunable_type=bool,
       default=True))}

    def __init__(self, *args, payment_destinations=None, **kwargs):
        (super().__init__)(args, payment_destinations=[], **kwargs)
        self._utility_info = None

    def _get_utility_bill_info(self, bills_manager):
        utility_info = bills_manager.get_utility_bill_info(self.utility)
        if utility_info is None:
            return
        unpaid_info = bills_manager.current_source_owed(self.utility)
        if unpaid_info is not None:
            utility_info -= unpaid_info
        return utility_info

    def get_amount(self, resolver):
        bills_manager = self._get_bills_manager(resolver)
        if bills_manager is None:
            return
        self._utility_info = self._get_utility_bill_info(bills_manager)
        if self._utility_info is None:
            return
        return self._utility_info.billable_amount

    def on_payment(self, amount, resolver, payment_info_override=None):
        if self._utility_info is None:
            return False
        bills_manager = self._get_bills_manager(resolver)
        if bills_manager is not None:
            utility_info = self._get_utility_bill_info(bills_manager)
            if utility_info.billable_amount != self._utility_info.billable_amount or self._utility_info.billable_amount != amount:
                return False
            bills_manager.pay_source_bill(self.utility, self._utility_info)
            return True
        return False


class PaymentCatalogValue(_Payment):
    FACTORY_TUNABLES = {'participant': TunableEnumEntry(description='\n            The participant for which we want to pay an amount equal to its\n            catalog value.\n            ',
                      tunable_type=ParticipantType,
                      default=(ParticipantType.Object))}

    def get_amount(self, resolver):
        participant = resolver.get_participant(self.participant)
        if participant is not None:
            return participant.definition.price


class PaymentCurrentValue(_Payment):
    FACTORY_TUNABLES = {'participant': TunableEnumEntry(description='\n            The participant for which we want to pay an amount equal to its\n            current value.\n            ',
                      tunable_type=ParticipantType,
                      default=(ParticipantType.Object))}

    def get_amount(self, resolver):
        participant = resolver.get_participant(self.participant)
        if participant is not None:
            return participant.current_value


class PaymentBaseRetailValue(_Payment):
    FACTORY_TUNABLES = {'participant': TunableEnumEntry(description='\n            The participant for which we want to pay an amount equal to its\n            retail value.\n            ',
                      tunable_type=ParticipantType,
                      default=(ParticipantType.Object))}

    def get_amount(self, resolver):
        participant = resolver.get_participant(self.participant)
        if participant is not None:
            retail_component = participant.get_component(objects.components.types.RETAIL_COMPONENT)
            if retail_component is not None:
                return retail_component.get_retail_value()
            return participant.current_value


class PaymentBaseDiningBill(_Payment):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            The participant for Sim is paying the bill so we can use that Sim\n            to determine the correct dining group and meal cost.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Object), 
     'locked_args':{'payment_destinations': ()}}

    def get_amount(self, resolver):
        group = self._get_group(resolver)
        if group is not None:
            return group.meal_cost
        return 0

    def on_payment(self, amount, resolver, payment_info_override=None):
        super().on_payment(amount, resolver)
        group = self._get_group(resolver)
        if group is not None:
            group.pay_for_group(amount)
            return True
        return False

    def _get_group(self, resolver):
        participant = resolver.get_participant(self.participant)
        if participant is None:
            return
        zone_director = get_restaurant_zone_director()
        if zone_director is None:
            return
        sim_instance = participant.get_sim_instance()
        if sim_instance is None:
            return
        groups = zone_director.get_dining_groups_by_sim(sim_instance)
        return next(iter(groups), None)


class _PaymentWrapper(_Payment):
    FACTORY_TUNABLES = {'wrapped_cost':TunableVariant(description='\n            The amount to pay, affected by wrapped payment type. If this is 0,\n            then this operation costs nothing.\n            ',
       amount=PaymentAmount.TunableFactory(),
       amount_up_to=PaymentAmountUpTo.TunableFactory(),
       catalog_value=PaymentCatalogValue.TunableFactory(),
       current_value=PaymentCurrentValue.TunableFactory(),
       base_retail_value=PaymentBaseRetailValue.TunableFactory(),
       default='amount'), 
     'locked_args':{'payment_destinations': ()}}

    def on_payment(self, amount, resolver, payment_info_override=None):
        return self.wrapped_cost.on_payment(amount, resolver, payment_info_override=(self.get_payment_info(amount, resolver)))


class PaymentBusinessAmount(_PaymentWrapper):

    @staticmethod
    def _verify_tunable_callback(cls, tunable_name, source, value):
        if value.generate_revenue is not None:
            if not value.wrapped_cost.payment_destinations:
                logger.error('Business Payment from {} is expected to generate revenue, but does not pay to any destinations.', source)

    FACTORY_TUNABLES = {'generate_revenue':OptionalTunable(description='\n            If this is enabled, then the business provider will gain the spent\n            amount as revenue. If this is not enabled, then the expense is\n            incurred and no revenue is generated.\n            \n            NOTE: You still need to set the payment destination under the\n            payment cost to actually pay the business.\n            ',
       tunable=TunableEnumEntry(description='\n                The type of revenue generated by this interaction. If the type\n                is Item Sold, the items old count for the store will increment.\n                If the type is Seed Money, the money is added to the store\n                without the sold item count being touched.\n                ',
       tunable_type=PaymentBusinessRevenueType,
       default=(PaymentBusinessRevenueType.ITEM_SOLD)),
       enabled_by_default=True), 
     'verify_tunable_callback':_verify_tunable_callback}

    def get_amount(self, resolver):
        business_manager = services.business_service().get_business_manager_for_zone()
        if business_manager is not None:
            amount = self.wrapped_cost.get_amount(resolver)
            if self.generate_revenue == PaymentBusinessRevenueType.ITEM_SOLD:
                return business_manager.get_value_with_markup(amount)
            return amount
        return self.wrapped_cost.get_amount(resolver)

    def get_payment_info(self, amount, resolver):
        return BusinessPaymentInfo(amount, resolver, revenue_type=(self.generate_revenue))


class PaymentMarketplaceListing(_Payment):
    FACTORY_TUNABLES = {'seller_sim':TunableEnumEntry(description="\n            The sim doing the selling. Might affect price, but doesn't \n            determine the actual payment source.\n            ",
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'object_being_listed':TunableEnumEntry(description='\n            The object being listed. This will be used to calculate the cost.\n            ',
       tunable_type=ParticipantTypeObject,
       default=ParticipantTypeObject.Object)}

    def get_amount(self, resolver):
        seller_sim_info = resolver.get_participant(self.seller_sim)
        object_being_listed = resolver.get_participant(self.object_being_listed)
        return ObjectMarketplaceComponent.get_listing_cost(seller_sim_info, object_being_listed)


class PaymentFashionMarketplaceListing(_Payment):
    FACTORY_TUNABLES = {'seller_sim':TunableEnumEntry(description="\n            The sim doing the selling. Might affect price, but doesn't \n            determine the actual payment source.\n            ",
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'object_being_listed':TunableEnumEntry(description='\n            The object being listed. This will be used to calculate the cost.\n            ',
       tunable_type=ParticipantTypeObject,
       default=ParticipantTypeObject.Object)}

    def get_amount(self, resolver):
        seller_sim_info = resolver.get_participant(self.seller_sim)
        object_being_listed = resolver.get_participant(self.object_being_listed)
        return ObjectFashionMarketplaceComponent.get_listing_cost(seller_sim_info, object_being_listed)


class PaymentFromLiability(_Payment):
    FACTORY_TUNABLES = {'locked_args': {'payment_destinations': ()}}

    def on_payment(self, amount, resolver, payment_info_override=None):
        interaction = resolver.interaction
        payment_liability = interaction.get_liability(PaymentLiability.LIABILITY_TOKEN)
        if payment_liability is not None:
            self.payment_destinations = payment_liability.payment_destinations
        super().on_payment(amount, resolver, payment_info_override)

    def get_amount(self, resolver):
        interaction = resolver.interaction
        if interaction is not None:
            payment_liability = interaction.get_liability(PaymentLiability.LIABILITY_TOKEN)
            if payment_liability is not None:
                return payment_liability.amount
            logger.error('Interaction {} has a payment element with liability payment cost but no liability', interaction)
            return 0
        else:
            return 0


TEXT_INPUT_PAYMENT_VALUE = 'payment_value'

class PaymentDialog(_Payment):
    FACTORY_TUNABLES = {'input_dialog':UiDialogTextInputOkCancel.TunableFactory(description='\n            The dialog that is displayed. The amount the user enters into the\n            input is used as the payment amount.\n            ',
       text_inputs=(
      TEXT_INPUT_PAYMENT_VALUE,)), 
     'dest_exceed_tooltip':OptionalTunable(description='\n             If enabled, allows specification of a tooltip to display if\n             the user has entered a value that exceeds what the destination\n             can hold.\n             \n             Additional tokens are source max, dest value, minimum\n             ',
       tunable=TunableLocalizedStringFactory()), 
     'source_exceed_tooltip':OptionalTunable(description='\n             If enabled, allows specification of a tooltip to display if\n             the user has entered a value that exceeds the amount in the source.\n             \n             Additional tokens are source max, dest value, minimum\n             ',
       tunable=TunableLocalizedStringFactory()), 
     'below_min_tooltip':OptionalTunable(description='\n             If enabled, allows specification of a tooltip to display if\n             the user has entered a value that is below minimum amount allowed.\n             \n             Additional tokens are source max, dest value, minimum\n             ',
       tunable=TunableLocalizedStringFactory()), 
     'success_continuation':OptionalTunable(description=' \n            If tuned to an interaction, we will push that interaction as a\n            continuation if we receive a valid dialog response. Additionally, we\n            will attach a payment liability to that interaction so that the\n            payment can be resolved on the sequence of that interaction or on a\n            later continuation. The payment liability will store the entered\n            value and tuned destination, but will not respect all other tuned\n            options.To trigger that payment, add a payment basic extra to that\n            interaction and select the "Liability" payment cost.\n            ',
       tunable=TunableTuple(interaction=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
       target_participant=TunableEnumEntry(description='\n                    The participant that is to be used as the target of the\n                    continuation interaction.\n                    ',
       tunable_type=ParticipantTypeSingle,
       default=(ParticipantType.Object))))}

    def get_amount(self, resolver):
        return 0

    def try_deduct_payment(self, resolver, sim, fail_callback, source, cost_modifiers):
        max_value = None
        min_value = None
        dest_funds = 0
        invalid_max_tooltip = None
        invalid_min_tooltip = None
        for dest in self.payment_destinations:
            max_value, dest_funds, min_value = dest.get_funds_info(resolver)
            if max_value is not None:
                break

        source_max = source.max_funds(sim, resolver)
        if max_value is None or source_max < max_value:
            max_value = source_max
            if self.source_exceed_tooltip is not None:
                invalid_max_tooltip = self.source_exceed_tooltip
        elif self.dest_exceed_tooltip is not None:
            invalid_max_tooltip = self.dest_exceed_tooltip
        if min_value is not None:
            invalid_min_tooltip = self.below_min_tooltip
        dialog = self.input_dialog(sim, resolver, max_value=max_value,
          invalid_max_tooltip=invalid_max_tooltip,
          min_value=min_value,
          invalid_min_tooltip=invalid_min_tooltip)

        def on_response(value_dialog):
            if not value_dialog.accepted:
                return
            else:
                new_value = value_dialog.text_input_responses.get(TEXT_INPUT_PAYMENT_VALUE)
                try:
                    new_value = int(new_value)
                except:
                    if fail_callback:
                        fail_callback()
                    return
                else:
                    if self.success_continuation is not None:
                        context = InteractionContext(sim, InteractionContext.SOURCE_SCRIPT, Priority.High)
                        target = resolver.get_participant(self.success_continuation.target_participant)
                        if target.is_sim:
                            target = target.get_sim_instance()
                            if target is None:
                                return
                        liability = PaymentLiability(new_value, self.payment_destinations)
                        liabilities = ((PaymentLiability.LIABILITY_TOKEN, liability),)
                        sim.push_super_affordance((self.success_continuation.interaction), target, context, liabilities=liabilities)
                    else:
                        self.make_payment(resolver, sim, source, cost_modifiers, new_value)

        if min_value is None:
            min_value = 0
        dialog.show_dialog(on_response=on_response, additional_tokens=(source_max, dest_funds, min_value))
        return True