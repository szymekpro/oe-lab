import random
from abc import ABC, abstractmethod
from ..models.individual import Individual
from ..models.chromosome import Chromosome

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
                new_chroms.append(chrom)
        return Individual(individual.num_variables, new_chroms)

# TODO MUTACJA DWUPUNKTOWA

# TODO MUTACJA BRZEGOWA