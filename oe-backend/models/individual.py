from typing import List
from .chromosome import Chromosome


class Individual:
    """
    Represents a single individual (a complete solution) in the genetic algorithm.
    It acts as a pure container for a provided list of chromosomes, where each
    chromosome represents one mathematical variable (e.g., x1, x2).
    """

    def __init__(self, num_variables: int, chromosomes: List[Chromosome]):
        if len(chromosomes) != num_variables:
            raise ValueError("The number of provided chromosomes does not match num_variables!")

        self.num_variables = num_variables
        self.chromosomes = chromosomes
        self.fitness: float | None = None

    def get_decoded_values(self) -> List[float]:
        """
        Iterates through all chromosomes, decodes their binary representations,
        and returns a list of real numbers ready to be evaluated by the fitness function.
        """
        return [chrom.decode() for chrom in self.chromosomes]

    def __repr__(self):
        decoded_rounded = [round(v, 4) for v in self.get_decoded_values()]
        return f"Individual(Fitness: {self.fitness}, Values: {decoded_rounded})"