# -*- coding: utf-8 -*-
from __future__ import division


class Instr(object):
    sigil_to_op = {
        '←': 'push', '→': 'pop',
        '↔': 'swap',
        '↑': 'jump',
        '+': 'add',
        '-': 'sub', '−': 'sub',  # A minus isn't the same thing as a hyphen!
        '*': 'mul', '×': 'mul',
        '/': 'div', '÷': 'div',
        '^': 'pow',
        '!': 'not', '¬': 'not',
    }

    def __init__(self, op, args=None, prefix=None):
        args = [] if args is None else args
        prefix = [] if prefix is None else prefix

        if op in Instr.sigil_to_op:
            op = Instr.sigil_to_op[op]
        self.op, self.args, self.prefix = op, args, prefix

    def __repr__(self):
        if self.prefix:
            return 'Instr({!r}, {!r}, {!r})'.format(
                self.op, self.args, self.prefix)
        elif self.args:
            return 'Instr({!r}, {!r})'.format(self.op, self.args)
        else:
            return 'Instr({!r})'.format(self.op)

    def __eq__(self, other):
        return (self.op == other.op and
                self.args == other.args and
                self.prefix == other.prefix)


def parse_program(code):
    r"""
    Take a source code string and yield a sequence of instructions

    >>> list(parse_program('push 1'))
    [Instr('push', [1.0])]

    Various sigils from Unicode are supported as alternate versions of
    operations, for example:
    >>> list(parse_program('← 1'))
    [Instr('push', [1.0])]
    >>> list(parse_program('↔'))
    [Instr('swap')]
    """
    for line in code.split('\n'):
        parts = line.split()
        op = parts[0]
        args = [float(arg) for arg in parts[1:]]
        yield Instr(op, args)


# TODO: This is pretty stringly typed, perhaps return a custom object?
def next_instruction(program):
    split_program = program.split(";")
    for instuction in split_program:
        if instuction == "":
            raise StopIteration
        else:
            yield instuction.strip()


def eval_program(program):
    instuction_gen = next_instruction(program)
    stack = []
    for instuction in instuction_gen:
        instuction = instuction.split()
        opcode = instuction[0]
        if opcode == "push":
            stack.append(int(instuction[1]))
        elif opcode == "pop":
            stack.pop()
        elif is_operator(opcode):
            a = stack.pop()
            b = stack.pop()
            # This uses b [op] a instead of a [op] b
            # because it allows for division and subtraction to be less
            # irritating (dividing by 5 -> push 5; divide).
            if opcode == "add":
                c = b + a
            elif opcode == "subtract":
                c = b - a
            elif opcode == "multiply":
                c = b * a
            elif opcode == "divide":
                c = b / a
            stack.append(c)
        elif opcode == "swap":
            # "swap" aliases to "swap 1"
            swap_gap = get_argument(instuction, 1)
            swap_from, swap_to = -1, -(1 + swap_gap)
            stack[swap_from], stack[swap_to] = stack[swap_to], stack[swap_from]
        elif opcode == "dup":
            dup_depth = get_argument(instuction, 1)  # "dup" aliases to "dup 1"
            if dup_depth == 0:
                continue
            if dup_depth > len(stack):
                raise IndexError
            stack.extend(stack[-dup_depth:])
    return stack


def get_argument(instuction, default):
    try:
        return int(instuction[1])
    except IndexError:
        return default


def is_operator(opcode):
    if opcode in ["add", "subtract", "multiply", "divide"]:
        return True
    else:
        return False
