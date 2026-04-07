import ply.lex as lex
from RAM.dataRam import ram

class LinkLoader():

    tokens = (
            "RELATIVE_ADDRESS",
            "BINARY",
            "NEWLINE",
        )

    t_ignore = ' \t'    

    def __init__(self, base_address=0, memory=None):
        self.base_address = base_address
        self.memory = memory or ram
        self.lexer = lex.lex(module=self)
        
    # Base address must be in decimal
    def set_base_address(self, base_address):
        self.base_address = base_address
    
    def t_NEWLINE(self, t):
        r'\n+'
        t.value = t.value
        return t

    def t_BINARY(self, t):
        r'[01]+'
        return t

    def t_RELATIVE_ADDRESS(self, t):
        r'\((\d+)\)'
        decimal_value = int(t.value[1:-1])
        relocated = decimal_value + self.base_address
        t.value = format(relocated, '064b')
        return t

    def t_error(self, t):
        t.lexer.skip(1)


    def link(self, program: str):
        program_size = len(program.split('\n'))
        self.lexer.input(program)
        result = ""

        if self.base_address and self._memory_check(self.base_address, program_size) != self.base_address:
            raise Exception(f"Insufficient memory from base address: {self.base_address}") 
                
        while self.base_address <= self.memory.DATA_START - program_size:
            new_memory_ptr = self._memory_check(self.base_address, program_size)
            if self.base_address != new_memory_ptr:
                self.base_address = new_memory_ptr
            else:
                break 
        
        if self.base_address >= self.memory.DATA_START - program_size:
            raise Exception("Insufficient memory")

        for tok in self.lexer:
            result += tok.value

        return result

    def _memory_check(self, memory_ptr, program_size):
        for i in range(memory_ptr, memory_ptr + program_size):
            if self.memory.storage[i] != "0" * 16:
                return i + 1
        return memory_ptr

    def hex_from_bin(self, value):
        return format(int(value, 2), f'0{len(value) // 4}X')

    def link_load(self, program: str):
        absolut_program  = self.link(program).split('\n')
        for line in absolut_program:
            self.memory.write(address=self.base_address, value=self.hex_from_bin(line))
            self.base_address += 1