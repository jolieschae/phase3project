# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\si_restore.py
# Compiled at: 2021-05-04 20:17:35
# Size of source mod 2**32: 5337 bytes
from autonomy.settings import AutonomyState
from objects import ALL_HIDDEN_REASONS
from sims.sim_info_types import SimZoneSpinUpAction
from sims4.tuning.tunable import Tunable
import services, sims4
logger = sims4.log.Logger('SuperInteractionRestore')

class SuperInteractionRestorer:
    INTERACTION_SPINUP_TIMETIMEOUT_TIME = Tunable(description="\n        The maximum number of ticks that the server takes trying to restore\n        SI's to restore staged interactions or run preroll autonomy.\n        ",
      tunable_type=int,
      default=10)
    INTERACTION_SPINUP_TRANSITIONING_TIME = Tunable(description='\n        The number of ticks that we take waiting for sims to get in\n        transitioning interactions.\n        ',
      tunable_type=int,
      default=10)
    RESTORE_STAGED_INTERACTIONS = 0
    RESTORE_TRANSITIONING_INTERACTION = 1
    RESTORE_QUEUED_INTERACTIONS = 2
    NUM_RESTORE_STEPS = 3

    def __init__(self):
        self._sims_to_restore = []
        self._si_state_restore_liabilities = []
        self._current_restore_state = self.RESTORE_STAGED_INTERACTIONS

    def _run_startup_interactions(self):
        try:
            for restore_step in range(self.NUM_RESTORE_STEPS):
                self._current_restore_state = restore_step
                if restore_step == self.RESTORE_STAGED_INTERACTIONS:
                    self._load_staged_interactions()
                elif restore_step == self.RESTORE_TRANSITIONING_INTERACTION:
                    self._load_transitioning_interactions()

        except Exception as e:
            try:
                logger.exception('Exception raised while trying to startup interactions.', exc=e)
            finally:
                e = None
                del e

    def restore_sim_si_state(self):
        sim_info_manager = services.sim_info_manager()
        for sim_info in sim_info_manager.get_sims_for_spin_up_action(SimZoneSpinUpAction.RESTORE_SI):
            sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if sim is None:
                continue
            self._sims_to_restore.append(sim.ref())
            sim.set_allow_route_instantly_when_hitting_marks(True)

        if not self._sims_to_restore:
            return
        self._sims_to_restore.sort(key=(lambda sim_ref: sim_ref().id))
        autonomy_disabled_sim_infos = set()
        for sim in sim_info_manager.instanced_sims_gen():
            old_setting = sim.autonomy_settings.get_setting(AutonomyState, sim.get_autonomy_settings_group())
            sim.autonomy_settings.set_setting(AutonomyState.DISABLED, sim.get_autonomy_settings_group())
            autonomy_disabled_sim_infos.add((sim.sim_info, old_setting))

        self._run_startup_interactions()
        for sim_info, setting in autonomy_disabled_sim_infos:
            sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if sim is not None:
                sim.autonomy_settings.set_setting(setting, sim.get_autonomy_settings_group())
            else:
                logger.error('{} was uninstantiated during si restore. si_state: {}',
                  sim_info,
                  (sim_info.si_state),
                  owner='tingyul')

    def restore_sim_queued_si_state(self):
        self._load_queued_interactions()

    def _load_staged_interactions(self):
        for sim_ref in self._sims_to_restore:
            sim = sim_ref()
            if sim is not None:
                sim.load_staged_interactions()

    def _load_transitioning_interactions(self):
        for sim_ref in self._sims_to_restore:
            sim = sim_ref()
            if sim is not None:
                sim.load_transitioning_interaction()

    def _load_queued_interactions(self):
        for sim_ref in self._sims_to_restore:
            sim = sim_ref()
            if sim is not None:
                sim.load_queued_interactions()