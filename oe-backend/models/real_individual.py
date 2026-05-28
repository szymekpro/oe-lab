from typing import List
from .real_chromosome import RealChromosome


class RealIndividual:
    """
    Represents a single individual (complete solution) using real-valued chromosome encoding.
    Each chromosome encodes one decision variable as a float in its domain.
    """

    def __init__(self, num_variables: int, chromosomes: List[RealChromosome]):
        if len(chromosomes) != num_variables:
            raise ValueError("The number of provided chromosomes does not match num_variables!")

        self.num_variables = num_variables
        self.chromosomes = chromosomes
        self.fitness: float | None = None

    def get_decoded_values(self) -> List[float]:
        return [chrom.decode() for chrom in self.chromosomes]

    def __repr__(self):
        decoded_rounded = [round(v, 6) for v in self.get_decoded_values()]
        return f"RealIndividual(Fitness: {self.fitness}, Values: {decoded_rounded})"
