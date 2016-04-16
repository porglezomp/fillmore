# -*- coding: utf-8 -*-
from __future__ import division
import re


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
        '=': 'eq',
        '<': 'lt',
        '>': 'gt',
        '<=': 'le', '≤': 'le',
        '>=': 'ge', '≥': 'ge'
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

    Various sigils from_ Unicode are supported as alternate versions of
    operations, for example:
    >>> list(parse_program('← 1'))
    [Instr('push', [1.0])]
    >>> list(parse_program('↔'))
    [Instr('swap')]
    """
    for line in re.split('\n|;', code):
        parts = line.strip().split()
        if not parts:
            continue
        # TODO: This only checks for 'quiet' as a prefix but should allow
        # "#" and "♯" as equlivlent (move it to Instr.)
        if parts[0] == 'quiet':
            prefix = ['quiet']
            op = parts[1]
            args = [float(arg) for arg in parts[2:]]
        else:
            prefix = None
            op = parts[0]
            args = [float(arg) for arg in parts[1:]]
        yield Instr(op, args, prefix)


def eval_program(program):
    instructions = list(parse_program(program))
    stack = []
    current_instr = 0
    while current_instr < len(instructions):
        instr = instructions[current_instr]
        current_instr += 1
        if instr.op == "push":
            stack.append(instr.args[0])
        elif instr.op == "pop":
            stack.pop()
        elif instr.op in binary_ops:
            if 'quiet' in instr.prefix:
                b = stack[-1]
                a = stack[-2]
            else:
                b = stack.pop()
                a = stack.pop()
            # b is the top of the stack, and a is the item before it, so
            # `... ; push 5 ; div` is dividing the result of `...` by 5.

            c = binary_ops[instr.op](b, a)
            stack.append(c)
        elif instr.op == 'swap':
            # `swap` aliased to `swap 1`
            swap_gap = int(instr.args[0] if instr.args else 1)
            from_, to = -1, -(1 + swap_gap)
            stack[from_], stack[to] = stack[to], stack[from_]
        elif instr.op == 'dup':
            # `dup` aliases to `dup 1`
            dup_depth = int(instr.args[0] if instr.args else 1)
            if dup_depth == 0:
                continue
            if dup_depth > len(stack):
                raise IndexError
            stack.extend(stack[-dup_depth:])
        elif instr.op in unary_ops:
            if 'quiet' in instr.prefix:
                operand = stack[-1]
            else:
                operand = stack.pop()
            c = unary_ops[instr.op](operand)
            stack.append(c)
        elif instr.op == 'jump':
            if instr.args:
                jump_distance = instr.args[0]
            else:
                jump_distance = stack[-1]
                if 'quiet' not in instr.prefix:
                    stack.pop()
            # We jump 1 less than the argument since we already incremented it
            # at the beginning of the loop.
            current_instr += int(jump_distance) - 1
            if current_instr > len(instructions) or current_instr < 0:
                raise IndexError
    return stack


binary_ops = {
    'add': lambda a, b: b + a,
    'sub': lambda a, b: b - a,
    'mul': lambda a, b: b * a,
    'div': lambda a, b: b / a,
    'pow': lambda a, b: b ** a,
    'eq': lambda a, b: float(b == a),
    'gt': lambda a, b: float(b > a),
    'ge': lambda a, b: float(b >= a),
    'lt': lambda a, b: float(b < a),
    'le': lambda a, b: float(b <= a)
}


unary_ops = {
    'not': lambda a: float(not a)
}


print(eval_program("push 1; push 2; add; push 5; multiply; push 3; divide"))
