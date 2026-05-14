"""
Shared pytest fixtures for P2 unit tests.
All fixtures are stateless helpers that build minimal valid objects,
keeping individual test cases focused and readable.
"""
import pytest
from models.real_chromosome import RealChromosome
from models.real_individual import RealIndividual
from engine.functions import Hypersphere


DOMAIN = (-5.0, 5.0)


@pytest.fixture
def domain():
    return DOMAIN


@pytest.fixture
def hypersphere():
    return Hypersphere()


def make_chromosome(value: float, domain=DOMAIN) -> RealChromosome:
    return RealChromosome(domain, value)


def make_individual(values: list, domain=DOMAIN) -> RealIndividual:
    chroms = [RealChromosome(domain, v) for v in values]
    return RealIndividual(len(values), chroms)
