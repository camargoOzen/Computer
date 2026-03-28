from RAM.dataRam import ram

class Fetch:
    def __init__(self, ):
        self.data_ram = ram
        
    def fetch_instruction(self, address):
        instruction = ram.read(address)
        instruction_hex = hex(int(instruction, 16))[2:].upper()
        return instruction_hex    