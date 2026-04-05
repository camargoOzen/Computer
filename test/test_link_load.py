import pytest
from Disco.Preprocesador.link_loader import LinkLoader
from RAM.dataRam import DataRAM

@pytest.fixture
def fresh_ram():
    DataRAM._instance = None
    return DataRAM()

def test_link_simple():
    loader = LinkLoader(base_address=0)
    
    program = "010(5)"
    result = loader.link(program)
    assert result == "0100000000000000000000000000000000000000000000000000000000000000101"

def test_multiline_link():
    loader = LinkLoader(base_address=0)

    program = "010(3)\n111(1)"
    result = loader.link(program)

    assert result == "0100000000000000000000000000000000000000000000000000000000000000011\n1110000000000000000000000000000000000000000000000000000000000000001"

def test_link_load_with_base(fresh_ram):
    loader = LinkLoader(base_address=5, memory=fresh_ram)

    program = "000100110001(14)"
    loader.link_load(program)

    assert fresh_ram.read(5) == "1310000000000000013"

def test_link_load_without_base(fresh_ram):
    loader = LinkLoader(base_address=0, memory=fresh_ram)

    program = "000100110001(14)\n000101100011(6)"
    loader.link_load(program)

    assert fresh_ram.read(0) == "131000000000000000E"

def test_insufficient_memory_base_not_zero(fresh_ram):
    loader = LinkLoader(base_address=1, memory=fresh_ram)

    loader.memory.write(1,"1")

    program = "0100(1)"

    with pytest.raises(Exception, match=f"Insufficient memory from base address: {1}"):
        loader.link_load(program)

def test_insufficient_memory_base_zero(fresh_ram):
    loader = LinkLoader(memory=fresh_ram)

    for i in range(256):
        fresh_ram.write(i, "1")

    program = "0100(1)"

    with pytest.raises(Exception, match="Insufficient memory"):
        loader.link_load(program)

def test_link_load_fragment_memory(fresh_ram):
    loader = LinkLoader(memory=fresh_ram)

    fresh_ram.write(1,"1")
    fresh_ram.write(3,"1")

    program = "000100110001(14)\n000101100011(6)\n0000000000000000000000000000000000000000000000000000000000000000"
    loader.link_load(program)
    
    assert fresh_ram.read(4) == "1310000000000000012"
    assert fresh_ram.read(6) == "0000000000000000"