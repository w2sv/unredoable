from abc import ABC
from collections import deque
from copy import copy, deepcopy
from functools import wraps
from typing import Any, Callable, Deque, Generic, TypeVar


_T = TypeVar('_T')
_FuncT = TypeVar('_FuncT', bound=Callable[..., Any])


class _Proxy(Generic[_T], ABC):
    def __init__(self, obj: _T):
        self.obj = obj

    def __getattr__(self, item):
        return getattr(self.obj, item)


class Unredoable(_Proxy[_T]):
    """ Wrapper class adding undo & redo functionality to whatever kind of object
        implementing __copy__/__deepcopy__ """

    def __init__(self, obj: _T, max_stack_depths: int, craft_deep_copies=True):
        """ Parameters:
                obj: object getting wrapped and unresolvable calls will be forwarded to via __getattr__
                max_stack_depths: maximal number of obj copies to be respectively held by both undo & redo stack
                craft_deep_copies: whether to craft copies by calling __copy__ or __deepcopy__ """

        super().__init__(obj)

        self._craft_deep_copies: bool = craft_deep_copies

        self._undo_stack: Deque[_T] = deque(maxlen=max_stack_depths)
        self._redo_stack: Deque[_T] = deque(maxlen=max_stack_depths)

    #################
    # State pushing #
    #################

    def push_state(self):
        """ Pushes copy of current object to undo stack """

        self._push_state_to(self._undo_stack)

    def state_pusher(self, f: _FuncT) -> _FuncT:
        @wraps(f)
        def wrapper(*args, **kwargs):
            self.push_state()
            return f(*args, **kwargs)
        return wrapper  # type: ignore

    def _push_state_to(self, stack: deque):
        stack.append(deepcopy(self.obj) if self._craft_deep_copies else copy(self.obj))

    ##########################
    # Operation availability #
    ##########################

    @property
    def is_undoable(self) -> bool:
        return bool(self._undo_stack)

    @property
    def is_redoable(self) -> bool:
        return bool(self._redo_stack)

    #############
    # Execution #
    #############

    def undo(self):
        """ Pushes current state to redo stack and sets obj to the uppermost
        popped element from undo stack

        Raises:
            AttributeError if stack empty """

        self._push_state_to(self._redo_stack)
        try:
            self.obj = self._undo_stack.pop()
        except IndexError:
            raise AttributeError('Undo stack empty')

    def redo(self):
        """ Pushes current state to undo stack and sets obj to uppermost
        popped element from redo stack

        Raises:
            AttributeError if stack empty """

        self._push_state_to(self._undo_stack)
        try:
            self.obj = self._redo_stack.pop()
        except IndexError:
            raise AttributeError('Redo stack empty')

    ########
    # Misc #
    ########

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return f'{self.__class__.__name__} | ' \
               f'wrapped obj: {self.obj} | ' \
               f'undo stack depth: {len(self._undo_stack)}, redo stack depth: {len(self._redo_stack)} | ' \
               f'max stack depth: {self._redo_stack.maxlen}'
