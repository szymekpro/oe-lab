"""
Unit tests for RealIndividual — a container that groups RealChromosomes into
a complete candidate solution and exposes a unified decoding interface.

Theory:
    An individual represents one point in the n-dimensional search space.
    For a problem with N variables, the individual holds N chromosomes,
    one per variable.  Its fitness is computed externally by evaluating
    the test function at the decoded point.  The individual itself is
    purely a data structure; all logic lives in the operators and the
    algorithm engine.
"""
import pytest
from models.real_chromosome import RealChromosome
from models.real_individual import RealIndividual

DOMAIN = (-5.0, 5.0)


def _make_individual(values: list) -> RealIndividual:
    chroms = [RealChromosome(DOMAIN, v) for v in values]
    return RealIndividual(len(values), chroms)


class TestRealIndividualConstruction:

    def test_correct_construction(self):
        """
        WHAT: Build an individual with 3 chromosomes for a 3-variable problem.
        EXPECTED: num_variables == 3, chromosomes list has length 3.
        THEORY: The individual must reflect the dimensionality of the search
                space.  Any mismatch would silently corrupt evaluations.
        """
        ind = _make_individual([1.0, -2.0, 3.0])
        assert ind.num_variables == 3
        assert len(ind.chromosomes) == 3

    def test_chromosome_count_mismatch_raises(self):
        """
        WHAT: Pass num_variables=3 but only 2 chromosomes.
        EXPECTED: ValueError is raised.
        THEORY: A mismatch between the declared dimensionality and the
                actual number of chromosomes would cause silent data
                corruption (wrong number of variables fed to the objective).
                Fast-fail at construction is safer.
        """
        chroms = [RealChromosome(DOMAIN, 0.0), RealChromosome(DOMAIN, 1.0)]
        with pytest.raises(ValueError):
            RealIndividual(3, chroms)

    def test_fitness_is_none_on_creation(self):
        """
        WHAT: Inspect fitness immediately after construction.
        EXPECTED: fitness is None.
        THEORY: Fitness is computed by the population's evaluate() method,
                not during construction.  An unevaluated individual has
                fitness=None to signal that it has not yet been scored.
                This prevents stale cached values from a previous generation.
        """
        ind = _make_individual([0.0, 0.0])
        assert ind.fitness is None


class TestRealIndividualDecoding:

    def test_get_decoded_values_returns_correct_length(self):
        """
        WHAT: Call get_decoded_values() on a 4-variable individual.
        EXPECTED: Returns a list of exactly 4 floats.
        THEORY: The method must produce one decoded value per chromosome so
                the objective function receives the full variable vector.
        """
        ind = _make_individual([1.0, 2.0, 3.0, 4.0])
        decoded = ind.get_decoded_values()
        assert len(decoded) == 4

    def test_get_decoded_values_matches_chromosome_values(self):
        """
        WHAT: Build an individual with known values, decode it.
        EXPECTED: Each decoded value equals the corresponding chromosome value.
        THEORY: In real encoding, decode() is identity, so the decoded vector
                must exactly reproduce the values stored in the chromosomes.
                This is the contract that RealChromosome.decode() must satisfy,
                verified at the individual level.
        """
        values = [-3.0, 0.0, 4.5]
        ind = _make_individual(values)
        decoded = ind.get_decoded_values()
        assert decoded == values

    def test_get_decoded_values_does_not_mutate_chromosomes(self):
        """
        WHAT: Call get_decoded_values() and check chromosome values are unchanged.
        EXPECTED: Chromosome values are the same before and after the call.
        THEORY: Decoding must be a read-only operation.  Modifying chromosomes
                as a side effect of decoding would corrupt the individual's
                genotype during fitness evaluation.
        """
        ind = _make_individual([1.1, 2.2])
        _ = ind.get_decoded_values()
        assert ind.chromosomes[0].value == 1.1
        assert ind.chromosomes[1].value == 2.2

    def test_fitness_can_be_assigned_externally(self):
        """
        WHAT: Assign a float to individual.fitness after construction.
        EXPECTED: The value is stored and retrievable.
        THEORY: The Population.evaluate() method sets fitness externally.
                The individual must accept arbitrary float assignments without
                validation — it is a dumb container, not a fitness evaluator.
        """
        ind = _make_individual([0.0])
        ind.fitness = 42.0
        assert ind.fitness == 42.0
