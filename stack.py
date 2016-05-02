# -*- coding: utf-8 -*-
from __future__ import division
import itertools


class Instr(object):
    def __init__(self, op, args=None, prefix=None):
        args = [] if args is None else args
        prefix = [] if prefix is None else prefix
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
    '>=': 'ge', '≥': 'ge',
    '∅': 'nop',
}

valid_ops = [
    'push', 'pop', 'dup', 'swap', 'jump',
    'add', 'sub', 'mul', 'div', 'pow',
    'eq', 'lt', 'gt', 'le', 'ge',
    'not',
    'nop',
]

arg_types = {
    'push': [[float]],
    'pop': [[]],
    'dup': [[], [int]], 'swap': [[], [int]], 'jump': [[], [int]],
    'add': [[]], 'sub': [[]], 'mul': [[]], 'div': [[]], 'pow': [[]],
    'eq': [[]], 'lt': [[]], 'gt': [[]], 'le': [[]], 'ge': [[]],
    'not': [[]],
    'nop': [[]],
}


def split_code(text):
    lines = (line.strip() for line in text.split('\n'))
    # We want to skip all comment lines
    lines = (line for line in lines if line and line[0] != ':')
    # Here lines is an iterable of lines that are not comments
    items = itertools.chain(*(line.split(';') for line in lines))
    items = (item.strip() for item in items)
    # We want to skip all empty strings
    return (item for item in items if item)


def parse_program(code):
    r"""
    Take a source code string and yield a sequence of instructions

    >> list(parse_program('push 1'))
    [Instr('push', [1.0])]

    Various sigils from_ Unicode are supported as alternate versions of
    operations, for example:
    >> list(parse_program('← 1'))
    [Instr('push', [1.0])]
    >> list(parse_program('↔'))
    [Instr('swap')]
    """
    for instruction in split_code(code):
        parts = instruction.split()
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
        if op in sigil_to_op:
            op = sigil_to_op[op]
        if op not in valid_ops:
            raise ValueError("Unknown opcode '{}'".format(op))

        check_type = {
            int: lambda x: int(x) == x,
            float: lambda x: isinstance(x, float),
        }
        arg_type_list = arg_types[op]
        typechecked = False
        for types in arg_type_list:
            if len(types) != len(args):
                continue
            if all(check_type[t](arg) for t, arg in zip(types, args)):
                typechecked = True
                break
        if not typechecked:
            raise ValueError(
                "Arguments for '{}' must be one of {}, were {}".format(
                    op, ', '.join(str(item) for item in arg_type_list), args))
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
                raise IndexError("Cannot dup {} elements, stack has {}".format(
                    dup_depth, len(stack)))
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
                raise IndexError("Jump address {} out of bounds ({})".format(
                    current_instr, len(instructions)-1))
        elif instr.op == 'nop':
            pass
        else:
            raise ValueError('Unknown instruction {}'.format(instr))
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


print(eval_program("push 1; push 2; add; push 5; mul; push 3; div"))
