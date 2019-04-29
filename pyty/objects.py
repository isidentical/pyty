from __future__ import annotations

from dataclasses import dataclass, field
from dis import get_instructions
from inspect import getcallargs
from queue import SimpleQueue
from types import CodeType, FunctionType
from typing import Any, Dict, List, Optional, Tuple

BUILTINS = __import__("builtins").__dict__

NSItem = Dict[str, Any]
FORBIDDEN = {"__qualname__"}


@dataclass
class Namespace:
    n_locals: NSItem = field(default_factory=dict)
    n_globals: NSItem = field(default_factory=dict)
    n_builtins: NSItem = field(default_factory=BUILTINS.copy, repr=False)


@dataclass
class Frame:
    code: CodeType
    namespace: Namespace = field(default_factory=Namespace)

    block: List = field(default_factory=list)
    stack: SimpleQueue = field(default_factory=SimpleQueue)
    lasti: int = 0

    def __post_init__(self):
        self.instrset = get_instructions(self.code)

    def next_operation(self):
        return next(self.instrset)


@dataclass
class Function:
    code: CodeType
    defaults: Tuple[Any, ...]
    runnervm: VM

    closure: Optional[type(_cell_factory())] = None

    def __post_init__(self):
        self.namespace = self.runnervm.get_ns()
        self.fn = FunctionType(
            self.code,
            self.namespace.n_globals,
            argdefs=self.defaults,
            closure=(
                tuple(self._cell_factory() for _ in self.closure)
                if self.closure
                else None
            ),
        )

    def __call__(self, *args, **kwargs):
        frame = Frame(self.code, self.runnervm.get_ns(getcallargs(*args, **kwargs)))
        self.runnervm.run(frame)

    @staticmethod
    def _cell_factory():
        # direct copy from cpython:3.8/types.py
        a = 1

        def f():
            nonlocal a

        return f.__closure__[0]
