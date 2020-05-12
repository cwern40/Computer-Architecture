"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.SP = 7
        self.reg[self.SP] = len(self.ram) -1
        self.branchtable = {}
        self.branchtable["LDI"] = self.handle_LDI
        self.branchtable["PRN"] = self.handle_PRN
        self.branchtable["HLT"] = self.handle_HLT
        self.branchtable["MUL"] = self.handle_MUL
        self.branchtable["PUSH"] = self.handle_PUSH
        self.branchtable["POP"] = self.handle_POP

    def load(self):
        """Load a program into memory."""

        address = 0
        self.ram = [0] * 256

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        if len(sys.argv) != 2:
            print("Need proper file name passed")
            sys.exit(1)

        filename = sys.argv[1]
        with open(filename) as f:
            for line in f:
                if line == '':
                    continue
                comment_split = line.split('#')
                num = comment_split[0].strip()
                if len(num) > 0:
                    self.ram[address] = int(num, 2)
                    address += 1

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_LDI(self, current):
        reg_a = current + 1
        value = current + 2
        self.reg[self.ram[reg_a]] = self.ram[value]
        return True

    def handle_PRN(self, current):
        value = current + 1
        print(self.reg[self.ram[value]])
        return True

    def handle_HLT(self, counter):
        return False

    def handle_MUL(self, current):
        reg_a = current + 1
        reg_b = current + 2
        self.alu("MUL", self.ram[reg_a], self.ram[reg_b])
        return True

    def handle_PUSH(self, current):
        register = self.ram(current + 1)
        self.reg[self.SP] -= 1

        self.ram[self.reg[self.SP]] = self.reg[register]

        return True

    def handle_POP(self, current):
        pass

    def run(self):
        # op codes
        op_codes = {
        0b10000010: "LDI",
        0b01000111: "PRN",
        0b00000001: "HLT",
        0b10100010: "MUL",
        0b01000101: "PUSH",
        0b01000110: "POP",
        }
        current = 0
        running = True

        while running:
            command = self.ram[current]
            counter = (command >> 6) + 1

            running = self.branchtable[op_codes[command]](current)
            current += counter



            # if command == LDI:
            #     reg_a = current + 1
            #     value = current + 2
            #     self.reg[self.ram[reg_a]] = self.ram[value]
            #     current += counter

            # elif command == PRN:
            #     value = current + 1
            #     print(self.reg[self.ram[value]])
            #     current += counter

            # elif command == HLT:
            #     running = False
            #     current += counter
            # elif command == MUL:
            #     reg_a = current + 1
            #     reg_b = current + 2
            #     self.alu("MUL", self.ram[reg_a], self.ram[reg_b])
            #     current += counter
