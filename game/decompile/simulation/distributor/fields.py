# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\distributor\fields.py
# Compiled at: 2017-12-08 19:04:54
# Size of source mod 2**32: 12408 bytes
from distributor.rollback import ProtocolBufferRollback
from sims4.log import LEVEL_EXCEPTION
import distributor.system, enum
__unittest__ = 'test.distributor.fields_test'

class Field:
    _distributed_fields = {}
    _OBJECT_DIR = set(dir(object))
    _NO_DEFAULT = object()

    class Priority(enum.Int, export=False):
        LOW = -1
        NORMAL = 0
        HIGH = 1

    def __init__(self, getter=None, setter=None, op=None, priority: Priority=Priority.NORMAL, default=_NO_DEFAULT, should_distribute_fn=None):
        self._get = getter
        self._set = setter
        self._op = op
        self._priority = priority
        self._default = default
        self._should_distribute_fn = should_distribute_fn

    def __call__(self, getter):
        if self._get is not None:
            raise Exception('getter has already been set')
        return self.getter(getter)

    def get_op(self, inst, for_create=False, value=_NO_DEFAULT):
        op = self._op
        if op is None:
            return
        try:
            if value is Field._NO_DEFAULT:
                value = self.__get__(inst, for_create=False)
            if for_create:
                if value == self._default:
                    return
            return op(value)
        except:
            msg = 'Error while attempting to create op {} for {}:'.format(op, inst)
            distributor.system.logger.callstack(msg, level=LEVEL_EXCEPTION)
            distributor.system.logger.exception(msg)
            return

    def __get__(self, inst, owner=None, *, for_create=False):
        if inst is None:
            return self
        return self._get(inst)

    def __set__(self, inst, value):
        if self._set is None:
            raise AttributeError("can't set read-only field")
        ret = self._set(inst, value)
        _distributor = distributor.system.Distributor.instance()
        if _distributor.client is not None:
            if self._should_distribute(inst):
                op = self.get_op(inst)
                if op is not None:
                    _distributor.add_op(inst, op)
        return ret

    def getter(self, getter):
        return type(self)(getter, self._set, self._op, self._priority, self._default, self._should_distribute_fn)

    def setter(self, setter):
        return type(self)(self._get, setter, self._op, self._priority, self._default, self._should_distribute_fn)

    def get_resend(self):

        def _resend(inst, value=Field._NO_DEFAULT):
            _distributor = distributor.system.Distributor.instance()
            if _distributor.client is not None:
                if self._should_distribute(inst):
                    op = self.get_op(inst, value=value)
                    if op is not None:
                        _distributor.add_op(inst, op)

        return _resend

    @staticmethod
    def _get_distributed_fields(obj):
        object_type = type(obj)
        component_definitions = getattr(obj, 'component_definitions', None)
        key = (object_type, component_definitions)
        distributed_fields = Field._distributed_fields.get(key)
        if distributed_fields is None:
            distributed_fields = []
            for name in set(dir(object_type)) - Field._OBJECT_DIR:
                field = getattr(object_type, name, None)
                if isinstance(field, Field):
                    distributed_fields.append((None, field))

            if component_definitions:
                for component in obj.components:
                    for _, field in Field._get_distributed_fields(component):
                        distributed_fields.append((component.INAME, field))

            distributed_fields.sort(reverse=True, key=(lambda t: t[1]._priority))
            Field._distributed_fields[key] = distributed_fields
        return distributed_fields

    @staticmethod
    def fill_in_operation_list(obj, operations, for_create=False):
        for op in Field.get_operations_gen(obj, for_create=for_create):
            with ProtocolBufferRollback(operations) as (op_msg):
                op.write(op_msg)

    @staticmethod
    def get_operations_gen(obj, for_create=False):
        distributed_fields = Field._get_distributed_fields(obj)
        for component_name, field in distributed_fields:
            field_owner = obj
            if component_name is not None:
                field_owner = getattr(obj, component_name)
            op = field.get_op(field_owner, for_create=for_create)
            if op is not None:
                yield op

    def _should_distribute(self, inst):
        if inst.valid_for_distribution:
            if self._should_distribute_fn is None or self._should_distribute_fn(inst):
                return True
        return False


class ComponentField(Field):

    def __set__(self, inst, value):
        if self._set is None:
            raise AttributeError("can't set read-only field")
        ret = self._set(inst, value)
        _distributor = distributor.system.Distributor.instance()
        if _distributor.client is not None:
            if self._should_distribute(inst.owner):
                op = self.get_op(inst)
                if op is not None:
                    _distributor.add_op(inst.owner, op)
        return ret

    def get_resend(self):

        def _resend(component):
            _distributor = distributor.system.Distributor.instance()
            if _distributor.client is not None:
                if self._should_distribute(component.owner):
                    op = self.get_op(component)
                    if op is not None:
                        _distributor.add_op(component.owner, op)

        return _resend


class ChildField:

    def __init__(self, getter=None, setter=None, parent=None):
        self._get = getter
        self._set = setter
        self._parent = parent

    def __call__(self, getter):
        if self._get is not None:
            raise Exception('getter has already been set')
        return type(self)(getter, self._set, self._parent)

    def __get__(self, inst, owner=None):
        if inst is None:
            return self
        return self._get(inst)

    def __set__(self, inst, value):
        if self._set is None:
            raise AttributeError("can't set read-only child field")
        ret = self._set(inst, value)
        self._parent.__set__(inst, self._parent.__get__(inst))
        return ret

    def getter(self, method):
        return type(self)(method, self._set, self._parent)

    def setter(self, method):
        return type(self)(self._get, method, self._parent)