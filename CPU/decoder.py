from CPU.memoryManagementModule import Load
from CPU.aluController import ALUController
from CPU.jumpHandler import Jump
from CPU.stackHandler import Stack
from CPU.flags import flags

class Decoder:
    _instance = None

    def __init__(self):
        pass

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Decoder, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def decode(instruction):
        opcode = instruction[0:2]
        print(f"Decoding instruction: {instruction}")

        # LOAD, LOADV, STORE, LEA
        if opcode in ("11", "12", "13", "16"):
            register = instruction[2]
            value = instruction[3:(3+16)]
            Load.loader(opcode, register, value)

        if opcode in ("14", "15"):
            register1 = instruction[-2]
            register2 = instruction[-1]
            Load.registerOperations(opcode, register1, register2)

        # Stack Operations: PUSH/POP
        if opcode == "10":
            midcode = instruction[14]
            register = instruction[15]
            Stack.readStackInstruction(midcode, register)

        # ALU + FPU Operations
        if opcode in ("20", "21", "30"):
            midcode = instruction[12:14]
            registerA = instruction[14]
            registerB = instruction[15]
            ALUController.readALUInstruction(opcode, midcode, registerA, registerB)

        # Jumps, CALL, RET
        if opcode == "70":
            midcode = instruction[2]
            # RET has no address
            if midcode == "A":
                Jump.readJumpInstruction(midcode, None)
            else:
                address = instruction[3:(3+16)]
                Jump.readJumpInstruction(midcode, address)

        # I/O
        if opcode == "90":
            pass

        # Interrupts
        if opcode == "00":
            midcode = instruction[15]
            if midcode == "1":
                flags.IF = 0
            if midcode == "2":
                flags.IF = 0