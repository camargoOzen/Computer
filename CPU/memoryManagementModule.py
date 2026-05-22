from RAM.dataRam import ram
from CPU.registers import registers
from CPU.storeOperationTracker import store_tracker

class Load:

    def loader(opcode, register, value):

        address = int(value, 16) if isinstance(value, str) else int(value)

        match opcode:
            #LOAD Instruction
            case "11":
                registers.values[register] = ram.read(address)
                print("Load memory address ", value, " in register ", register)

            #LOADV Instruction
            case "12":
                registers.values[register] = value
                print("Load value: ", value, "into register ", register)

            #STORE
            case "13":
                ram.write(address, registers.values[register])
                store_tracker.log_store(format(address, '016X'), registers.values[register])
                print("Store value of register ", register, " in memory address ", value)
            
            #LEA
            case "16":
                registers.values[register] = value
                print("Load effective memory address ", value, " in register ", register)
    
    def registerOperations(opcode, register1, register2):
        match opcode:       
            #LOADI
            case "14":
                retrieved_value = ram.read(register2)
                registers.values[register1] = retrieved_value
                print("Load memory value: ", retrieved_value, " from the memory address: ",register2," in register", register1)
            #STOREI
            case "15":
                address = registers.values[register2]
                value = registers.values[register1]
                ram.write(address, value)
                store_tracker.log_store(address, value)
                print("Store value of register ", register1, " in memory address ", register2)
                
            