import struct
from CPU.flags import Flags

class FPU:
    from CPU.flags import Flags

    def __init__(self):
        self.MASK = (1 << 64) - 1

    # ─── Pack / Unpack ────────────────────────────────────────────────

    def _unpack(self, hex_str):
        """Hex string → Python float (IEEE 754 double)"""
        bits = int(hex_str, 16)
        packed = struct.pack('>Q', bits)
        return struct.unpack('>d', packed)[0]

    def _pack(self, value):
        """Python float → hex string (IEEE 754 double)"""
        packed = struct.pack('>d', value)
        bits = struct.unpack('>Q', packed)[0]
        return format(bits, '016X')

    # ─── Flag Updates ─────────────────────────────────────────────────

    def _update_flags(self, result):
        self.Flags.ZF = 1 if result == 0.0 else 0
        self.Flags.NF = 1 if result < 0.0 else 0
        self.Flags.CF = 0  # No carry in FPU
        self.Flags.OF = 0  # Handled per operation

    # ─── Operations ───────────────────────────────────────────────────

    def add(self, a_str, b_str):
        a, b = self._unpack(a_str), self._unpack(b_str)
        result = a + b
        print(result)
        self._update_flags(result)
        return self._pack(result)

    def subtract(self, a_str, b_str):
        a, b = self._unpack(a_str), self._unpack(b_str)
        result = a - b
        print(result)
        self._update_flags(result)
        return self._pack(result)

    def multiply(self, a_str, b_str):
        a, b = self._unpack(a_str), self._unpack(b_str)
        result = a * b
        print(result)
        # Overflow: result exceeded float range
        if result > 1.7976931348623157e+308 or result < -1.7976931348623157e+308:
            self.Flags.OF = 1
            self.Flags.IF = 1
            return "0000000000000000"
        self._update_flags(result)
        return self._pack(result)

    def divide(self, a_str, b_str):
        a, b = self._unpack(a_str), self._unpack(b_str)
        if b == 0.0:
            self.Flags.IF = 1
            return "0000000000000000"
        result = a / b
        print(result)
        self._update_flags(result)
        return self._pack(result)

    def modulo(self, a_str, b_str):
        a, b = self._unpack(a_str), self._unpack(b_str)
        if b == 0.0:
            self.Flags.IF = 1
            return "0000000000000000"
        result = a % b
        print(result)
        self._update_flags(result)
        return self._pack(result)

    def increment(self, a_str):
        return self.add(a_str, self._pack(1.0))

    def decrement(self, a_str):
        return self.subtract(a_str, self._pack(1.0))

    def cmp(self, a_str, b_str):
        # Like ALU CMP — just sets flags, no result stored
        self.subtract(a_str, b_str)

fpu = FPU()