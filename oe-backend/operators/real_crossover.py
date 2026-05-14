import random
from abc import ABC, abstractmethod
from typing import Tuple

from models.real_chromosome import RealChromosome
from models.real_individual import RealIndividual


class RealCrossoverMethod(ABC):
    """Abstract base class for real-valued crossover operations."""

    @abstractmethod
    def crossover(self, parent1: RealIndividual, parent2: RealIndividual,
                  probability: float) -> Tuple[RealIndividual, RealIndividual]:
        pass


def _clone_real_individual(individual: RealIndividual) -> RealIndividual:
    cloned = [RealChromosome(ch.domain, ch.value) for ch in individual.chromosomes]
    clone = RealIndividual(individual.num_variables, cloned)
    clone.fitness = individual.fitness
    return clone


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class ArithmeticCrossover(RealCrossoverMethod):
    """
    Whole arithmetic crossover.
    A single alpha is drawn per crossover event:
        c1_i = alpha * p1_i + (1 - alpha) * p2_i
        c2_i = (1 - alpha) * p1_i + alpha * p2_i
    """

    def crossover(self, parent1: RealIndividual, parent2: RealIndividual,
                  probability: float) -> Tuple[RealIndividual, RealIndividual]:
        if random.random() > probability:
            return _clone_real_individual(parent1), _clone_real_individual(parent2)

        alpha = random.random()
        chroms1, chroms2 = [], []

        for c1, c2 in zip(parent1.chromosomes, parent2.chromosomes):
            a, b = c1.domain
            v1 = _clamp(alpha * c1.value + (1 - alpha) * c2.value, a, b)
            v2 = _clamp((1 - alpha) * c1.value + alpha * c2.value, a, b)
            chroms1.append(RealChromosome(c1.domain, v1))
            chroms2.append(RealChromosome(c1.domain, v2))

        return (RealIndividual(parent1.num_variables, chroms1),
                RealIndividual(parent1.num_variables, chroms2))


class LinearCrossover(RealCrossoverMethod):
    """
    Linear crossover.
    Generates 3 candidate offspring from linear combinations of parents,
    then returns the 2 with the best fitness.
        z1 = 0.5*p + 0.5*q
        z2 = 1.5*p - 0.5*q
        z3 = -0.5*p + 1.5*q
    Requires access to the objective function to rank the candidates.
    """

    def __init__(self, test_function, is_minimization: bool = True):
        self.test_function = test_function
        self.is_minimization = is_minimization

    def _make_individual(self, parent1: RealIndividual, parent2: RealIndividual,
                         a_coef: float, b_coef: float) -> RealIndividual:
        chroms = []
        for c1, c2 in zip(parent1.chromosomes, parent2.chromosomes):
            lo, hi = c1.domain
            v = _clamp(a_coef * c1.value + b_coef * c2.value, lo, hi)
            chroms.append(RealChromosome(c1.domain, v))
        ind = RealIndividual(parent1.num_variables, chroms)
        ind.fitness = self.test_function.evaluate(ind.get_decoded_values())
        return ind

    def crossover(self, parent1: RealIndividual, parent2: RealIndividual,
                  probability: float) -> Tuple[RealIndividual, RealIndividual]:
        if random.random() > probability:
            return _clone_real_individual(parent1), _clone_real_individual(parent2)

        z1 = self._make_individual(parent1, parent2, 0.5, 0.5)
        z2 = self._make_individual(parent1, parent2, 1.5, -0.5)
        z3 = self._make_individual(parent1, parent2, -0.5, 1.5)

        candidates = sorted([z1, z2, z3], key=lambda x: x.fitness,
                            reverse=not self.is_minimization)
        return candidates[0], candidates[1]


class BlendAlphaCrossover(RealCrossoverMethod):
    """
    BLX-α (blend crossover type alpha).
    For each gene: d = |p1_i - p2_i|
    Child gene is sampled from [min(p1_i, p2_i) - alpha*d, max(p1_i, p2_i) + alpha*d],
    clamped to domain.
    Two children are generated independently.
    """

    def __init__(self, alpha: float = 0.5):
        if alpha < 0:
            raise ValueError("alpha must be >= 0")
        self.alpha = alpha

    def crossover(self, parent1: RealIndividual, parent2: RealIndividual,
                  probability: float) -> Tuple[RealIndividual, RealIndividual]:
        if random.random() > probability:
            return _clone_real_individual(parent1), _clone_real_individual(parent2)

        chroms1, chroms2 = [], []

        for c1, c2 in zip(parent1.chromosomes, parent2.chromosomes):
            lo, hi = c1.domain
            cmin = min(c1.value, c2.value)
            cmax = max(c1.value, c2.value)
            d = cmax - cmin
            lower = cmin - self.alpha * d
            upper = cmax + self.alpha * d
            v1 = _clamp(random.uniform(lower, upper), lo, hi)
            v2 = _clamp(random.uniform(lower, upper), lo, hi)
            chroms1.append(RealChromosome(c1.domain, v1))
            chroms2.append(RealChromosome(c1.domain, v2))

        return (RealIndividual(parent1.num_variables, chroms1),
                RealIndividual(parent1.num_variables, chroms2))


class BlendAlphaBetaCrossover(RealCrossoverMethod):
    """
    BLX-α-β (blend crossover type alpha and beta).
    For each gene: d = |p1_i - p2_i|
    Child gene is sampled from [min(p1_i, p2_i) - beta*d, max(p1_i, p2_i) + alpha*d],
    clamped to domain.
    alpha extends above the maximum, beta extends below the minimum.
    """

    def __init__(self, alpha: float = 0.5, beta: float = 0.5):
        if alpha < 0 or beta < 0:
            raise ValueError("alpha and beta must be >= 0")
        self.alpha = alpha
        self.beta = beta

    def crossover(self, parent1: RealIndividual, parent2: RealIndividual,
                  probability: float) -> Tuple[RealIndividual, RealIndividual]:
        if random.random() > probability:
            return _clone_real_individual(parent1), _clone_real_individual(parent2)

        chroms1, chroms2 = [], []

        for c1, c2 in zip(parent1.chromosomes, parent2.chromosomes):
            lo, hi = c1.domain
            cmin = min(c1.value, c2.value)
            cmax = max(c1.value, c2.value)
            d = cmax - cmin
            lower = cmin - self.beta * d
            upper = cmax + self.alpha * d
            v1 = _clamp(random.uniform(lower, upper), lo, hi)
            v2 = _clamp(random.uniform(lower, upper), lo, hi)
            chroms1.append(RealChromosome(c1.domain, v1))
            chroms2.append(RealChromosome(c1.domain, v2))

        return (RealIndividual(parent1.num_variables, chroms1),
                RealIndividual(parent1.num_variables, chroms2))


class AveragingCrossover(RealCrossoverMethod):
    """
    Averaging crossover (uśredniające).
    Each gene of the single child is the arithmetic mean of both parents' genes:
        c_i = (p1_i + p2_i) / 2
    Both returned children are identical copies of that average.
    """

    def crossover(self, parent1: RealIndividual, parent2: RealIndividual,
                  probability: float) -> Tuple[RealIndividual, RealIndividual]:
        if random.random() > probability:
            return _clone_real_individual(parent1), _clone_real_individual(parent2)

        chroms = []
        for c1, c2 in zip(parent1.chromosomes, parent2.chromosomes):
            lo, hi = c1.domain
            v = _clamp((c1.value + c2.value) / 2.0, lo, hi)
            chroms.append(RealChromosome(c1.domain, v))

        child = RealIndividual(parent1.num_variables, chroms)
        return child, _clone_real_individual(child)
