import struct
from CPU.decoder import Decoder
from RAM.dataRam import ram
from CPU.pc import ProgramCounter
from Utilities.fetch import Fetch
from CPU.registers import registers
from CPU.flags import flags

STACK_BASE = ram.STACK_START
END_PROGRAM = 1

class Execute:
    def __init__(self, current_instruction=0):
        self.ram = ram
        self.decoder = Decoder()
        self.fetcher = Fetch()
        if isinstance(current_instruction, str):
            entry_point = int(current_instruction, 16)
        else:
            entry_point = int(current_instruction)

        self.program_counter = ProgramCounter(entry_point)
        self.program_counter.set_next_instruction(entry_point)
        self.auto_mode = False
        self._init_stack()

    def _init_stack(self):
        registers.stack_pointer = STACK_BASE
        print(f"Stack initialized at 0x{STACK_BASE:04X}")

    def exceute_step(self):
    
        current_addr = self.program_counter.get_next_instruction()
        print(f"\nAddress: {format(current_addr, '016X')}")

        if current_addr >= self.ram.DATA_START:
            print("End of program reached (data segment).")
            return END_PROGRAM

        word = self.ram.read(current_addr)
        if word == "0" * self.ram.WORD_SIZE_HEX:
            print("End of program reached (empty word).")
            return END_PROGRAM

        self.program_counter.set_next_instruction()

        instruction = self.fetcher.fetch_instruction(current_addr)
        Decoder.decode(instruction)
        
        return 0

    def execute_program_auto(self):
        
        while True:
            end_program = self.exceute_step()
            print(f"Registers: {registers.values}")
            print(f"Flags: {flags}")
            if end_program == END_PROGRAM:
                break
            

    def execute_program(self):
        print("========= Starting Program Execution =========")
        print("Tip: Press 'Enter' to step, or type 'auto' for continuous execution.")
        
        input_us = input().lower()
        self.set_auto_mode_value(input_us)
        
        if not self.auto_mode:
            while True:
                
                if self.exceute_step() == END_PROGRAM:
                    break
                
                user_input = input("Press Enter to step: ").strip().lower()
        else:
            self.execute_program_auto()
        
        self._print_final_state()
        print("========= Program Execution Finished =========")
        
        
        while True:
            current_addr = self.program_counter.get_next_instruction()
            print(f"\nAddress: {format(current_addr, '016X')}")

            if current_addr >= self.ram.DATA_START:
                print("End of program reached (data segment).")
                break

            word = self.ram.read(current_addr)
            if word == "0" * self.ram.WORD_SIZE_HEX:
                print("End of program reached (empty word).")
                break

            self.program_counter.set_next_instruction()

            instruction = self.fetcher.fetch_instruction(current_addr)
            Decoder.decode(instruction)

            print(f"Registers: {registers.values}")
            print(f"Flags: {flags}")

            if not self.auto_mode:
                user_input = input("Press Enter to step: ").strip().lower()
    
        self._print_final_state()
        print("========= Program Execution Finished =========")

    def _print_final_state(self):
        print(self.get_final_state_text())

    def get_final_state_text(self, highlight_pc: bool = False):
        lines = ["\n========= Final State ========="]
        lines.append("\n--- Registers ---")
        for reg, val in registers.values.items():
            dec_val = int(val, 16)
            try:
                double_val = struct.unpack('!d', bytes.fromhex(val))[0]
                lines.append(f"  R{reg} = {val}  (dec: {dec_val}, double: {double_val})")
            except:
                lines.append(f"  R{reg} = {val}  (dec: {dec_val})")

        lines.append(f"\n  SP = {format(registers.stack_pointer, '016X')}")
        lines.append(f"  PC = {self.program_counter.get_next_instruction_hex()}")
        lines.append("\n--- Flags ---")
        lines.append(f"  {flags}")

        

        return "\n".join(lines)

    def set_current_isntruction(self, current_instruction):
        self.program_counter = ProgramCounter(current_instruction)
        self.program_counter.set_next_instruction(current_instruction)

    def set_auto_mode_value(self, value):
        self.auto_mode = value