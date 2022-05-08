from collections import deque
from copy import copy, deepcopy
from typing import Deque, TypeVar


_T = TypeVar('_T')


class Unredoable:
    """ Wrapper class adding undo & redo functionality to whatever kind of object
        implementing __copy__/__deepcopy__ """

    def __init__(self, obj: _T, max_stack_depths: int, craft_deep_copies=True):
        """ Parameters:
                obj: object getting wrapped and unresolvable calls will be forwarded to via __getattr__
                max_stack_depths: maximal number of obj copies to be respectively held by both undo & redo stack
                craft_deep_copies: whether to craft copies by calling __copy__ or __deepcopy__ """

        self.obj: _T = obj
        self._craft_deep_copies: bool = craft_deep_copies

        self._undo_stack: Deque[_T] = deque(maxlen=max_stack_depths)
        self._redo_stack: Deque[_T] = deque(maxlen=max_stack_depths)

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
        uppermost element from undo stack

        Raises:
            AttributeError if stack empty """

        self._push_state_to(self._redo_stack)
        try:
            self.obj = self._undo_stack.pop()
        except IndexError:
            raise AttributeError('Undo stack empty')

    def redo(self):
        """ Pushes current state to undo stack and set obj to popped
        uppermost element from redo stack

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
        return f'{self.__class__.__name__} | ' \
               f'wrapped obj: {self.obj} | ' \
               f'undo stack depth: {len(self._undo_stack)}, redo stack depth: {len(self._redo_stack)} | ' \
               f'max stack depth: {self._redo_stack.maxlen}'
