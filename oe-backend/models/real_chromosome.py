import random
from typing import Tuple


class RealChromosome:
    """
    Represents a single variable of the optimization problem using real-valued encoding.
    The value is stored directly as a float within the domain [a, b].
    """

    def __init__(self, domain: Tuple[float, float], value: float = None):
        self.domain = domain

        if value is not None:
            if not (domain[0] <= value <= domain[1]):
                raise ValueError(f"Value {value} is out of domain bounds {domain}")
            self.value = value
        else:
            self.value = random.uniform(domain[0], domain[1])

    def decode(self) -> float:
        return self.value

    def __repr__(self):
        return f"RealChromosome(value={self.value:.6f}, domain={self.domain})"
