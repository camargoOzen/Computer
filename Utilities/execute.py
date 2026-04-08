from CPU.decoder import Decoder
from RAM.dataRam import ram
from CPU.pc import ProgramCounter
from Utilities.fetch import Fetch
from CPU.registers import registers
from CPU.flags import flags

STACK_BASE = ram.STACK_START

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

    def execute_program(self):
        print("========= Starting Program Execution =========")
        print("Tip: Press 'Enter' to step, or type 'auto' for continuous execution.")

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
        print("\n========= Final State =========")

        print("\n--- Registers ---")
        for reg, val in registers.values.items():
            print(f"  R{reg} = {val}  (dec: {int(val, 16)})")

        print(f"\n  SP = {format(registers.stack_pointer, '016X')}")
        print(f"  PC = {self.program_counter.get_next_instruction_hex()}")
        print(f"\n--- Flags ---")
        print(f"  {flags}")

        print("\n--- RAM ---")
        for addr in range(self.ram.CODE_START, self.ram.DATA_START):
            value = self.ram.read(addr)
            if value != "0" * self.ram.WORD_SIZE_HEX:
                print(f"  [{format(addr, '016X')}] = {value}")

    def set_current_isntruction(self, current_instruction):
        self.program_counter = ProgramCounter(current_instruction)
        self.program_counter.set_next_instruction(current_instruction)

    def set_auto_mode_value(self, value):
        self.auto_mode = value