import time
import random
from typing import Dict, Any
from ..models.population import Population
from .functions import TestFunction
from ..operators.selection import SelectionMethod
from ..operators.crossover import CrossoverMethod
from ..operators.mutation import MutationMethod


class GeneticAlgorithm:
    """The Engine that orchestrates the genetic evolution through generations."""

    def __init__(self, test_function: TestFunction, population_size: int, num_variables: int,
                 precision: int, epochs: int, selection: SelectionMethod, crossover: CrossoverMethod,
                 mutation: MutationMethod, crossover_prob: float, mutation_prob: float,
                 elite_strategy: bool = True):
        self.test_function = test_function
        self.epochs = epochs
        self.population_size = population_size
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.elite_strategy = elite_strategy
        self.selection = selection
        self.crossover = crossover
        self.mutation = mutation

        self.population = Population(population_size, num_variables, test_function.domain, precision)
        self.history = []

    def run(self) -> Dict[str, Any]:
        start_time = time.time()

        for epoch in range(self.epochs):
            self.population.evaluate(self.test_function)
            best_individual = self.population.get_best_individual(is_minimization=True)
            self.history.append({"epoch": epoch, "best_fitness": best_individual.fitness})

            next_generation = []

            if self.elite_strategy:
                next_generation.append(best_individual)

            parents_pool = self.selection.select(self.population.individuals, self.population_size)

            while len(next_generation) < self.population_size:
                parent1, parent2 = random.sample(parents_pool, 2)

                child1, child2 = self.crossover.crossover(parent1, parent2, self.crossover_prob)

                child1 = self.mutation.mutate(child1, self.mutation_prob)
                child2 = self.mutation.mutate(child2, self.mutation_prob)

                next_generation.append(child1)
                if len(next_generation) < self.population_size:
                    next_generation.append(child2)

            self.population = Population(
                self.population_size, best_individual.num_variables, self.test_function.domain,
                best_individual.chromosomes[0].precision, individuals=next_generation[:self.population_size]
            )

        self.population.evaluate(self.test_function)
        return {
            "best": self.population.get_best_individual(is_minimization=True),
            "time": time.time() - start_time,
            "history": self.history
        }