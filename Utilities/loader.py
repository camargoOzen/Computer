from RAM.dataRam import ram
import re

class Loader:
    def __init__(self, data_ram, base_hex="0"):
        self.data_ram = data_ram
        self.offset = int(base_hex, 16) if isinstance(base_hex, str) else base_hex

    def load_program(self, file_path):
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith(';'):
                    continue

                # Expand (n) placeholders → 64-bit binary
                def expand(match):
                    n = int(match.group(1))
                    return format(n & ((1 << 64) - 1), '064b')

                line = re.sub(r'\((\d+)\)', expand, line)

                if not line:
                    continue

                num_hex_chars = len(line) // 4
                value = format(int(line, 2), f'0{num_hex_chars}X')

                address = format(self.offset, '016X')
                self.data_ram.write(address, value)
                self.offset += 1

        print(f"Program loaded from '{file_path}'")

    def load_program2(self, file: str):
            # Expand (n) placeholders → 64-bit binary
            def expand(match):
                n = int(match.group(1))
                return format(n & ((1 << 64) - 1), '064b')

            for line in file.splitlines():
                line = re.sub(r'\s+', '', line)
                line = re.sub(r'\((\d+)\)', expand, line)

                num_hex_chars = len(line) // 4
                value = format(int(line, 2), f'0{num_hex_chars}X')

                address = format(self.offset, '016X')
                self.data_ram.write(address, value)
                self.offset += 1

    def save_program(self, file_path, start_hex="0F", end_hex=None):
        start = int(start_hex, 16)
        if end_hex is not None:
            addresses = range(start, int(end_hex, 16) + 1)
        else:
            addresses = sorted(
                int(addr, 16)
                for addr in self.data_ram.storage
                if int(addr, 16) >= start
            )
        with open(file_path, "w") as file:
            for addr in addresses:
                addr_str = format(addr, '016X')
                if addr_str not in self.data_ram.storage:
                    continue
                hex_value = self.data_ram.storage[addr_str]
                num_bits = len(hex_value) * 4
                binary = format(int(hex_value, 16), f'0{num_bits}b')
                file.write(binary + "\n")
        print(f"Program saved to '{file_path}'")

    def set_base_hex(self, base_hex: str):
        self.offset = int(base_hex, 16)

loader = Loader(ram)