from CPU.alu import alu
from CPU.fpu import fpu
from CPU.registers import registers

class ALUController:
    def readALUInstruction(opcode, midcode, registerA, registerB):

        # Integer registers
        if opcode == "20" or opcode == "30":
            register1 = registers.values[registerA]
            register2 = registers.values[registerB]

        # Float registers
        if opcode == "21":
            register1 = registers.values[registerA]
            register2 = registers.values[registerB]

        if opcode == "20":
            match midcode:
                case "01": registers.values[registerA] = alu.add(register1, register2)
                case "02": registers.values[registerA] = alu.subtract(register1, register2)
                case "03": registers.values[registerA] = alu.multiply(register1, register2)
                case "04": registers.values[registerA] = alu.divide(register1, register2)
                case "05": registers.values[registerA] = alu.modulo(register1, register2)
                case "06": registers.values[registerA] = registers.values[registerB]
                case "07": registers.values[registerA] = alu.increment(registers.values[registerA])
                case "08": registers.values[registerA] = alu.decrement(registers.values[registerA])
                case "0E": alu.subtract(register1, register2)
                case "0F": alu.bitwise_and(register1, register2)
                case "11": registers.values[registerA] = alu.bitwise_and(register1, register2)
                case "12": registers.values[registerA] = alu.bitwise_or(register1, register2)
                case "13": registers.values[registerA] = alu.bitwise_xor(register1, register2)
                case "14": registers.values[registerA] = alu.bitwise_not(register1)
                case "15": registers.values[registerA] = alu.bitwise_nand(register1, register2)
                case "16": registers.values[registerA] = alu.bitwise_nor(register1, register2)

        if opcode == "30":
            match midcode:
                case "01": registers.values[registerA] = alu.shl(register1, register2)
                case "02": registers.values[registerA] = alu.shr(register1, register2)
                case "03": registers.values[registerA] = alu.rol(register1, register2)
                case "04": registers.values[registerA] = alu.ror(register1, register2)

        if opcode == "21":
            match midcode:
                case "01": registers.values[registerA] = fpu.add(register1, register2)
                case "02": registers.values[registerA] = fpu.subtract(register1, register2)
                case "03": registers.values[registerA] = fpu.multiply(register1, register2)
                case "04": registers.values[registerA] = fpu.divide(register1, register2)
                case "05": registers.values[registerA] = fpu.modulo(register1, register2)
                case "06": registers.values[registerA] = registers.values[registerB]
                case "07": registers.values[registerA] = fpu.increment(registers.values[registerA])
                case "08": registers.values[registerA] = fpu.decrement(registers.values[registerA])
                case "0E": fpu.cmp(register1, register2)