from RAM.dataRam import ram
from Utilities.loader import Loader
from Utilities.execute import Execute

def main():
    loader = Loader(ram, "0F")
    loader.load_program("Disco/Programas/program1.bin")
    Execute("0F").execute_program()

if __name__ == "__main__":
    main()