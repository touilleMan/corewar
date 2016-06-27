from copy import copy

from .rca import redcode_compile
from .common import Program, Instruction, DATInstruction, DATException


VERBOSE = False


class Warrior:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.alive = True


class RelativeCore:
    def __init__(self, offset, core):
        self._offset = offset
        self._core = core
        self._len = len(core)

    def read(self, val, mode='#'):
        if mode == '#':
            return val
        elif mode == '$':
            return self[val]
        elif mode == '@':
            ptr = self[val]
            return self[ptr]

    def write(self, addr, instruction, mode='#'):
        if mode == '#':
            return
        elif mode == '$':
            self[addr] = copy(instruction)
        elif mode == '$':
            ptr_b = self[addr]
            self[ptr_b] = copy(instruction)

    def write_b_field(self, addr, field_val, mode='#'):
        if mode == '#':
            return
        elif mode == '$':
            self[addr].b = field_val
        elif mode == '$':
            ptr_b = self[addr]
            self[ptr_b].b = field_val

    def __getitem__(self, i):
        return self._core[(self._offset + i) % self._len]

    def __setitem__(self, i, v):
        if isinstance(i, slice):
            for j, k in enumerate(range(i.start, i.stop, i.step or 1)):
                self._core[(self._offset + k) % self._len] = v[j]
        else:
            self._core[(self._offset + i) % self._len] = v

    def __len__(self):
        return self._len


class CoreWarVM:
    def __init__(self, size=8000, max_code_size=100):
        self.size = size
        self.max_code_size = max_code_size
        self.core = RelativeCore(0, [DATInstruction()] * size)
        self.warriors = []

    def load_warrior(self, name, address, instructions):
        assert len(instructions) < self.max_code_size
        assert address >= 0
        address_end = address + len(instructions)
        assert address_end < self.size
        self.core[address:address_end] = instructions
        self.warriors.append(Warrior(name, address))

    def run(self, steps):
        for _ in range(steps):
            for warrior in self.warriors:
                if not warrior.alive:
                    continue
                try:
                    instruction = self.core[warrior.address]
                    if VERBOSE:
                        print('0x%x ==> %s' % (warrior.address, instruction))
                    jmp = instruction.exec(RelativeCore(warrior.address, self.core))
                    if VERBOSE:
                        for i in range(4):
                            print('0x%x -- %s' % (warrior.address + i, self.core[warrior.address + i]))
                    if jmp:
                        warrior.address += jmp
                    else:
                        warrior.address += 1
                except DATException:
                    print('%s has been killed !' % warrior.name)
                    warrior.alive = False
                    alives = [w for w in self.warriors if w.alive]
                    if len(alives) == 1:
                        return alives[0]
                    elif len(alives) == 0:
                        raise RuntimeError('All warrior have died !')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Corewar VM.')
    parser.add_argument('infiles', type=argparse.FileType('rb'),
                        nargs='+', help='code files to run')
    parser.add_argument('-s', '--size', type=int, default=80000,
                        help="VM's memory size")
    parser.add_argument('-r', '--max-steps', type=int,
                        help="Run the VM for a number of steps.")
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    VERBOSE = args.verbose
    address = 0
    max_code_size = int(args.size / len(args.infiles))
    vm = CoreWarVM(size=args.size, max_code_size=max_code_size)
    for i, infile in enumerate(args.infiles):
        if infile.name.endswith('.rc'):
            # Compile the file
            print('Compiling %s' % infile.name)
            program = redcode_compile(infile.read().decode())
        elif infile.name.endswith('.rco'):
            program = Program.from_bytecode(infile.read())
        else:
            raise RuntimeError("Code file should be a .rc or a .rco, exiting...")
        name = infile.name.rsplit('/', 1)[-1].rsplit('.', 1)[0] + '-%s' % i
        print('Loading %s (%s) at 0x%x' % (name, infile.name, address))
        vm.load_warrior(name, address, program)
        address += max_code_size

    print('Starting VM !')
    if args.max_steps:
        winner = vm.run(args.max_steps)
    else:
        while True:
            winner = vm.run(8000)
            if winner:
                break
    if winner:
        print("%s have won !" % winner.name)
    else:
        print("Warriors still alive:")
        for warrior in vm.warriors:
            print(' - %s' % warrior.name)
