# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\sim_log.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 14916 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
from sims4.repr_utils import standard_brief_id_repr
import interactions, sims4.log, sims4.telemetry, telemetry_helper
logger = sims4.log.Logger('InteractionLog')
TELEMETRY_GROUP_INTERACTION = 'INTR'
TELEMETRY_HOOK_SI_BEGIN = 'SIBE'
TELEMETRY_HOOK_SI_END = 'SIEN'
TELEMETRY_HOOK_MIXER_BEGIN = 'MIBE'
TELEMETRY_HOOK_MIXER_END = 'MIEN'
TELEMETRY_FIELD_INTERACTION_ID = 'idix'
TELEMETRY_FIELD_TARGET_ID = 'idtx'
TELEMETRY_FIELD_TARGET_TYPE = 'tptx'
TELEMETRY_FIELD_SOURCE = 'sorc'
TELEMETRY_FIELD_OUTCOME = 'outc'
TELEMETRY_FIELD_GROUP_ID = 'idgr'
TELEMETRY_HOOK_MAPPING = {
 ('Process_SI', True): 'TELEMETRY_HOOK_SI_BEGIN', 
 ('Running', False): 'TELEMETRY_HOOK_MIXER_BEGIN', 
 ('Remove_SI', True): 'TELEMETRY_HOOK_SI_END', 
 ('Done', False): 'TELEMETRY_HOOK_MIXER_END'}
writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_INTERACTION)
interactions_archive_schema = GsiGridSchema(label='Interaction Log', sim_specific=True)
interactions_archive_schema.add_field('affordance', label='Affordance')
interactions_archive_schema.add_field('phase', label='Phase')
interactions_archive_schema.add_field('target', label='Target')
interactions_archive_schema.add_field('context', label='Context')
interactions_archive_schema.add_field('progress', label='Progress')
interactions_archive_schema.add_field('message', label='Message')
interactions_archive_schema.add_field('group_id', label='Group ID')
archiver = GameplayArchiver('interactions', interactions_archive_schema, enable_archive_by_default=True,
  max_records=200,
  add_to_archive_enable_functions=True)
_INTERACTION_LOG_FORMAT = '{sim:>24}, {phase:>16}, {name:>32}, {target:>32}, {progress:>8}, {context}, {msg}'
_POSTURE_LOG_FORMAT = '{sim:>24}, {phase:>16}, {name:>32}, {target:>32},         , {msg}'

def _get_csv_friendly_string(s):
    if s is not None:
        s = s.replace('"', "'")
        if ',' in s:
            s = '"{}"'.format(s)
        return s
    return 'None'


def _get_sim_name(sim):
    if sim is not None:
        s = '{}[{}]'.format(sim.full_name, standard_brief_id_repr(sim.id))
        s = _get_csv_friendly_string(s)
        return s
    return 'None'


def _get_object_name(obj):
    if obj is not None:
        return _get_csv_friendly_string('{}'.format(obj))
    return 'None'


def log_affordance(phase, affordance, context, msg=None):
    logger.info(_INTERACTION_LOG_FORMAT.format(phase=phase,
      name=('{}'.format(affordance.__name__)),
      sim=(_get_sim_name(context.sim)),
      target='',
      progress='',
      context='',
      msg=(_get_csv_friendly_string(msg) or '')))
    archive_data = {'affordance':affordance.__name__, 
     'phase':phase}
    if msg:
        archive_data['message'] = msg
    sim_id = context.sim.id if context.sim is not None else 0
    archiver.archive(data=archive_data, object_id=sim_id)


def log_interaction(phase, interaction, msg=None):
    if archiver.enabled:
        if interaction.is_super:
            progress = str(interaction.pipeline_progress).split('.', 1)[-1]
        else:
            progress = ''
        source = str(interaction.context.source).split('.', 1)[-1]
        priority = str(interaction.priority).split('.', 1)[-1]
        sim_name = _get_sim_name(interaction.sim)
        interaction_name = getattr(interaction, 'name_override', interaction.affordance.__name__)
        interaction_name = '{}({})'.format(interaction_name, interaction.id)
        logger.info(_INTERACTION_LOG_FORMAT.format(phase=phase,
          name=interaction_name,
          sim=sim_name,
          target=(_get_object_name(interaction.target)),
          progress=progress,
          context=('{}-{}'.format(source, priority)),
          msg=(_get_csv_friendly_string(msg) or '')))
        target_str = str(interaction.target)
        carry_target = interaction.carry_target
        if carry_target is not None:
            target_str = target_str + ' Carrying:{}'.format(str(carry_target))
        create_target = interaction.create_target
        if create_target is not None:
            target_str = target_str + ' Creating:{}'.format(str(create_target))
        archive_data = {'affordance':interaction_name, 
         'phase':phase, 
         'target':target_str, 
         'context':'{}, {}'.format(source, priority), 
         'progress':progress, 
         'group_id':interaction.group_id}
        if msg:
            archive_data['message'] = msg
        archiver.archive(data=archive_data, object_id=(interaction.sim.id if interaction.sim is not None else 0))
    else:
        if interaction.sim is not None:
            if interaction.sim.interaction_logging:
                log_queue_automation(interaction.sim)
        hook_tag = TELEMETRY_HOOK_MAPPING.get((phase, interaction.is_super))
        if hook_tag is not None and interaction.visible:
            with telemetry_helper.begin_hook(writer, hook_tag, sim=(interaction.sim)) as (hook):
                hook.write_guid(TELEMETRY_FIELD_INTERACTION_ID, interaction.guid64)
                hook.write_int(TELEMETRY_FIELD_SOURCE, interaction.source)
                hook.write_int(TELEMETRY_FIELD_GROUP_ID, interaction.group_id)
                target = interaction.target
                if target is not None:
                    hook.write_int(TELEMETRY_FIELD_TARGET_ID, target.id)
                    hook.write_int(TELEMETRY_FIELD_TARGET_TYPE, target.definition.id)
                outcome_result = interaction.global_outcome_result
                if outcome_result is not None:
                    hook.write_int(TELEMETRY_FIELD_OUTCOME, interaction.global_outcome_result)


def log_queue_automation(sim=None):
    if sim is None or sim.client is None:
        return False
    else:
        output = sims4.commands.AutomationOutput(sim.client.id)
        if sim.queue.running is None:
            output('[AreaInstanceInteraction] SimInteractionData; SimId:%d, SICount:%d, RunningId:None' % (
             sim.id, len(sim.si_state)))
        else:
            output('[AreaInstanceInteraction] SimInteractionData; SimId:%d, SICount:%d, RunningId:%d, RunningClass:%s' % (
             sim.id, len(sim.si_state), sim.queue.running.id, sim.queue.running.__class__.__name__))
    for si in sim.si_state.sis_actor_gen():
        output('[AreaInstanceInteraction] SimSuperInteractionData; Id:%d, Class:%s' % (si.id, si.__class__.__name__))


def log_posture(phase, posture, msg=None):
    if not archiver.enabled:
        return
    logger.info(_POSTURE_LOG_FORMAT.format(phase=phase,
      name=('{}({})'.format(posture.name, hex(posture.id))),
      sim=(_get_sim_name(posture.sim)),
      target=(_get_object_name(posture.target)),
      msg=(_get_csv_friendly_string(msg) or '')))
    archive_data = {'affordance':posture.posture_type.__name__, 
     'phase':phase, 
     'target':str(posture.target)}
    if msg:
        archive_data['message'] = msg
    archiver.archive(data=archive_data, object_id=(posture.sim.id))


interactions_outcome_archive_schema = GsiGridSchema(label='Interaction Outcome Log')
interactions_outcome_archive_schema.add_field('actor', label='Actor')
interactions_outcome_archive_schema.add_field('affordance', label='Affordance')
interactions_outcome_archive_schema.add_field('target', label='Target')
interactions_outcome_archive_schema.add_field('result', label='Result')
interactions_outcome_archive_schema.add_field('sim_buff_modifier', label='Actor Modifier')
interactions_outcome_archive_schema.add_field('chance_modification', label='Chance Modification')
interactions_outcome_archive_schema.add_field('success_chance', label='Success Chance')
interactions_outcome_archive_schema.add_field('outcome_type', label='Outcome Type')
interactions_outcome_archive_schema.add_field('message', label='Message')
outcome_archiver = GameplayArchiver('interactionOutcomes', interactions_outcome_archive_schema, add_to_archive_enable_functions=True)
sim_interactions_outcome_archive_schema = GsiGridSchema(label='Interaction Outcome Log Sim', sim_specific=True)
sim_interactions_outcome_archive_schema.add_field('actor', label='Actor')
sim_interactions_outcome_archive_schema.add_field('affordance', label='Affordance')
sim_interactions_outcome_archive_schema.add_field('target', label='Target')
sim_interactions_outcome_archive_schema.add_field('result', label='Result')
sim_interactions_outcome_archive_schema.add_field('sim_buff_modifier', label='Actor Modifier')
sim_interactions_outcome_archive_schema.add_field('chance_modification', label='Chance Modification')
sim_interactions_outcome_archive_schema.add_field('success_chance', label='Success Chance')
sim_interactions_outcome_archive_schema.add_field('outcome_type', label='Outcome Type')
sim_interactions_outcome_archive_schema.add_field('message', label='Message')
sim_interactions_outcome_archive_schema.add_field('tested_outcome_index', label='Tested Index')
sim_interactions_outcome_archive_schema.add_field('potential_outcome_index', label='Potential Index')
sim_interactions_outcome_archive_schema.add_field('fallback_outcome_index', label='Fallback Index')
sim_outcome_archiver = GameplayArchiver('SimInteractionOutcomes', sim_interactions_outcome_archive_schema, add_to_archive_enable_functions=True)

def create_tested_outcome_message(selected_outcome, weights=None):
    msg = '-------- Selected Outcome: -----\n' + str(selected_outcome).replace(',', '\n')
    if weights is not None:
        weight_part = '------- Weights: ------\n' + '\n\n'.join(map(str, weights))
        msg += '\n\n' + weight_part
    return msg


def log_interaction_outcome(interaction, outcome, outcome_type, success_chance=None, is_tested_outcome=False, msg=None):
    try:
        sim = interaction.sim
        sim_name = _get_sim_name(sim)
        if interaction.target_type & interactions.TargetType.TARGET:
            target = interaction.target
        else:
            target = sim
        archive_data = {'actor':sim_name,  'affordance':type(interaction).__name__, 
         'target':_get_object_name(target), 
         'result':interaction.global_outcome_result.__str__(), 
         'skill_multiplier':interaction.get_skill_multiplier(interaction.success_chance_multipliers, sim), 
         'outcome_type':outcome_type}
        if success_chance is not None:
            archive_data['success_chance'] = success_chance
            archive_data['sim_buff_modifier'] = sim.get_actor_success_modifier(interaction.affordance, interaction.get_resolver()) if sim is not None else 0
            archive_data['chance_modification'] = sim.get_success_chance_modifier() if sim is not None else 0
        if is_tested_outcome:
            outcome_found = False
            for tested_index, tested_outcome in enumerate(outcome._tested_outcomes):
                for potential_index, potential_outcome in enumerate(tested_outcome.potential_outcomes):
                    if potential_outcome.outcome is outcome._selected_outcome:
                        outcome_found = True
                        archive_data['tested_outcome_index'] = tested_index
                        archive_data['potential_outcome_index'] = potential_index
                        break

                if outcome_found:
                    break

            for fallback_index, fallback_outcome in enumerate(outcome._fallback_outcomes):
                if fallback_outcome.outcome is outcome._selected_outcome:
                    archive_data['fallback_outcome_index'] = fallback_index
                    break

        if msg:
            archive_data['message'] = msg
        if sim is not None:
            sim_outcome_archiver.archive(data=archive_data, object_id=(sim.id))
        outcome_archiver.archive(data=archive_data, object_id=(sim.id if sim is not None else 0))
    except:
        logger.exception('Exception while attempting to log an interaction outcome:')