from RAM.dataRam import ram

class Fetch:
    def __init__(self, ):
        self.data_ram = ram
        
    def fetch_instruction(self, address):
        return self.data_ram.read(address).upper()