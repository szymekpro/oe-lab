import random
from abc import ABC, abstractmethod
from models.individual import Individual
from models.chromosome import Chromosome

class MutationMethod(ABC):
    """Abstract base class for mutation operations."""
    @abstractmethod
    def mutate(self, individual: Individual, probability: float) -> Individual:
        pass

class OnePointMutation(MutationMethod):
    """Flips one random bit in the genome."""
    def mutate(self, individual: Individual, probability: float) -> Individual:
        new_chroms = []
        for chrom in individual.chromosomes:
            if random.random() <= probability:
                idx = random.randint(0, chrom.size - 1)
                bits = list(chrom.bits)
                bits[idx] = "1" if bits[idx] == "0" else "0"
                new_chroms.append(Chromosome(chrom.domain, chrom.precision, bits_string="".join(bits)))
            else:
                new_chroms.append(Chromosome(chrom.domain, chrom.precision, bits_string=chrom.bits))
        return Individual(individual.num_variables, new_chroms)


class TwoPointMutation(MutationMethod):
    """Flips two random bits in each chromosome when mutation is triggered."""

    def mutate(self, individual: Individual, probability: float) -> Individual:
        new_chroms = []
        for chrom in individual.chromosomes:
            if random.random() <= probability:
                bits = list(chrom.bits)
                if chrom.size == 1:
                    idx = 0
                    bits[idx] = "1" if bits[idx] == "0" else "0"
                else:
                    idx1, idx2 = random.sample(range(chrom.size), 2)
                    bits[idx1] = "1" if bits[idx1] == "0" else "0"
                    bits[idx2] = "1" if bits[idx2] == "0" else "0"
                new_chroms.append(Chromosome(chrom.domain, chrom.precision, bits_string="".join(bits)))
            else:
                new_chroms.append(Chromosome(chrom.domain, chrom.precision, bits_string=chrom.bits))

        return Individual(individual.num_variables, new_chroms)


class EdgeMutation(MutationMethod):
    """
    Boundary mutation (brzegowa): forces chromosome to the lower or upper bound
    in binary representation.
    """

    def mutate(self, individual: Individual, probability: float) -> Individual:
        new_chroms = []
        for chrom in individual.chromosomes:
            if random.random() <= probability:
                boundary_bits = "0" * chrom.size if random.random() < 0.5 else "1" * chrom.size
                new_chroms.append(Chromosome(chrom.domain, chrom.precision, bits_string=boundary_bits))
            else:
                new_chroms.append(Chromosome(chrom.domain, chrom.precision, bits_string=chrom.bits))

        return Individual(individual.num_variables, new_chroms)
