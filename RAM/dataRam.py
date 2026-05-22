class DataRAM:
    #This piece of code makes the object singleton.
    _instance = None

    # 64-bit address space, implemented as sparse storage to avoid huge allocation.
    ADDRESS_BITS = 64
    MAX_ADDRESS = (1 << ADDRESS_BITS) - 1
    UI_MAX_ADDRESS = 0xFFFF

    # Legacy logical segment markers used by the emulator.
    SIZE = 1024
    WORD_SIZE_HEX = 16
    '''
    0x000 - 0x0FF CODE (program)
    0x100 - 0x1FF DATA (global variable)
    0x200 - 0x2FF HEAP (dynamic memory)
    0x300 - 0x400 STACK
    '''
    CODE_START = 0
    DATA_START = 256
    HEAP_START = 512
    STACK_START = 1024
    STACK_MIN = 768

    def __new__(cls):
        if cls._instance is None:
            # If it doesn't exist yet, create it
            cls._instance = super(DataRAM, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.storage = {}
        self.heap_ptr = self.HEAP_START
        self.stack_ptr = self.STACK_START

    def _normalize_address(self, address):
        if isinstance(address, str):
            stripped = address.strip()
            if stripped == "":
                raise Exception("Memory out of index")
            address = int(stripped, 16)
        else:
            address = int(address)

        if address < self.CODE_START or address > self.MAX_ADDRESS:
            raise Exception("Memory out of index")

        return address

    # addres must be in decimal
    def read(self, address):
        normalized_address = self._normalize_address(address)
        return self.storage.get(normalized_address, "0" * self.WORD_SIZE_HEX)
    
    def write(self, address, value):
        normalized_address = self._normalize_address(address)
        self.storage[normalized_address] = value

    def __str__(self):
        return f"DataRAM Storage: {self.storage}"
    
    def stack_push(self, value):
        self.stack_ptr -= 1
        if self.stack_ptr < self.STACK_MIN:
            self.stack_ptr += 1
            raise Exception("Stack is full")
        self.storage[self.stack_ptr] = value
        

    def stack_pop(self):
        if self.stack_ptr == self.STACK_START:
            raise Exception("Stack underflow")
        value = self.storage[self.stack_ptr]
        self.storage[self.stack_ptr] = "0" * self.WORD_SIZE_HEX
        self.stack_ptr += 1
        return value

    def stack_peek(self):
        if self.stack_ptr == self.STACK_START:
            raise Exception("Stack is empty")
        return self.storage[self.stack_ptr]
    
    def reset(self):
        """Reset RAM to initial state"""
        self.storage = {}
        self.heap_ptr = self.HEAP_START
        self.stack_ptr = self.STACK_START

ram = DataRAM()