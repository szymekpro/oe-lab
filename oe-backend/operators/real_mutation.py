import random
import math
from abc import ABC, abstractmethod

from models.real_chromosome import RealChromosome
from models.real_individual import RealIndividual


class RealMutationMethod(ABC):
    """Abstract base class for real-valued mutation operations."""

    @abstractmethod
    def mutate(self, individual: RealIndividual, probability: float) -> RealIndividual:
        pass


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class UniformRealMutation(RealMutationMethod):
    """
    Uniform mutation (mutacja równomierna).
    For each gene that is selected for mutation, its value is replaced by a new
    value drawn uniformly at random from the gene's domain [a, b].
    """

    def mutate(self, individual: RealIndividual, probability: float) -> RealIndividual:
        new_chroms = []
        for chrom in individual.chromosomes:
            if random.random() <= probability:
                new_value = random.uniform(chrom.domain[0], chrom.domain[1])
                new_chroms.append(RealChromosome(chrom.domain, new_value))
            else:
                new_chroms.append(RealChromosome(chrom.domain, chrom.value))
        return RealIndividual(individual.num_variables, new_chroms)


class GaussianMutation(RealMutationMethod):
    """
    Gaussian mutation (mutacja Gaussa).
    For each gene selected for mutation, Gaussian noise N(0, sigma) is added to
    the current value. The result is clamped to the domain [a, b].
    sigma can be specified as an absolute value or as a fraction of the domain width.
    """

    def __init__(self, sigma: float = 0.1, relative: bool = True):
        """
        Args:
            sigma: Standard deviation of the Gaussian noise.
                   If relative=True, sigma is multiplied by (b - a) to scale
                   with the domain width.
            relative: If True, sigma is treated as a fraction of domain width.
        """
        if sigma <= 0:
            raise ValueError("sigma must be > 0")
        self.sigma = sigma
        self.relative = relative

    def mutate(self, individual: RealIndividual, probability: float) -> RealIndividual:
        new_chroms = []
        for chrom in individual.chromosomes:
            if random.random() <= probability:
                a, b = chrom.domain
                effective_sigma = self.sigma * (b - a) if self.relative else self.sigma
                noise = random.gauss(0.0, effective_sigma)
                new_value = _clamp(chrom.value + noise, a, b)
                new_chroms.append(RealChromosome(chrom.domain, new_value))
            else:
                new_chroms.append(RealChromosome(chrom.domain, chrom.value))
        return RealIndividual(individual.num_variables, new_chroms)
