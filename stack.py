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
        '=': 'eq'
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
    instuctions = parse_program(program)
    stack = []

    for instr in instuctions:
        if instr.op == "push":
            stack.append(instr.args[0])
        elif instr.op == "pop":
            stack.pop() 
        elif is_binary_operator(instr.op):
            if 'quiet' in instr.prefix:
                b = stack[-1]
                a = stack[-2]
            else:
                b = stack.pop()
                a = stack.pop()
            # b is the top of the stack, and a is the item before it, so
            # `... ; push 5 ; div` is dividing the result of `...` by 5.
            if instr.op == 'add':
                c = a + b
            elif instr.op == 'sub':
                c = a - b
            elif instr.op == 'mul':
                c = a * b
            elif instr.op == 'div':
                c = a / b
            elif instr.op == 'pow':
                c = a ** b
            elif instr.op == 'eq':
                c = int(a == b)
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
    return stack


def is_binary_operator(op):
    return op in ('add', 'sub', 'mul', 'div', 'pow', 'eq')


print(eval_program("push 1; push 2; add; push 5; multiply; push 3; divide"))
