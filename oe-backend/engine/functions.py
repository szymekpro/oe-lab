from abc import ABC, abstractmethod
from typing import List, Tuple

class TestFunction(ABC):
    """
    Abstract class for all mathematical test functions.
    Defines a common interface that the Population class will expect and use to evaluate individuals.
    """

    def __init__(self, name: str, domain: Tuple[float, float]):
        self.name = name
        self.domain = domain

    @abstractmethod
    def evaluate(self, variables: List[float]) -> float:
        """
        Main evaluation method. Every specific mathematical function must implement its own formula here.
        """
        pass

#TODO TUTAJ JUZ PODJEBALI WIDZE TĄ FUNKCJE, TRZEBA BEDZIE INNA WYBRAĆ
class Hypersphere(TestFunction):
    """
    Hypersphere (Sphere) test function.
    A standard minimization problem where the algorithm should aim to reach a score of 0.0.
    Formula: f(x) = sum(x_i^2) for i = 1..N
    Global Minimum: f(x) = 0.0 at the point x = [0.0, 0.0, ...]
    """

    def __init__(self):
        super().__init__(name="Hypersphere", domain=(-5.0, 5.0))

    def evaluate(self, variables: List[float]) -> float:
        """
        Calculates the sum of squares for the provided list of variables.
        """
        # A fast generator expression to iterate through 'variables', square each 'x', and sum them up.
        return sum(x ** 2 for x in variables)