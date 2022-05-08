from unredoable import UnredoableObject
import pytest


@pytest.fixture
def unredoable() -> UnredoableObject:
    return UnredoableObject(int(), max_stack_depths=20)


def _add(_unredoable):
    _unredoable.push_state_to_undo_stack()
    _unredoable.obj += 1


_undo = lambda unredoable: unredoable.undo()
_redo = lambda unredoable: unredoable.redo()


def test___str__(unredoable):
    assert str(unredoable) == 'UnredoableObject: 0 | undo stack depth: 0, redo stack depth: 0 | max stack depth: 20'


@pytest.mark.parametrize(
    'commands,expected', [
        (
                [_add, _undo],
                True
        ),
        (
                [],
                False
        ),
        (
                [_add],
                False
        ),
        (
                [_add, _add, _undo, _undo, _redo],
                True
        ),
        (
                [_add, _add, _undo, _undo, _redo, _redo],
                False
        ),
    ]
)
def test_redoable(commands, expected, unredoable):
    for cmd in commands:
        cmd(unredoable)

    assert unredoable.is_redoable == expected


@pytest.mark.parametrize(
    'commands,expected', [
        (
                [_add],
                True
        ),
        (
                [],
                False
        ),
        (
                [_add, _undo],
                False
        ),
        (
                [_add, _add, _undo],
                True
        ),
        (
                [_add, _add, _undo, _undo],
                False
        ),
        (
                [_add, _undo, _redo],
                True
        ),
        (
                [_add, _add, _undo, _redo, _undo],
                True
        ),
        (
                [_add, _add, _undo, _undo, _redo],
                True
        ),
    ]
)
def test_undoable(commands, expected, unredoable):
    for cmd in commands:
        cmd(unredoable)

    assert unredoable.is_undoable == expected


@pytest.mark.parametrize('commands,expected', [
    ([_add], 0),
    ([_add, _add], 1),
    ([_add, _add, _undo], 0),
])
def test_undo(commands, expected, unredoable):
    for cmd in commands:
        cmd(unredoable)

    unredoable.undo()

    assert unredoable.obj == expected


@pytest.mark.parametrize('commands,expected', [
    ([_add], 1),
    ([_add, _add], 2),
    ([_add, _add, _undo], 1),
    ([_add, _add, _undo, _redo], 2),
])
def test_redo(commands, expected, unredoable):
    for cmd in commands:
        cmd(unredoable)

    unredoable.undo()
    unredoable.redo()

    assert unredoable.obj == expected