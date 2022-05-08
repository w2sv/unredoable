from unredoable import Unredoable
import pytest


@pytest.fixture
def unredoable() -> Unredoable:
    return Unredoable(int(), max_stack_depths=20, craft_deep_copies=False)


def _push_state_and_alter_obj(_unredoable):
    _unredoable.push_state()
    _unredoable.obj += 1


_undo = lambda unredoable: unredoable.undo()
_redo = lambda unredoable: unredoable.redo()


def test_raising_on_empty_undo_stack():
    unredoable = Unredoable(int(), max_stack_depths=10)

    with pytest.raises(AttributeError):
        unredoable.undo()


def test_raising_on_empty_redo_stack():
    unredoable = Unredoable(int(), max_stack_depths=10)

    with pytest.raises(AttributeError):
        unredoable.redo()


def test_call_forwarding(unredoable):
    _ = unredoable.numerator


################################
# Operation Feasibility checks #
################################

@pytest.mark.parametrize(
    'commands,expected', [
        (
                [_push_state_and_alter_obj],
                True
        ),
        (
                [],
                False
        ),
        (
                [_push_state_and_alter_obj, _undo],
                False
        ),
        (
                [_push_state_and_alter_obj, _push_state_and_alter_obj, _undo],
                True
        ),
        (
                [_push_state_and_alter_obj, _push_state_and_alter_obj, _undo, _undo],
                False
        ),
        (
                [_push_state_and_alter_obj, _undo, _redo],
                True
        ),
        (
                [_push_state_and_alter_obj, _push_state_and_alter_obj, _undo, _redo, _undo],
                True
        ),
        (
                [_push_state_and_alter_obj, _push_state_and_alter_obj, _undo, _undo, _redo],
                True
        ),
    ]
)
def test_undoable(commands, expected, unredoable):
    for cmd in commands:
        cmd(unredoable)

    assert unredoable.is_undoable == expected


@pytest.mark.parametrize(
    'commands,expected', [
        (
                [_push_state_and_alter_obj, _undo],
                True
        ),
        (
                [],
                False
        ),
        (
                [_push_state_and_alter_obj],
                False
        ),
        (
                [_push_state_and_alter_obj, _push_state_and_alter_obj, _undo, _undo, _redo],
                True
        ),
        (
                [_push_state_and_alter_obj, _push_state_and_alter_obj, _undo, _undo, _redo, _redo],
                False
        ),
    ]
)
def test_redoable(commands, expected, unredoable):
    for cmd in commands:
        cmd(unredoable)

    assert unredoable.is_redoable == expected


#############
# Unredoing #
#############

@pytest.mark.parametrize('commands,expected', [
    ([_push_state_and_alter_obj], 0),
    ([_push_state_and_alter_obj, _push_state_and_alter_obj], 1),
    ([_push_state_and_alter_obj, _push_state_and_alter_obj, _undo], 0),
])
def test_undo(commands, expected, unredoable):
    for cmd in commands:
        cmd(unredoable)

    unredoable.undo()

    assert unredoable.obj == expected


@pytest.mark.parametrize('commands,expected', [
    ([_push_state_and_alter_obj], 1),
    ([_push_state_and_alter_obj, _push_state_and_alter_obj], 2),
    ([_push_state_and_alter_obj, _push_state_and_alter_obj, _undo], 1),
    ([_push_state_and_alter_obj, _push_state_and_alter_obj, _undo, _redo], 2),
])
def test_redo(commands, expected, unredoable):
    for cmd in commands:
        cmd(unredoable)

    unredoable.undo()
    unredoable.redo()

    assert unredoable.obj == expected


########
# Misc #
########

def test___str__(unredoable):
    assert str(unredoable) == 'Unredoable | wrapped obj: 0 | undo stack depth: 0, redo stack depth: 0 | max stack depth: 20'