from RAM.dataRam import ram
from Utilities.execute import Execute
from Disco.Compilador.link_loader import LinkLoader

def main():
    base_hex = "0F"
    base_address = int(base_hex, 16)

    with open("Disco/Programas/program1.bin", "r", encoding="utf-8") as file:
        program = file.read().strip()

    loader = LinkLoader(base_address=base_address, memory=ram)
    entry_point = loader.link_load(program)

    Execute(entry_point).execute_program()

if __name__ == "__main__":
    main()