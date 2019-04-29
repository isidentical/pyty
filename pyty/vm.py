from opcode import opmap
from typing import Callable, Dict

from pyty.objects import Frame, Function, Namespace


class PyTy:
    operations: Dict[int, Callable] = {}

    def __init__(self):
        self.call_stack = []
        self.current_frame = None

    def run_single(self, frame):
        for operation in frame.instrset:
            operator = self.operations.get(operation.opname)
            if operator:
                result = operator(frame, operation.argval)
        return frame

    def get_ns(self, **kwargs):
        ns = Namespace()
        ns.n_globals = ns.n_locals = ns.n_builtins  # Global Scope
        ns.n_locals.update(kwargs)
        return ns

    @classmethod
    def register(cls, func):
        cls.operations[func.__name__.upper()] = func
        return func


@PyTy.register
def load_const(frame, arg):
    if arg is None:
        arg = frame.stack.get()
    frame.stack.put(arg)


@PyTy.register
def store_name(frame, arg):
    frame.namespace.n_locals[arg] = frame.stack.get()


@PyTy.register
def load_name(frame, arg):
    frame.stack.put(frame.namespace.n_locals[arg])


@PyTy.register
def binary_add(frame, arg):
    frame.stack.put(frame.stack.get() + frame.stack.get())


code = """
a = 3
b = 5
a + b
"""
code = compile(code, "<pyty>", "exec")
pyty = PyTy()
frame = pyty.run_single(Frame(code))
