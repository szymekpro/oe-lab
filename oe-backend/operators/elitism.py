from typing import List
from models.individual import Individual
from models.chromosome import Chromosome


class Elitism:
    """Preserves best individuals from the current population."""

    def __init__(self, elite_count: int = 1):
        if elite_count < 1:
            raise ValueError("elite_count must be >= 1")
        self.elite_count = elite_count

    @staticmethod
    def _clone_individual(individual: Individual) -> Individual:
        cloned_chromosomes = [
            Chromosome(ch.domain, ch.precision, bits_string=ch.bits)
            for ch in individual.chromosomes
        ]
        clone = Individual(individual.num_variables, cloned_chromosomes)
        clone.fitness = individual.fitness
        return clone

    def preserve(self, population: List[Individual], is_minimization: bool = True) -> List[Individual]:
        if not population:
            return []

        if any(ind.fitness is None for ind in population):
            raise ValueError("Population must be evaluated before elitism.")

        sorted_pop = sorted(population, key=lambda ind: ind.fitness, reverse=not is_minimization)
        elite = sorted_pop[:min(self.elite_count, len(sorted_pop))]
        return [self._clone_individual(ind) for ind in elite]
