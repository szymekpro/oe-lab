import random
from typing import List
from abc import ABC, abstractmethod
from ..models.individual import Individual

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


#TODO SELEKCJA RULETKI

#TODO SELEKCJA TURNIEJOWA
