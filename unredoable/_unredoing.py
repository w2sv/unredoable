from abc import ABC, abstractmethod
from collections import deque
from copy import copy, deepcopy
from functools import wraps
from typing import Any, Callable, Deque, TypeVar, List


class _UnredoableBase(ABC):
    @abstractmethod
    def undo(self):
        """  """

    @abstractmethod
    def redo(self):
        """  """

    @property
    @abstractmethod
    def is_undoable(self) -> bool:
        """  """

    @property
    @abstractmethod
    def is_redoable(self) -> bool:
        """  """


class Unredoable(_UnredoableBase):
    """ Wrapper class adding undo & redo functionality to whatever kind of object
        implementing __copy__/__deepcopy__ """

    def __init__(self, obj: Any, max_stack_depths: int, craft_deep_copies=True):
        self.obj = obj
        self._craft_deep_copies = craft_deep_copies

        self._undo_stack: Deque[Any] = deque(maxlen=max_stack_depths)
        self._redo_stack: Deque[Any] = deque(maxlen=max_stack_depths)

    def __getattr__(self, item):
        """ Forward unresolvable calls to obj """

        return getattr(self.obj, item)

    #################
    # State pushing #
    #################
    def push_state(self):
        """ Pushes copy of current object to undo stack """

        self._push_state_to(self._undo_stack)

    def _push_state_to(self, stack: deque):
        stack.append(deepcopy(self.obj) if self._craft_deep_copies else copy(self.obj))

    ################################
    # Operation availability query #
    ################################
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
        """ Pushes current state to redo stack and set obj to popped
        uppermost element from undo stack """

        self._push_state_to(self._redo_stack)
        self.obj = self._undo_stack.pop()

    def redo(self):
        """ Pushes current state to undo stack and set obj to popped
        uppermost element from redo stack """

        self._push_state_to(self._undo_stack)
        self.obj = self._redo_stack.pop()

    ########
    # Misc #
    ########
    def __str__(self):
        return f'{self.__class__.__name__} | ' \
               f'wrapped obj: {self.obj} | ' \
               f'undo stack depth: {len(self._undo_stack)}, redo stack depth: {len(self._redo_stack)} | ' \
               f'max stack depth: {self._redo_stack.maxlen}'


class UnredoableAdministrator(_UnredoableBase, ABC):
    def __init__(self, *obj: Any, max_stack_depths: int):
        self._unredoables: List[Unredoable] = list(
            map(
                lambda _obj: Unredoable(
                    _obj,
                    max_stack_depths=max_stack_depths
                ),
                obj
            )
        )

    _Method = TypeVar('_Method', bound=Callable[..., Any])

    def state_pusher(method: _Method) -> _Method:  # type: ignore
        """ Method decorator pushing state of all unredoable objects
            before triggering decorated method """

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            for unredoable in self._unredoables:
                unredoable.push_state()
            return method(self, *args, **kwargs)
        return wrapper  # type: ignore

    ################################
    # Operation availability query #
    ################################
    @property
    def is_undoable(self) -> bool:
        return self._unredoables[0].is_undoable

    @property
    def is_redoable(self) -> bool:
        return self._unredoables[0].is_redoable

    #############
    # Execution #
    #############
    def undo(self):
        for unredoable in self._unredoables:
            unredoable.undo()

    def redo(self):
        for unredoable in self._unredoables:
            unredoable.redo()

    ########
    # Misc #
    ########
    def __str__(self):
        return ' || '.join(map(str, [super] + self._unredoables))  # type: ignore