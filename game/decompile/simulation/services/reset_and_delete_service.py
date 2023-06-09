# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\services\reset_and_delete_service.py
# Compiled at: 2019-10-23 22:11:56
# Size of source mod 2**32: 28545 bytes
from objects.object_enums import ResetReason
from scheduling import HardStopError
import enum, gsi_handlers, services, sims4.log, sims4.service_manager
logger = sims4.log.Logger('Reset')

class _Stage(enum.Int, export=False):
    PENDING = ...
    EARLY_DETACHMENT = ...
    HARD_STOP_ELEMENTS = ...
    HARD_STOP_PURGATORY = ...
    SEND_RESET_OP = ...
    INTERNAL_STATE_RESET = ...
    RESTART_PURGATORY = ...
    PROCESSING_COUNT = ...
    DESTROY = ...
    RESTART = ...


def can_be_destroyed(obj):
    return obj.id in obj.manager


def has_been_destroyed(obj):
    return obj.id not in obj.manager


class ResetRecord:

    def __init__(self, obj, reset_reason=ResetReason.RESET_EXPECTED, source=None, cause=None, **params):
        if not can_be_destroyed(obj):
            logger.error('Creating a ResetRecord for a deleted obj:{}', obj, owner='sscholl')
            if gsi_handlers.reset_handlers.reset_log_archiver.enabled:
                gsi_handlers.reset_handlers.archive_reset_log_entry('RESETTING DELETED OBJECT', obj,
                  reset_reason, source, cause, include_callstack=True)
        elif not obj.can_reset:
            logger.error("Creating a ResetRecord for something that can't reset:{}", obj, owner='sscholl')
            if gsi_handlers.reset_handlers.reset_log_archiver.enabled:
                gsi_handlers.reset_handlers.archive_reset_log_entry("RESETTING THING THAT CAN'T BE RESET", obj,
                  reset_reason, source, cause, include_callstack=True)
        self.obj = obj
        self.reset_reason = reset_reason
        self.params = params
        self.stage = _Stage.PENDING
        self.is_being_processed = False
        self.elements = []
        self.source = source
        self.cause = cause

    def __repr__(self):
        return '<{}, reason:{}, stage:{}, being_processed:{}, source:{}, cause:{}'.format(self.obj, self.reset_reason, self.stage, self.is_being_processed, self.source, self.cause)


class ResetAndDeleteService(sims4.service_manager.Service):

    def __init__(self):
        self._all_reset_records = {}
        self._staged_records = []
        for stage in range(_Stage.PROCESSING_COUNT):
            self._staged_records.insert(stage, [])

        self._is_processing = False
        self._master_controller_sims = set()
        self._build_buy_reset_sims = None

    def _get_reset_record(self, obj):
        return self._all_reset_records.get(obj, None)

    def _add_new_record(self, record):
        logger.assert_log((self._get_reset_record(record.obj) is None), ('Attempting to create duplicate ResetRecord for {}'.format(record.obj)),
          owner='sscholl')
        self._all_reset_records[record.obj] = record
        self._staged_records[record.stage].append(record)

    def _restage_record(self, record, append=True):
        if append:
            self._staged_records[record.stage].append(record)
        else:
            self._staged_records[record.stage].insert(0, record)

    def _change_record_stage(self, record, new_stage):
        self._staged_records[record.stage].remove(record)
        record.stage = new_stage
        self._staged_records[new_stage].append(record)

    def trigger_destroy(self, obj, source=None, cause=None, **kwargs):
        (self.trigger_reset)(obj, ResetReason.BEING_DESTROYED, source=source, cause=cause, **kwargs)

    def trigger_reset(self, obj, reset_reason, source=None, cause=None, **kwargs):
        new_record = ResetRecord(obj, reset_reason, source, cause, **kwargs)
        is_new = self._add_or_update_record(new_record)
        if is_new:
            if reset_reason == ResetReason.RESET_ON_ERROR:
                logger.callstack('Resetting:{}', obj, level=(sims4.log.LEVEL_ERROR), owner='sscholl')
            self._collect_dependencies(new_record)
        self.start_processing()

    def trigger_batch_reset(self, objs, reset_reason=ResetReason.RESET_EXPECTED, source=None, cause=None):
        new_records = []
        for obj in objs:
            new_record = ResetRecord(obj, reset_reason, source, cause)
            is_new = self._add_or_update_record(new_record)
            if is_new:
                new_records.append(new_record)

        for record in new_records:
            self._collect_dependencies(record)

        self.start_processing()

    def trigger_batch_destroy(self, objs):
        self.trigger_batch_reset(objs, ResetReason.BEING_DESTROYED)

    def get_reset_reason(self, obj):
        record = self._get_reset_record(obj)
        if record is None:
            return ResetReason.NONE
        return record.reset_reason

    def _add_or_update_record(self, new_record):
        if new_record.obj.id not in new_record.obj.manager:
            logger.error('Attempting to add a record for a deleted obj:{}', (new_record.obj), owner='sscholl')
            return False
        else:
            if not new_record.obj.can_reset:
                logger.error("Attempting to add a ResetRecord for something that can't be reset:{}", (new_record.obj), owner='sscholl')
                return False
                extant_record = self._get_reset_record(new_record.obj)
                if extant_record is None:
                    self._add_new_record(new_record)
                    logger.info('Reset:{}', new_record)
                    if gsi_handlers.reset_handlers.reset_log_archiver.enabled:
                        gsi_handlers.reset_handlers.archive_reset_log_record('Reset', new_record, include_callstack=True)
                    new_record.obj.on_reset_notification(new_record.reset_reason)
                    return True
            elif extant_record.reset_reason < new_record.reset_reason:
                extant_record.reset_reason = new_record.reset_reason
                extant_record.source = new_record.source
                extant_record.cause = new_record.cause
                extant_record.is_being_processed or self._change_record_stage(extant_record, _Stage.PENDING)
            else:
                extant_record.stage = _Stage.PENDING
            logger.info('Updated:{}', extant_record)
            if gsi_handlers.reset_handlers.reset_log_archiver.enabled:
                gsi_handlers.reset_handlers.archive_reset_log_record('Updated', extant_record, include_callstack=True)
            extant_record.obj.on_reset_notification(extant_record.reset_reason)
        return False

    def _collect_dependencies(self, root_record):
        logger.assert_log((self._get_reset_record(root_record.obj) is not None), 'Root record must have already been added to the service.',
          owner='sscholl')
        to_collect = [
         root_record]
        while to_collect:
            record = to_collect.pop()
            try:
                for element in record.obj.on_reset_get_elements_to_hard_stop(record.reset_reason):
                    if element not in record.elements:
                        record.elements.append(element)

                reset_records = []
                record.obj.on_reset_get_interdependent_reset_records(record.reset_reason, reset_records)
                for dependent_record in reset_records:
                    is_new = self._add_or_update_record(dependent_record)
                    if is_new:
                        to_collect.append(dependent_record)

            except BaseException:
                logger.exception('Unexpected exception while collecting reset dependencies for record:{}', record, owner='sscholl')

    def start_processing(self):
        if self._is_processing:
            return
        self._process()

    def _process(self):
        logger.debug('Start Processing')
        if gsi_handlers.reset_handlers.reset_log_archiver.enabled:
            gsi_handlers.reset_handlers.archive_reset_log_message('Start Processing')
        self._is_processing = True
        hard_stop_error = False
        master_controller = services.get_master_controller()
        try:
            try:
                if master_controller is not None:
                    master_controller.on_reset_begin()
                    while self._all_reset_records:
                        for stage in range(_Stage.PROCESSING_COUNT):
                            if self._staged_records[stage]:
                                self._process_one_record(stage)
                                break

            except HardStopError:
                hard_stop_error = True
                logger.debug('Hard Stop out of Processing')
                if gsi_handlers.reset_handlers.reset_log_archiver.enabled:
                    gsi_handlers.reset_handlers.archive_reset_log_message('Hard Stop out of Processing')
                raise
            except BaseException:
                logger.exception('Unexpected exception while processing ResetAndDeleteService.')

        finally:
            self._is_processing = False
            hard_stop_error or logger.debug('Stop Processing')
            if gsi_handlers.reset_handlers.reset_log_archiver.enabled:
                gsi_handlers.reset_handlers.archive_reset_log_message('Stop Processing')

        logger.debug('Poke MasterController:{}', self._master_controller_sims)
        if gsi_handlers.reset_handlers.reset_log_archiver.enabled:
            gsi_handlers.reset_handlers.archive_reset_log_message('Poke MasterController:{}'.format(self._master_controller_sims))
        try:
            sims = self._master_controller_sims
            self._master_controller_sims = set()
            if master_controller is not None:
                (master_controller.on_reset_end)(*sims)
        except BaseException:
            logger.exception('Unexpected exception in master_controller.on_reset_end.')

    def _process_one_record(self, stage):
        try:
            try:
                record = self._staged_records[stage].pop(0)
                record.is_being_processed = True
                append_record = True
                update_stage = record.stage
                if record.stage == _Stage.PENDING:
                    update_stage = _Stage.EARLY_DETACHMENT
                else:
                    if record.stage == _Stage.EARLY_DETACHMENT:
                        if record.elements:
                            update_stage = _Stage.HARD_STOP_ELEMENTS
                        else:
                            update_stage = _Stage.HARD_STOP_PURGATORY
                    elif record.stage == _Stage.HARD_STOP_ELEMENTS:
                        update_stage = record.elements or _Stage.HARD_STOP_PURGATORY
                    else:
                        if record.stage == _Stage.HARD_STOP_PURGATORY:
                            update_stage = _Stage.SEND_RESET_OP
                        else:
                            if record.stage == _Stage.SEND_RESET_OP:
                                update_stage = _Stage.INTERNAL_STATE_RESET
                            else:
                                if record.stage == _Stage.INTERNAL_STATE_RESET:
                                    if record.reset_reason == ResetReason.BEING_DESTROYED:
                                        update_stage = _Stage.DESTROY
                                    else:
                                        update_stage = _Stage.RESTART_PURGATORY
                                elif record.stage == _Stage.RESTART_PURGATORY:
                                    update_stage = _Stage.RESTART
                                else:
                                    raise RuntimeError('In advance, unexpected record stage:{}'.format(record))
                record.stage = update_stage
                if record.stage == _Stage.EARLY_DETACHMENT:
                    logger.debug('on_reset_early_detachment for record:{}', record)
                    if gsi_handlers.reset_handlers.reset_log_archiver.enabled:
                        gsi_handlers.reset_handlers.archive_reset_log_record('Early Detach', record)
                    record.obj.on_reset_early_detachment(record.reset_reason)
                else:
                    if record.stage == _Stage.HARD_STOP_ELEMENTS:
                        element = record.elements.pop(0)
                        logger.debug('trigger_hard_stop:{} for record:{}', element.tracing_repr(), record)
                        if gsi_handlers.reset_handlers.reset_log_archiver.enabled:
                            gsi_handlers.reset_handlers.archive_reset_log_entry('Hard Stop', element.tracing_repr(), record.reset_reason, record.obj)
                        element.trigger_hard_stop()
                    else:
                        if record.stage == _Stage.HARD_STOP_PURGATORY:
                            pass
                        elif record.stage == _Stage.SEND_RESET_OP:
                            record.obj.on_reset_send_op(record.reset_reason)
                        else:
                            if record.stage == _Stage.INTERNAL_STATE_RESET:
                                logger.debug('on_reset_internal_state for record:{}', record)
                                if gsi_handlers.reset_handlers.reset_log_archiver.enabled:
                                    gsi_handlers.reset_handlers.archive_reset_log_record('Internal State', record)
                                record.obj.on_reset_internal_state(record.reset_reason)
                            else:
                                if record.stage == _Stage.DESTROY:
                                    logger.debug('remove for record:{}', record)
                                    if gsi_handlers.reset_handlers.reset_log_archiver.enabled:
                                        gsi_handlers.reset_handlers.archive_reset_log_record('Destroy', record)
                                    (record.obj.on_reset_destroy)(**record.params)
                                else:
                                    if record.stage == _Stage.RESTART_PURGATORY:
                                        pass
                                    elif record.stage == _Stage.RESTART:
                                        logger.debug('on_reset_restart for record:{}', record)
                                        if gsi_handlers.reset_handlers.reset_log_archiver.enabled:
                                            gsi_handlers.reset_handlers.archive_reset_log_record('Restart', record)
                                        handled = record.obj.on_reset_restart()
                                        if not handled:
                                            self._master_controller_sims.add(record.obj)
                                            if self._build_buy_reset_sims is not None:
                                                self._build_buy_reset_sims.add(record.obj)
                                    else:
                                        raise RuntimeError('In update, unexpected record stage:{}'.format(record))
            except HardStopError:
                if update_stage == _Stage.HARD_STOP_ELEMENTS:
                    append_record = False
                    raise
                else:
                    logger.exception('HardStopError processing ResetRecord:{}. This will result in a partially reset object', record, owner='sscholl')
            except BaseException:
                logger.exception('Exception processing ResetRecord:{}. This will result in a partially reset object', record, owner='sscholl')

        finally:
            record.is_being_processed = False
            if record.stage == _Stage.RESTART or record.stage == _Stage.DESTROY:
                self._all_reset_records.pop(record.obj)
            else:
                self._restage_record(record, append=append_record)

    def on_build_buy_enter(self):
        self._build_buy_reset_sims = set()

    def on_build_buy_exit(self):
        if self._build_buy_reset_sims:
            self.trigger_batch_reset(self._build_buy_reset_sims, ResetReason.RESET_EXPECTED, 'Sims Reset During Build Buy. Resetting again on build buy exit.')
        self._build_buy_reset_sims = None