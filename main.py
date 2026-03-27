from RAM.dataRam import ram
from Utilities.loader import Loader
from Utilities.execute import Execute

def main():
    loader = Loader(ram, "00")
    loader.load_program("program1.txt")
    Execute("00").execute_program()

if __name__ == "__main__":
    main()