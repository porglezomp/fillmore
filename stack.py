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

    Prefixes are placed before the instruction
    Some prefixes also have sigils
    >>> list(parse_program('♯ +'))
    [Instr('add', [], ['quiet'])]
    """
    split_program = re.split('\n|;', code)
    label_indexes = get_label_indexes(split_program);
    # Represents ONLY instruction indexes
    # Used to map labels and index numbers.
    current_index = 0
    for line in split_program:
        # TODO: Disallow `@label add 1`, `add @label 1`, etc
        # `@label; add 1` is ok though.
        parts = line.strip().split()
        # Ignore newlines 
        if not parts or is_label(parts[0]):
            continue
#       elif any(is_label(part) for part in parts) and 'jump' not in parts:
#            raise ValueError("The instruction, {}, contains both a label and an instruction".format(line))
        # Process an actual instruction
        else:
            current_index += 1
            has_label = False
            prefix = []
            args = []
            op = None
            for part in parts:
                if part in sigil_to_op:
                    part = sigil_to_op[part]
                # A label on the same line as an instruction is an error.

                if part in prefixes:
                    prefix.append(prefixes[part])
                elif part in ops:
                    if op == None:
                        op = part
                    else:
                        raise ValueError("Two opcodes found in instruction: " + part + " and " + op)
                # We convert labels to an absolute jump.
                elif is_label(part):
                    has_label = True
                    if op not in ['jump', 'to']:
                        raise ValueError("Cannot use {} with a label".format(op))
                    if part not in label_indexes:
                        raise ValueError("The label, {}, was not defined".format(part))
                    op = 'to'
                    args.append(float(label_indexes[part]))
                # Test if part is an arguement.
                elif is_number(part):
                    args.append(float(part))
                else:
                    raise ValueError("Unknown Instruction: " + line)
            if op == None:
                raise ValueError("No opcode in instruction")
            yield Instr(op, args, prefix)

def is_label(label):
    return label[0] == '@'

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


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

ops = [
    'push', 'pop', 'dup', 'swap', 'jump', 
    'add', 'sub', 'mul', 'div', 'pow', 
    'eq', 'lt', 'gt', 'le', 'ge', 
    'not', 'jump', 'to'
]


prefixes = {
    'quiet': 'quiet',
    '#': 'quiet',
    '♯': 'quiet'
}


def get_label_indexes(split_program):
    label_indexes = {}
    current_index = 0
    for line in split_program:
        parts = line.strip().split()
        if not parts:
            continue
        # Two labels in a program is an error.
        if parts[0] in label_indexes:
            raise ValueError("Found the label {} on lines {} and {}"
                .format(parts[0], label_indexes[parts[0]], current_index))
        if is_label(parts[0]):
            if len(parts) != 1:
                raise ValueError("{} has a label before an instruction.".format(line))
            else:
                label_indexes[parts[0]] = current_index
                continue
        current_index += 1
    return label_indexes


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
        elif instr.op == 'to':
            if instr.args:
                jump_to = instr.args[0]
            else:
                jump_to = stack[-1]
                if 'quiet' not in instr.prefix:
                    stack.pop()
            if not float.is_integer(jump_to):
                raise TypeError("Expected an integer, got a: " + jump_to)
            current_instr = int(jump_to)
            if current_instr >= len(instructions) or current_instr <= 0:
                raise IndexError
    return stack


jump_ops = {
    'jump',
    'to',
}


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
