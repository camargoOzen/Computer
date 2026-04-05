import pytest
from RAM.dataRam import DataRAM

@pytest.fixture
def ram():
    DataRAM._instance = None  # reset singleton
    return DataRAM()

def test_write_and_read(ram):
    ram.write(10, "ABCDEF1234567890")
    assert ram.read(10) == "ABCDEF1234567890"

def test_initial_memory(ram):
    assert ram.read(0) == "0" * ram.WORD_SIZE_HEX

def test_stack_push(ram):
    ram.stack_push("AAAAAAAAAAAAAAAA")
    assert ram.stack_peek() == "AAAAAAAAAAAAAAAA"

def test_stack_pop(ram):
    ram.stack_push("BBBBBBBBBBBBBBBB")
    value = ram.stack_pop()
    
    assert value == "BBBBBBBBBBBBBBBB"
    assert ram.stack_ptr == ram.STACK_START

def test_stack_underflow(ram):
    with pytest.raises(Exception, match="Stack underflow"):
        ram.stack_pop()

def test_stack_overflow(ram):
    # Fill stack until limit
    for _ in range(256):
        ram.stack_push("X" * ram.WORD_SIZE_HEX)

    with pytest.raises(Exception, match="Stack is full"):
        ram.stack_push("Y" * ram.WORD_SIZE_HEX)

def test_singleton():
    DataRAM._instance = None
    
    ram1 = DataRAM()
    ram2 = DataRAM()

    assert ram1 is ram2