import random
from typing import Tuple, List
from abc import ABC, abstractmethod
from ..models.individual import Individual
from ..models.chromosome import Chromosome


class CrossoverMethod(ABC):
    """Abstract base class for crossover operations."""

    @abstractmethod
    def crossover(self, parent1: Individual, parent2: Individual, probability: float) -> Tuple[Individual, Individual]:
        pass


class OnePointCrossover(CrossoverMethod):
    """Standard one-point crossover."""

    def crossover(self, parent1: Individual, parent2: Individual, probability: float) -> Tuple[Individual, Individual]:
        if random.random() > probability:
            return parent1, parent2

        child1_chroms = []
        child2_chroms = []

        for parent1_chrom, parent2_chrom in zip(parent1.chromosomes, parent2.chromosomes):
            cut = random.randint(1, parent1_chrom.size - 1)

            new_bits_child1 = parent1_chrom.bits[:cut] + parent2_chrom.bits[cut:]
            new_bits_child2 = parent2_chrom.bits[:cut] + parent1_chrom.bits[cut:]

            child1_chroms.append(Chromosome(parent1_chrom.domain, parent1_chrom.precision, bits_string=new_bits_child1))
            child2_chroms.append(Chromosome(parent1_chrom.domain, parent1_chrom.precision, bits_string=new_bits_child2))

        return Individual(parent1.num_variables, child1_chroms), Individual(parent1.num_variables, child2_chroms)

# TODO KRZYZOWANIE DWUPUNKTOWE

# TODO KRZYZOWANIE JEDNORODNE

# TODO KRZYZOWANIE ZARNISTE