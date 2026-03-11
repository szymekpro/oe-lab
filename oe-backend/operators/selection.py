import random
from typing import List
from abc import ABC, abstractmethod
from models.individual import Individual

class SelectionMethod(ABC):
    """Abstract base class for all selection methods."""
    @abstractmethod
    def select(self, population: List[Individual], num_parents: int, is_minimization: bool = True) -> List[Individual]:
        pass

class BestSelection(SelectionMethod):
    """Simple selection: picks the top N individuals based on fitness."""
    def select(self, population: List[Individual], num_parents: int, is_minimization: bool = True) -> List[Individual]:
        sorted_pop = sorted(population, key=lambda ind: ind.fitness, reverse=not is_minimization)
        return sorted_pop[:num_parents]


class RouletteSelection(SelectionMethod):
    """
    Roulette-wheel selection with robust handling for minimization and
    non-positive fitness values.
    """

    def select(self, population: List[Individual], num_parents: int, is_minimization: bool = True) -> List[Individual]:
        if not population:
            return []

        fitness_values = [ind.fitness for ind in population]

        if any(f is None for f in fitness_values):
            raise ValueError("Population must be evaluated before selection.")

        epsilon = 1e-12

        if is_minimization:
            max_fitness = max(fitness_values)
            weights = [(max_fitness - f) + epsilon for f in fitness_values]
        else:
            min_fitness = min(fitness_values)
            weights = [(f - min_fitness) + epsilon for f in fitness_values]

        if sum(weights) <= 0:
            return random.choices(population, k=num_parents)

        return random.choices(population, weights=weights, k=num_parents)


class TournamentSelection(SelectionMethod):
    """Tournament selection with configurable tournament size."""

    def __init__(self, tournament_size: int = 3):
        if tournament_size < 2:
            raise ValueError("tournament_size must be >= 2")
        self.tournament_size = tournament_size

    def select(self, population: List[Individual], num_parents: int, is_minimization: bool = True) -> List[Individual]:
        if not population:
            return []

        if any(ind.fitness is None for ind in population):
            raise ValueError("Population must be evaluated before selection.")

        parents = []
        draw_size = min(self.tournament_size, len(population))

        for _ in range(num_parents):
            contestants = random.sample(population, draw_size)
            if is_minimization:
                winner = min(contestants, key=lambda ind: ind.fitness)
            else:
                winner = max(contestants, key=lambda ind: ind.fitness)
            parents.append(winner)

        return parents
