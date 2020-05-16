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
        self.IR = None
        self.FL = 0b00000000
        self.reg[self.SP] = 0xf3
        self.branchtable = {}
        self.branchtable["LDI"] = self.handle_LDI
        self.branchtable["PRN"] = self.handle_PRN
        self.branchtable["HLT"] = self.handle_HLT
        self.branchtable["MUL"] = self.handle_MUL
        self.branchtable["PUSH"] = self.handle_PUSH
        self.branchtable["POP"] = self.handle_POP
        self.branchtable["CALL"] = self.handle_CALL
        self.branchtable["RET"] = self.handle_RET
        self.branchtable["ADD"] = self.handle_ADD
        self.branchtable["CMP"] = self.handle_CMP
        self.branchtable["JMP"] = self.handle_JMP
        self.branchtable["JNE"] = self.handle_JNE
        self.branchtable["JEQ"] = self.handle_JEQ
        self.branchtable["AND"] = self.handle_AND
        self.branchtable["OR"] = self.handle_OR


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
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b00000001
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.FL = 0b00000100
        elif op == "AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
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

    def handle_LDI(self, counter):
        reg_a = self.pc + 1
        value = self.pc + 2
        self.reg[self.ram[reg_a]] = self.ram[value]
        self.pc += counter

        return True

    def handle_PRN(self, counter):
        value = self.pc + 1
        print(self.reg[self.ram[value]])
        self.pc += counter

        return True

    def handle_HLT(self, counter):
        return False

    def handle_MUL(self, counter):
        reg_a = self.pc + 1
        reg_b = self.pc + 2
        self.alu("MUL", self.ram[reg_a], self.ram[reg_b])
        self.pc += counter

        return True

    def handle_ADD(self, counter):
        reg_a = self.pc + 1
        reg_b = self.pc + 2
        self.alu("ADD", self.ram[reg_a], self.ram[reg_b])
        self.pc += counter

        return True

    def handle_CMP(self, counter):
        reg_a = self.pc + 1
        reg_b = self.pc + 2
        self.alu("CMP", self.ram[reg_a], self.ram[reg_b])
        self.pc += counter

        return True

    def handle_PUSH(self, counter):
        register = self.ram[self.pc + 1]
        self.reg[self.SP] -= 1

        self.ram[self.reg[self.SP]] = self.reg[register]
        self.pc += counter

        return True

    def handle_POP(self, counter):
        register = self.ram[self.pc + 1]

        self.reg[register] = self.ram[self.reg[self.SP]]
        self.reg[self.SP] += 1

        self.pc += counter

        return True

    def handle_CALL(self, counter):
        register = self.ram[self.pc + 1]
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = self.pc + counter

        self.pc = self.reg[register]

        return True



    def handle_RET(self, counter):
        self.pc = self.ram[self.reg[self.SP]]
        self.reg[self.SP] += 1

        return True

    def handle_JMP(self, counter):
        register = self.ram[self.pc + 1]
        self.pc = self.reg[register]

        return True

    def handle_JNE(self, counter):
        register = self.ram[self.pc + 1]
        if self.FL & 0b00000001 == 0:
            self.pc = self.reg[register]

            return True
        
        self.pc += counter

        return True

    def handle_JEQ(self, counter):
        register = self.ram[self.pc + 1]
        if self.FL & 0b00000001 == 1:
            self.pc = self.reg[register]

            return True
        
        self.pc += counter

        return True

    def handle_AND(self, counter):
        reg_a = self.pc + 1
        reg_b = self.pc + 2
        self.alu("AND", self.ram[reg_a], self.ram[reg_b])
        self.pc += counter

        return True
    
    def handle_OR(self, counter):
        reg_a = self.pc + 1
        reg_b = self.pc + 2
        self.alu("OR", self.ram[reg_a], self.ram[reg_b])
        self.pc += counter

        return True


    def run(self):
        # op codes
        op_codes = {
        0b10000010: "LDI",
        0b01000111: "PRN",
        0b00000001: "HLT",
        0b10100010: "MUL",
        0b01000101: "PUSH",
        0b01000110: "POP",
        0b01010000: "CALL",
        0b00010001: "RET",
        0b10100000: "ADD",
        0b10100111: "CMP",
        0b01010100: "JMP",
        0b01010110: "JNE",
        0b01010101: "JEQ",
        0b10101000: "AND",
        0b10101010: "OR",
        }

        self.FL = 0b00000000
        self.pc = 0
        Running = True

        while Running:
            self.IR = self.ram[self.pc]
            counter = (self.IR >> 6) + 1

            Running = self.branchtable[op_codes[self.IR]](counter)