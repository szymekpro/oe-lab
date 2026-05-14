import time
import random
from typing import Dict, Any

from models.real_population import RealPopulation
from .functions import TestFunction
from operators.selection import SelectionMethod
from operators.real_crossover import RealCrossoverMethod
from operators.real_mutation import RealMutationMethod
from operators.elitism import Elitism


class RealGeneticAlgorithm:
    """
    GA engine for real-valued chromosome representation (Projekt 2).
    Mirrors the GeneticAlgorithm API so the controller can use both interchangeably.
    Inversion is not applicable to real encoding and is therefore omitted.
    """

    def __init__(self, test_function: TestFunction, population_size: int, num_variables: int,
                 epochs: int, selection: SelectionMethod, crossover: RealCrossoverMethod,
                 mutation: RealMutationMethod, crossover_prob: float, mutation_prob: float,
                 elite_strategy: bool = True, elite_count: int = 1,
                 is_minimization: bool = True):
        self.test_function = test_function
        self.epochs = epochs
        self.population_size = population_size
        self.num_variables = num_variables
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.elite_strategy = elite_strategy
        self.is_minimization = is_minimization
        self.selection = selection
        self.crossover = crossover
        self.mutation = mutation
        self.elitism = Elitism(elite_count) if elite_strategy else None

        self.population = RealPopulation(population_size, num_variables, test_function.domain)
        self.history = []

    def run(self) -> Dict[str, Any]:
        start_time = time.time()

        for epoch in range(self.epochs):
            self.population.evaluate(self.test_function)
            best_individual = self.population.get_best_individual(is_minimization=self.is_minimization)

            fitnesses = [ind.fitness for ind in self.population.individuals if ind.fitness is not None]
            if fitnesses:
                best_fit = min(fitnesses) if self.is_minimization else max(fitnesses)
                worst_fit = max(fitnesses) if self.is_minimization else min(fitnesses)
                avg_fit = sum(fitnesses) / len(fitnesses)
                self.history.append({
                    "epoch": epoch,
                    "best_fitness": best_fit,
                    "average_fitness": avg_fit,
                    "worst_fitness": worst_fit,
                })

            next_generation = []

            if self.elite_strategy:
                next_generation.extend(
                    self.elitism.preserve(self.population.individuals, is_minimization=self.is_minimization)
                )

            parents_pool = self.selection.select(
                self.population.individuals, self.population_size, is_minimization=self.is_minimization
            )
            if len(parents_pool) < 2:
                parents_pool = self.population.individuals[:]

            while len(next_generation) < self.population_size:
                parent1, parent2 = (
                    random.sample(parents_pool, 2) if len(parents_pool) >= 2
                    else (parents_pool[0], parents_pool[0])
                )

                child1, child2 = self.crossover.crossover(parent1, parent2, self.crossover_prob)
                child1 = self.mutation.mutate(child1, self.mutation_prob)
                child2 = self.mutation.mutate(child2, self.mutation_prob)

                next_generation.append(child1)
                if len(next_generation) < self.population_size:
                    next_generation.append(child2)

            self.population = RealPopulation(
                self.population_size, self.num_variables, self.test_function.domain,
                individuals=next_generation[:self.population_size],
            )

        self.population.evaluate(self.test_function)

        fitnesses = [ind.fitness for ind in self.population.individuals if ind.fitness is not None]
        if fitnesses:
            self.history.append({
                "epoch": self.epochs,
                "best_fitness": min(fitnesses) if self.is_minimization else max(fitnesses),
                "average_fitness": sum(fitnesses) / len(fitnesses),
                "worst_fitness": max(fitnesses) if self.is_minimization else min(fitnesses),
            })

        return {
            "best": self.population.get_best_individual(is_minimization=self.is_minimization),
            "time": time.time() - start_time,
            "history": self.history,
        }
