import random
from typing import Tuple, List
from abc import ABC, abstractmethod
from models.individual import Individual
from models.chromosome import Chromosome


class CrossoverMethod(ABC):
    """Abstract base class for crossover operations."""

    @abstractmethod
    def crossover(self, parent1: Individual, parent2: Individual, probability: float) -> Tuple[Individual, Individual]:
        pass


def _clone_individual(individual: Individual) -> Individual:
    cloned_chromosomes = [
        Chromosome(ch.domain, ch.precision, bits_string=ch.bits)
        for ch in individual.chromosomes
    ]
    clone = Individual(individual.num_variables, cloned_chromosomes)
    clone.fitness = individual.fitness
    return clone


class OnePointCrossover(CrossoverMethod):
    """Standard one-point crossover."""

    def crossover(self, parent1: Individual, parent2: Individual, probability: float) -> Tuple[Individual, Individual]:
        if random.random() > probability:
            return _clone_individual(parent1), _clone_individual(parent2)

        child1_chroms = []
        child2_chroms = []

        for parent1_chrom, parent2_chrom in zip(parent1.chromosomes, parent2.chromosomes):
            cut = random.randint(1, parent1_chrom.size - 1)

            new_bits_child1 = parent1_chrom.bits[:cut] + parent2_chrom.bits[cut:]
            new_bits_child2 = parent2_chrom.bits[:cut] + parent1_chrom.bits[cut:]

            child1_chroms.append(Chromosome(parent1_chrom.domain, parent1_chrom.precision, bits_string=new_bits_child1))
            child2_chroms.append(Chromosome(parent1_chrom.domain, parent1_chrom.precision, bits_string=new_bits_child2))

        return Individual(parent1.num_variables, child1_chroms), Individual(parent1.num_variables, child2_chroms)


class TwoPointCrossover(CrossoverMethod):
    """Two-point crossover."""

    def crossover(self, parent1: Individual, parent2: Individual, probability: float) -> Tuple[Individual, Individual]:
        if random.random() > probability:
            return _clone_individual(parent1), _clone_individual(parent2)

        child1_chroms = []
        child2_chroms = []

        for p1c, p2c in zip(parent1.chromosomes, parent2.chromosomes):
            if p1c.size < 3:
                child1_chroms.append(Chromosome(p1c.domain, p1c.precision, bits_string=p1c.bits))
                child2_chroms.append(Chromosome(p2c.domain, p2c.precision, bits_string=p2c.bits))
                continue

            cut1, cut2 = sorted(random.sample(range(1, p1c.size), 2))
            b1 = p1c.bits[:cut1] + p2c.bits[cut1:cut2] + p1c.bits[cut2:]
            b2 = p2c.bits[:cut1] + p1c.bits[cut1:cut2] + p2c.bits[cut2:]
            child1_chroms.append(Chromosome(p1c.domain, p1c.precision, bits_string=b1))
            child2_chroms.append(Chromosome(p1c.domain, p1c.precision, bits_string=b2))

        return Individual(parent1.num_variables, child1_chroms), Individual(parent1.num_variables, child2_chroms)


class UniformCrossover(CrossoverMethod):
    """Uniform crossover using independent per-bit mixing."""

    def __init__(self, parent1_bias: float = 0.5):
        if not 0.0 <= parent1_bias <= 1.0:
            raise ValueError("parent1_bias must be in range [0.0, 1.0]")
        self.parent1_bias = parent1_bias

    def crossover(self, parent1: Individual, parent2: Individual, probability: float) -> Tuple[Individual, Individual]:
        if random.random() > probability:
            return _clone_individual(parent1), _clone_individual(parent2)

        child1_chroms = []
        child2_chroms = []

        for p1c, p2c in zip(parent1.chromosomes, parent2.chromosomes):
            bits1 = []
            bits2 = []
            for bit1, bit2 in zip(p1c.bits, p2c.bits):
                if random.random() < self.parent1_bias:
                    bits1.append(bit1)
                    bits2.append(bit2)
                else:
                    bits1.append(bit2)
                    bits2.append(bit1)

            child1_chroms.append(Chromosome(p1c.domain, p1c.precision, bits_string="".join(bits1)))
            child2_chroms.append(Chromosome(p1c.domain, p1c.precision, bits_string="".join(bits2)))

        return Individual(parent1.num_variables, child1_chroms), Individual(parent1.num_variables, child2_chroms)


class GrainCrossover(CrossoverMethod):
    """
    Grainy crossover: exchanges random chunks of fixed size.
    """

    def __init__(self, grain_size: int = 2):
        if grain_size < 1:
            raise ValueError("grain_size must be >= 1")
        self.grain_size = grain_size

    def crossover(self, parent1: Individual, parent2: Individual, probability: float) -> Tuple[Individual, Individual]:
        if random.random() > probability:
            return _clone_individual(parent1), _clone_individual(parent2)

        child1_chroms = []
        child2_chroms = []

        for p1c, p2c in zip(parent1.chromosomes, parent2.chromosomes):
            pieces1: List[str] = []
            pieces2: List[str] = []
            for start in range(0, p1c.size, self.grain_size):
                end = min(start + self.grain_size, p1c.size)
                seg1 = p1c.bits[start:end]
                seg2 = p2c.bits[start:end]
                if random.random() < 0.5:
                    pieces1.append(seg1)
                    pieces2.append(seg2)
                else:
                    pieces1.append(seg2)
                    pieces2.append(seg1)

            child1_chroms.append(Chromosome(p1c.domain, p1c.precision, bits_string="".join(pieces1)))
            child2_chroms.append(Chromosome(p1c.domain, p1c.precision, bits_string="".join(pieces2)))

        return Individual(parent1.num_variables, child1_chroms), Individual(parent1.num_variables, child2_chroms)
