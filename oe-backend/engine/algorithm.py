import time
import random
from typing import Dict, Any, Optional
from models.population import Population
from .functions import TestFunction
from operators.selection import SelectionMethod
from operators.crossover import CrossoverMethod
from operators.mutation import MutationMethod
from operators.inversion import Inversion
from operators.elitism import Elitism


class GeneticAlgorithm:
    """The Engine that orchestrates the genetic evolution through generations."""

    def __init__(self, test_function: TestFunction, population_size: int, num_variables: int,
                 precision: int, epochs: int, selection: SelectionMethod, crossover: CrossoverMethod,
                 mutation: MutationMethod, crossover_prob: float, mutation_prob: float,
                 elite_strategy: bool = True, elite_count: int = 1,
                 inversion: Optional[Inversion] = None, inversion_prob: float = 0.0,
                 is_minimization: bool = True):
        self.test_function = test_function
        self.epochs = epochs
        self.population_size = population_size
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.elite_strategy = elite_strategy
        self.is_minimization = is_minimization
        self.selection = selection
        self.crossover = crossover
        self.mutation = mutation
        self.inversion = inversion
        self.inversion_prob = inversion_prob
        self.elitism = Elitism(elite_count) if elite_strategy else None

        self.population = Population(population_size, num_variables, test_function.domain, precision)
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
                    "worst_fitness": worst_fit
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
                parent1, parent2 = random.sample(parents_pool, 2) if len(parents_pool) >= 2 else (
                    parents_pool[0], parents_pool[0]
                )

                child1, child2 = self.crossover.crossover(parent1, parent2, self.crossover_prob)

                child1 = self.mutation.mutate(child1, self.mutation_prob)
                child2 = self.mutation.mutate(child2, self.mutation_prob)
                if self.inversion is not None and self.inversion_prob > 0.0:
                    child1 = self.inversion.invert(child1, self.inversion_prob)
                    child2 = self.inversion.invert(child2, self.inversion_prob)

                next_generation.append(child1)
                if len(next_generation) < self.population_size:
                    next_generation.append(child2)

            self.population = Population(
                self.population_size, best_individual.num_variables, self.test_function.domain,
                best_individual.chromosomes[0].precision, individuals=next_generation[:self.population_size]
            )

        self.population.evaluate(self.test_function)
        
        fitnesses = [ind.fitness for ind in self.population.individuals if ind.fitness is not None]
        if fitnesses:
            self.history.append({
                "epoch": self.epochs, 
                "best_fitness": min(fitnesses) if self.is_minimization else max(fitnesses),
                "average_fitness": sum(fitnesses) / len(fitnesses),
                "worst_fitness": max(fitnesses) if self.is_minimization else min(fitnesses)
            })

        return {
            "best": self.population.get_best_individual(is_minimization=self.is_minimization),
            "time": time.time() - start_time,
            "history": self.history
        }
