# Make Python 2 use float division instead of integer division
from __future__ import division


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
            stack[-1], stack[-(1 + swap_gap)
                             ] = stack[-(swap_gap + 1)], stack[-1]
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

print(eval_program("push 1; push 2; add; push 5; multiply; push 3; divide"))
