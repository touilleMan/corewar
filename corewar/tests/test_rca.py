from ..rca import redcode_compile


def test_comment():
    for code in (
            ";",
            "; foo",
            "  ; foo",
            "  ; foo ; bar",
            "  ; foo",
        ):
        assert redcode_compile(code) == []


def test_mixed():
    code = """
ADD #-4, $12 ; foo
MOV $11, @11
SLT $10, #-100
JMP $-3;JMP $-3
ADD #-1, $9

MOV $8, $7
CMP $7, #-13
JMP $-7

; bar

ADD #-100, $-6
MOV #-9, $4
MOV $3, $2
JMP $-11
DAT #-9, #-9
DAT #-9, #-9
"""

    binary = (
        b"ADD\x00\xfc\xff\xff\xff\x0c\x00\x00\x00#$",
        b"MOV\x00\x0b\x00\x00\x00\x0b\x00\x00\x00$@",
        b"SLT\x00\x0a\x00\x00\x00\x9c\xff\xff\xff$#",
        b"JMP\x00\xfd\xff\xff\xff\x00\x00\x00\x00$$",
        b"ADD\x00\xff\xff\xff\xff\x09\x00\x00\x00#$",
        b"MOV\x00\x08\x00\x00\x00\x07\x00\x00\x00$$",
        b"CMP\x00\x07\x00\x00\x00\xf3\xff\xff\xff$#",
        b"JMP\x00\xf9\xff\xff\xff\x00\x00\x00\x00$$",
        b"ADD\x00\x9c\xff\xff\xff\xfa\xff\xff\xff#$",
        b"MOV\x00\xf7\xff\xff\xff\x04\x00\x00\x00#$",
        b"MOV\x00\x03\x00\x00\x00\x02\x00\x00\x00$$",
        b"JMP\x00\xf5\xff\xff\xff\x00\x00\x00\x00$$",
        b"DAT\x00\xf7\xff\xff\xff\xf7\xff\xff\xff##",
        b"DAT\x00\xf7\xff\xff\xff\xf7\xff\xff\xff##"
    )

    program = redcode_compile(code)

    for instruction, expected in zip(program, binary):
        assert instruction.to_bytecode() == expected, instruction

    # Test "to_bytecode" method as well
    assert program.to_bytecode() == b''.join(binary)
