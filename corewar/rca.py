"""
Redcode assembler

see http://vyznev.net/corewar/guide.html

DAT -- data (kills the process)
MOV -- move (copies data from one address to another)
ADD -- add (adds one number to another)
SUB -- subtract (subtracts one number from another)
MUL -- multiply (multiplies one number with another)
DIV -- divide (divides one number with another)
MOD -- modulus (divides one number with another and gives the remainder)
JMP -- jump (continues execution from another address)
JMZ -- jump if zero (tests a number and jumps to an address if it's 0)
JMN -- jump if not zero (tests a number and jumps if it isn't 0)
DJN -- decrement and jump if not zero (decrements a number by one, and jumps unless the result is 0)
SPL -- split (starts a second process at another address)
CMP -- compare (same as SEQ)
SEQ -- skip if equal (compares two instructions, and skips the next instruction if they are equal)
SNE -- skip if not equal (compares two instructions, and skips the next instruction if they aren't equal)
SLT -- skip if lower than (compares two values, and skips the next instruction if the first is lower than the second)
LDP -- load from p-space (loads a number from private storage space)
STP -- save to p-space (saves a number to private storage space)
NOP -- no operation (does nothing)
"""

import parsimonious
from parsimonious.nodes import NodeVisitor

from .common import (Program, Instruction,
    MOVInstruction, ADDInstruction, JMPInstruction,
    CMPInstruction, SLTInstruction, DATInstruction
)


REDCODE_GRAMMAR = parsimonious.Grammar("""
    line = ws instruction? ws comment? ws

    comment = ";" ~".*"

    sep = ws "," ws
    ws = ~"\\s*"

    instruction = MOV / ADD / JMP / CMP / SLT / DAT

    MOV = "MOV" ws param sep param
    ADD = "ADD" ws param sep param
    JMP = "JMP" ws param
    CMP = "CMP" ws param sep param
    SLT = "SLT" ws param sep param
    DAT = "DAT" ws param sep param

    param = direct / immediate / b_indirect

    direct = "$"? number
    immediate = "#" number
    b_indirect = "@" number

    number = ~"-?[0-9]+"
""")


class CompilerVisitor(NodeVisitor):
    grammar = REDCODE_GRAMMAR

    def visit_line(self, n, vc):
        return vc[1]

    def visit_MOV(self, n, vc):
        _, _, a, _, b = vc
        return MOVInstruction(a=a[1], b=b[1], amode=a[0], bmode=b[0])

    def visit_JMP(self, n, vc):
        _, _, a = vc
        return JMPInstruction(a=a[1], b=0, amode=a[0], bmode='$')

    def visit_ADD(self, n, vc):
        _, _, a, _, b = vc
        return ADDInstruction(a=a[1], b=b[1], amode=a[0], bmode=b[0])

    def visit_CMP(self, n, vc):
        _, _, a, _, b = vc
        return CMPInstruction(a=a[1], b=b[1], amode=a[0], bmode=b[0])

    def visit_SLT(self, n, vc):
        _, _, a, _, b = vc
        return SLTInstruction(a=a[1], b=b[1], amode=a[0], bmode=b[0])

    def visit_DAT(self, n, vc):
        _, _, a, _, b = vc
        return DATInstruction(a=a[1], b=b[1], amode=a[0], bmode=b[0])

    def visit_number(self, n, vc):
        return int(n.text)

    def visit_direct(self, n, vc):
        return ('$', vc[-1])

    def visit_immediate(self, n, vc):
        return ('#', vc[1])

    def visit_b_indirect(self, n, vc):
        return ('@', vc[1])

    def visit_param(self, n, vc):
        return vc[0]

    def visit_instruction(self, n, vc):
        return vc[0]

    def visit_(self, n, vc):
        return vc[0] if vc else None

    def generic_visit(self, n, vc):
        return vc or n  # should semantically be a tuple


def redcode_compile(text):
    visitor = CompilerVisitor()
    out = Program()
    for line in text.splitlines():
        line = visitor.visit(REDCODE_GRAMMAR.parse(line))
        if line:
            out.append(line)
    return out


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Redcode assembler.')
    parser.add_argument('infile', type=argparse.FileType('r'),
                        help='Input file')
    parser.add_argument('-o', '--outfile', type=argparse.FileType('wb'),
                        help='Output file')
    args = parser.parse_args()
    assert args.infile.name.endswith('.rc')
    if not args.outfile:
        args.outfile = open(args.infile.name.rsplit('.', 1)[0] + '.rco', 'wb')
    program = redcode_compile(args.infile.read())
    args.outfile.write(program.to_bytecode())
    args.outfile.close()
