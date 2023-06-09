# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\formation\formation_tests.py
# Compiled at: 2020-11-12 10:43:20
# Size of source mod 2**32: 10889 bytes
from event_testing.results import TestResult
from caches import cached_test
from interactions import ParticipantTypeSingle
from objects import ALL_HIDDEN_REASONS
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, OptionalTunable, TunableEnumEntry, TunableReference, TunableVariant, Tunable, TunableSet
from tunable_utils.tunable_white_black_list import TunableWhiteBlackList
import event_testing.test_base, services, sims4.resources

class FormationAvailability(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'available_formations': TunableSet(description='\n            The Sims must be able to form at least one of these formations.\n            ',
                               tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
                               class_restrictions=('RoutingFormation', )))}

    def test(self, master, slave, tooltip):
        if slave is not None:
            if slave.routing_component.routing_master is not None:
                return TestResult(False, 'Slave {} is already in a formation. No formations available.', slave, tooltip=tooltip)
        if master is not None:
            other_formations = [other_formation for other_formation in master.get_routing_slave_data()]
            for formation_type in self.available_formations:
                if not formation_type.formation_compatibility.test_collection(other_formations):
                    continue
                formations = [slave_data for slave_data in other_formations if slave_data.formation_type is formation_type]
                if formations:
                    if len(formations) >= formation_type.max_slave_count:
                        continue
                break
            else:
                return TestResult(False, '{} has no more room in their routing formation or their formations are incompatible.', master, tooltip=tooltip)

        return TestResult.TRUE


class InRoutingFormation(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'required_or_prohibited':Tunable(description='\n            If enabled, we require the master/slave to be in a\n            formation of any type. If disabled, we require that the\n            master/slave is not in a formation.\n            ',
       tunable_type=bool,
       default=True), 
     'formations_to_validate':OptionalTunable(description='\n            If enabled depending on the required_or_prohibited check, we will\n            validate if the Sim current formation against the ones on this\n            list.\n            ',
       tunable=TunableWhiteBlackList(description='\n                A white/blacklist that determines compatibility via\n                required or prohibited formations.\n                ',
       tunable=TunableReference(description='\n                    A routing formation\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
       class_restrictions=('RoutingFormation', ),
       pack_safe=True)))}

    def test(self, master, slave, tooltip):
        if slave is not None:
            if slave.routing_component is None:
                return TestResult(False, '{} is expected to have a routing component.', slave, tooltip=tooltip)
        elif self.required_or_prohibited:
            if slave.routing_component.routing_master is None:
                return TestResult(False, '{} is expected to be the slave in a routing formation.', slave, tooltip=tooltip)
        elif not self.required_or_prohibited:
            if slave.routing_component.routing_master is not None:
                return TestResult(False, '{} is not expected to be the slave in a routing formation.', slave, tooltip=tooltip)
        elif master is not None:
            slave_data = [formation for formation in master.get_routing_slave_data() if not self.formations_to_validate is None if self.formations_to_validate.test_item(formation.formation_type)]
            if self.required_or_prohibited:
                if not slave_data:
                    return TestResult(False, '{} is expected to be the master of a routing formation.', master, tooltip=tooltip)
                if slave is not None:
                    slave_formation = master.get_formation_data_for_slave(slave)
                    if not slave_formation is None:
                        if self.formations_to_validate is not None:
                            return self.formations_to_validate.test_item(slave_formation.formation_type) or TestResult(False, '{} is expected to be the master of a routing formation with {}', master, slave, tooltip=tooltip)
                    elif slave_data:
                        return TestResult(False, '{} is not expected to be the master of a routing formation', master, tooltip=tooltip)
        return TestResult.TRUE


class FormationCompatibility(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'compatibility': TunableWhiteBlackList(description='\n            A white/blacklist that determines compatibility via\n            required or prohibited formations.\n            ',
                        tunable=TunableReference(description='\n                A routing formation\n                ',
                        manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
                        class_restrictions=('RoutingFormation', ),
                        pack_safe=True))}

    def test(self, master, slave, tooltip):
        test_formations = None
        if master is not None:
            test_formations = set(master.get_all_routing_slave_data_gen())
        elif slave is not None:
            if slave.routing_master is None:
                test_formations = (None, )
            else:
                if test_formations is not None:
                    test_formations &= {slave.routing_master.get_formation_data_for_slave(slave)}
                else:
                    test_formations = (
                     slave.routing_master.get_formation_data_for_slave(slave),)
        if test_formations:
            test_formations = {formation.formation_type for formation in test_formations if formation is not None}
            if not self.compatibility.test_collection(test_formations):
                return TestResult(False, '{}, {} are not in compatible formations.', master, slave, tooltip=tooltip)
        return TestResult.TRUE


class RoutingSlaveTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'participant_master':OptionalTunable(description='\n            If enabled, the specified participant must satisfy the test\n            requirements for all routing formations they are a master of.\n            ',
       tunable=TunableEnumEntry(description='\n                The master participant.\n                ',
       tunable_type=ParticipantTypeSingle,
       default=(ParticipantTypeSingle.Actor))), 
     'participant_slave':OptionalTunable(description='\n            If enabled, the specified participant must satisfy the test\n            requirements for all routing formations they are a slave of.\n            ',
       tunable=TunableEnumEntry(description='\n                The slave participant.\n                ',
       tunable_type=ParticipantTypeSingle,
       default=(ParticipantTypeSingle.TargetSim))), 
     'formation_test':TunableVariant(description='\n            How we want to test the formation of the Master/Slave.\n            ',
       in_formation=InRoutingFormation.TunableFactory(),
       available_formations=FormationAvailability.TunableFactory(),
       compatibility=FormationCompatibility.TunableFactory(),
       default='in_formation')}

    def get_expected_args(self):
        expected_args = {}
        if self.participant_master is not None:
            expected_args['master_sims'] = self.participant_master
        if self.participant_slave is not None:
            expected_args['slave_sims'] = self.participant_slave
        return expected_args

    @cached_test
    def __call__(self, master_sims=(), slave_sims=()):
        master = next(iter(master_sims), None)
        slave = next(iter(slave_sims), None)
        if master is not None:
            if master.is_sim:
                master = master.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if slave is not None:
            if slave.is_sim:
                slave = slave.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        result = self.formation_test.test(master, slave, self.tooltip)
        return result