import stack
from stack import next_instruction, eval_program

import pytest


def test_next_instruction():
    program = next_instruction("push 1; pop; swap;")
    assert next(program) == "push 1"
    assert next(program) == "pop"
    assert next(program) == "swap"
    with pytest.raises(StopIteration):
        next(program)


def test_push_and_pop():
    assert eval_program("push 1; push 2; push 3;") == [1, 2, 3]
    assert eval_program("push 2; pop") == []
    with pytest.raises(IndexError):
        # IDEA: poping an empty list does nothing instead of index error?
        eval_program("pop")


def test_simple_operators():
    assert eval_program("push 10; push 20; add;") == [30]
    assert eval_program("push 10; push 5; subtract;") == [5]
    assert eval_program("push 10; push 20; subtract;") == [-10]
    assert eval_program("push 10; push 0; multiply;") == [0]
    assert eval_program("push 10; push 10; multiply;") == [100]
    assert eval_program("push 10; push 2; divide") == [5.0]
    assert eval_program("push 3; push 2; divide") == [1.5]
    with pytest.raises(IndexError):
        assert eval_program("push 1; add")
        assert eval_program("subtract; push 1")
        assert eval_program("push 1; push 2; pop; multiply")
        assert eval_program("divide")
    with pytest.raises(ZeroDivisionError):
        # IDEA: division by zero pushes nothing? halts program? pushes zero?
        assert eval_program("push 1; push 0; divide")


def test_complex_operators():
    assert eval_program("push 2; push 3; push 5; add; multiply") == [
        2 * (3 + 5)]
    assert eval_program("push 36; push 24; push 6; divide; divide;") == [
        36 / (24 / 6)]
    program = "push 10; push 4; subtract; push 6; push 2; subtract; multiply"
    assert eval_program(program) == [(10 - 4) * (6 - 2)]


def test_swap():
    assert eval_program("push 1; swap 0") == [1]
    assert eval_program("push 1; push 2; swap") == [2, 1]
    assert eval_program("push 1; push 2; swap 1") == [2, 1]
    assert eval_program("push 1; push 2; push 3; swap") == [1, 3, 2]
    assert eval_program("push 1; push 2; push 3; push 4; swap 3;") == [
        4, 2, 3, 1, ]
    with pytest.raises(IndexError):
        assert eval_program("swap")
        assert eval_program("push 1; swap")
        assert eval_program("push 1; push 2; swap 2")
        assert eval_program("push 1; push 2; push 3; swap 3")

