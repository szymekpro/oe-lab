from typing import List, Tuple
from .chromosome import Chromosome
from .individual import Individual
from engine.functions import TestFunction


class Population:
    """
    Represents the entire population of individuals in a given epoch (generation).
    Responsible for storing individuals and evaluating their fitness in bulk.
    """

    def __init__(self, size: int, num_variables: int, domain: Tuple[float, float], precision: int,
                 individuals: List[Individual] = None):
        self.size = size

        if individuals is None:
            self.individuals = []
            for _ in range(size):
                new_chromosomes = [
                    Chromosome(domain=domain, precision=precision)
                    for _ in range(num_variables)
                ]

                new_individual = Individual(num_variables=num_variables, chromosomes=new_chromosomes)
                self.individuals.append(new_individual)
        else:
            if len(individuals) != size:
                raise ValueError("Provided individuals list length does not match the size parameter!")
            self.individuals = individuals

    def evaluate(self, test_function: TestFunction):
        """
        Calculates the fitness for each individual using the provided objective function.
        Only evaluates individuals that haven't been evaluated yet (fitness is None).
        """
        for individual in self.individuals:
            if individual.fitness is None:
                decoded_vars = individual.get_decoded_values()
                individual.fitness = test_function.evaluate(decoded_vars)

    def get_best_individual(self, is_minimization: bool = True) -> Individual:
        """
        Returns the individual with the best fitness score.
        """
        if any(ind.fitness is None for ind in self.individuals):
            raise ValueError("Cannot find the best individual. Population has not been evaluated yet!")

        if is_minimization:
            return min(self.individuals, key=lambda ind: ind.fitness)
        else:
            return max(self.individuals, key=lambda ind: ind.fitness)

    def __repr__(self):
        is_evaluated = self.individuals[0].fitness is not None if self.individuals else False
        return f"Population(Size: {self.size}, Evaluated: {is_evaluated})"
