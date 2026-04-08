from RAM.dataRam import ram
from CPU.registers import registers

class Stack:

    def readStackInstruction(midcode, register):
        match midcode:
            case "1":  # PUSH
                ram.stack_push(registers.values[register])
                registers.stack_pointer = ram.stack_ptr

            case "2":  # POP
                registers.values[register] = ram.stack_pop()
                registers.stack_pointer = ram.stack_ptr