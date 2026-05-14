from typing import List, Tuple
from .real_chromosome import RealChromosome
from .real_individual import RealIndividual
from engine.functions import TestFunction


class RealPopulation:
    """
    Population of real-valued individuals. Mirrors the Population API so the
    rest of the engine can treat both representations uniformly.
    """

    def __init__(self, size: int, num_variables: int, domain: Tuple[float, float],
                 individuals: List[RealIndividual] = None):
        self.size = size

        if individuals is None:
            self.individuals = []
            for _ in range(size):
                new_chromosomes = [RealChromosome(domain=domain) for _ in range(num_variables)]
                self.individuals.append(RealIndividual(num_variables=num_variables, chromosomes=new_chromosomes))
        else:
            if len(individuals) != size:
                raise ValueError("Provided individuals list length does not match the size parameter!")
            self.individuals = individuals

    def evaluate(self, test_function: TestFunction):
        for individual in self.individuals:
            if individual.fitness is None:
                individual.fitness = test_function.evaluate(individual.get_decoded_values())

    def get_best_individual(self, is_minimization: bool = True) -> RealIndividual:
        if any(ind.fitness is None for ind in self.individuals):
            raise ValueError("Population has not been evaluated yet!")
        if is_minimization:
            return min(self.individuals, key=lambda ind: ind.fitness)
        else:
            return max(self.individuals, key=lambda ind: ind.fitness)

    def __repr__(self):
        is_evaluated = self.individuals[0].fitness is not None if self.individuals else False
        return f"RealPopulation(Size: {self.size}, Evaluated: {is_evaluated})"
