from CPU.memoryManagementModule import Load
from CPU.aluController import ALUController
from CPU.jumpHandler import Jump
from CPU.flags import flags

class Decoder:


    #This code makes every class a singleton, meaning that only one instance of each class can exist at a time.
    #In this CPU simulation, we want to ensure that there is only one ALU and one set of Flags, as they represent the state of the CPU.
    _instance = None

    def __init__(self):
        pass    
    
    def __new__(cls):
        if cls._instance is None:
            # If it doesn't exist yet, create it
            cls._instance = super(Decoder, cls).__new__(cls)
        return cls._instance

    
    def decode(instruction):
        
        opcode = instruction[0:2]

        print(f"Decoding instruction: {instruction}")
        #Instruction set 1: LOAD, LOADV, STORE, LEA
        #Instruction form: Opcode[2 Hex] Register[1 Hex] Address[16 Hex]
        if opcode == "11" or opcode == "12" or opcode == "13" or opcode == "16":
            register = instruction[2]
            value = instruction[3:(3+16)]
            Load.loader(opcode, register, value)

        #Instruction set 2: Stack Operations
        #Instruction form: Opcode [14 Hex] Midcode[1 Hex] Register[1 Hex]
        if opcode == "10":
            midcode = instruction[14]
            register = instruction[15]

        #Instruction set 3: ALU Operations
        #Instruction form: Opcode[12 Hex] Midcode[2 Hex] RegisterA[1 Hex] RegisterB[1 Hex]
        if opcode == "20" or opcode == "21" or opcode =="30":
            midcode = instruction[12:14]
            registerA = instruction[14]
            registerB = instruction[15]
            ALUController.readALUInstruction(opcode,midcode,registerA,registerB)

        #Instruction set 4: Jump Instructions
        #Instruction form: Opcode[2 Hex] Micdoce[1 Hex] Address[16 Hex]
        if opcode == "70":
            midcode = instruction[2]
            address = instruction [3:(3+16)]
            Jump.readJumpInstruction(midcode, address)

        #Instruction set 5: I/O Devices
        #Instruction form:  Opcode[13 Hex] Register[1 Hex] Port[2 Hex]
        if opcode == "90":
            #Not implemented since this emulator doesn't support I/O Devices.
            pass

        #Instruction set 6: Interruption instructions
        #Instruction form: Opcode[15 Hex] Midcode[1 Hex]
        if opcode == "00":
            midcode = instruction[15]
            if midcode == "1":
                flags.IF == 0
            if midcode == "2":
                flags.IF == 0
            

    


        
