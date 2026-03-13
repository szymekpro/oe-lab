import math
import random
from typing import Tuple


class Chromosome:
    """
    Represents a single variable of the optimization problem in a binary
    """

    def __init__(self, domain: Tuple[float, float], precision: int, value: float = None, bits_string: str = None):
        self.domain = domain
        self.precision = precision
        self.size = self._calculate_size()

        if bits_string is not None and value is not None:
            raise ValueError("Cannot provide both 'value' and 'bits_string' simultaneously!")

        if bits_string is not None:
            if len(bits_string) != self.size:
                raise ValueError(f"Provided bits_string has an invalid length! Expected {self.size}.")
            self.bits = bits_string

        elif value is not None:
            if not (domain[0] <= value <= domain[1]):
                raise ValueError(f"Value {value} is out of domain bounds {self.domain}")
            self.bits = self._encode(value)

        else:
            self.bits = "".join(random.choice(["0", "1"]) for _ in range(self.size))

    def _calculate_size(self) -> int:
        """
        Calculates the required number of bits using the formula:
        m = log2((b - a) * 10^precision + 1)
        """
        a, b = self.domain
        return math.ceil(math.log2((b - a) * 10 ** self.precision + 1))

    def _encode(self, number: float) -> str:
        """
        Encodes a real number into a binary string representation.
        """
        a, b = self.domain
        decimal_value = int(round((number - a) / (b - a) * (2 ** self.size - 1)))
        binary_str = bin(decimal_value)[2:]
        return binary_str.zfill(self.size)

    def decode(self) -> float:
        """
        Decodes the binary string back to a real number within the given domain.
        """
        a, b = self.domain
        decimal_value = int(self.bits, 2)
        real_value = a + decimal_value * (b - a) / (2 ** self.size - 1)
        return real_value

    def __repr__(self):
        return f"Chromosome(bits='{self.bits}', decoded={self.decode():.4f})"