class DataRAM:
    #This piece of code makes the object singleton.
    _instance = None
    
    # 1024 * 64 = 8.1 KB
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

    def __new__(cls):
        if cls._instance is None:
            # If it doesn't exist yet, create it
            cls._instance = super(DataRAM, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.storage = ["0" * self.WORD_SIZE_HEX for _ in range(self.SIZE)]
        self.heap_ptr = self.HEAP_START
        self.stack_ptr = self.STACK_START

    # addres must be in decimal
    def read(self, address):
        return self.storage[address]  
    
    def write(self, address, value):
        if address >= self.HEAP_START or address < self.CODE_START:
            raise Exception("Memory out of index")
        self.storage[address] = value

    def __str__(self):
        return f"DataRAM Storage: {self.storage}"
    
    def stack_push(self, value):
        self.stack_ptr -= 1
        if self.stack_ptr <= 767:
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

ram = DataRAM()