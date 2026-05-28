"""
Unit tests for RealPopulation — the collection of individuals for one
generation of the real-valued genetic algorithm.

Theory:
    The population is the unit of selection.  Every generation, the entire
    population is evaluated (fitness assigned to each individual), sorted by
    fitness, and then new offspring are bred from the selected parents.
    Correct population initialisation, evaluation, and best-individual
    retrieval are prerequisites for any meaningful GA run.
"""
import pytest
from models.real_chromosome import RealChromosome
from models.real_individual import RealIndividual
from models.real_population import RealPopulation
from engine.functions import Hypersphere

DOMAIN = (-5.0, 5.0)
NUM_VARS = 3


def _make_evaluated_population(values_list: list) -> RealPopulation:
    """Helper: build a population with known fitness values."""
    individuals = []
    for values in values_list:
        chroms = [RealChromosome(DOMAIN, v) for v in values]
        ind = RealIndividual(len(values), chroms)
        ind.fitness = sum(v ** 2 for v in values)
        individuals.append(ind)
    return RealPopulation(len(values_list), NUM_VARS, DOMAIN, individuals=individuals)


class TestRealPopulationInitialization:

    def test_random_population_has_correct_size(self):
        """
        WHAT: Create a population of size 10 without providing individuals.
        EXPECTED: len(individuals) == 10.
        THEORY: The size parameter determines how many candidate solutions
                compete each generation.  A mismatch would silently reduce
                selection pressure or cause index errors in the algorithm.
        """
        pop = RealPopulation(10, NUM_VARS, DOMAIN)
        assert len(pop.individuals) == 10

    def test_all_random_genes_are_within_domain(self):
        """
        WHAT: Create 50 random individuals with 5 variables each.
        EXPECTED: Every gene of every individual lies in [a, b].
        THEORY: Variables must stay in the feasible region throughout the
                run.  Initialising outside the domain could cause the
                objective function to be evaluated at infeasible points.
        """
        pop = RealPopulation(50, 5, DOMAIN)
        a, b = DOMAIN
        for ind in pop.individuals:
            for chrom in ind.chromosomes:
                assert a <= chrom.value <= b

    def test_wrong_individuals_length_raises(self):
        """
        WHAT: Pass a list of 3 individuals but declare size=5.
        EXPECTED: ValueError is raised.
        THEORY: Mismatched size would break elitism (wrong slice bounds) and
                offspring-generation loops.  The constructor must enforce the
                invariant size == len(individuals).
        """
        chroms = [RealChromosome(DOMAIN) for _ in range(NUM_VARS)]
        ind = RealIndividual(NUM_VARS, chroms)
        with pytest.raises(ValueError):
            RealPopulation(5, NUM_VARS, DOMAIN, individuals=[ind, ind, ind])


class TestRealPopulationEvaluation:

    def test_evaluate_assigns_fitness_to_all(self):
        """
        WHAT: Call evaluate() on an unevaluated population.
        EXPECTED: Every individual has a non-None fitness after the call.
        THEORY: The GA main loop calls evaluate() at the start of each epoch.
                Any individual with fitness=None would cause KeyErrors or
                wrong comparisons in selection and elitism.
        """
        pop = RealPopulation(5, NUM_VARS, DOMAIN)
        pop.evaluate(Hypersphere())
        for ind in pop.individuals:
            assert ind.fitness is not None

    def test_evaluate_computes_correct_fitness(self):
        """
        WHAT: Build an individual at the known global optimum (0,0,0) of
              Hypersphere and evaluate.
        EXPECTED: fitness == 0.0.
        THEORY: Hypersphere f(x) = sum(x_i^2).  At x = [0,0,0], f = 0.
                This verifies that RealPopulation wires the objective
                function to decoded values correctly.
        """
        chroms = [RealChromosome(DOMAIN, 0.0) for _ in range(NUM_VARS)]
        ind = RealIndividual(NUM_VARS, chroms)
        pop = RealPopulation(1, NUM_VARS, DOMAIN, individuals=[ind])
        pop.evaluate(Hypersphere())
        assert pop.individuals[0].fitness == pytest.approx(0.0)

    def test_evaluate_skips_already_evaluated(self):
        """
        WHAT: Set fitness manually, then call evaluate().
        EXPECTED: The manually set fitness is preserved (not overwritten).
        THEORY: evaluate() only scores individuals with fitness=None.
                Skipping already-scored individuals avoids redundant
                function calls — important when elite individuals are
                carried over from the previous generation.
        """
        chroms = [RealChromosome(DOMAIN, 1.0) for _ in range(NUM_VARS)]
        ind = RealIndividual(NUM_VARS, chroms)
        ind.fitness = 999.0
        pop = RealPopulation(1, NUM_VARS, DOMAIN, individuals=[ind])
        pop.evaluate(Hypersphere())
        assert pop.individuals[0].fitness == 999.0


class TestRealPopulationBestIndividual:

    def test_get_best_minimization_returns_minimum_fitness(self):
        """
        WHAT: Population of 3 individuals with fitness 1.0, 5.0, 3.0.
              Call get_best_individual(is_minimization=True).
        EXPECTED: Returns the individual with fitness 1.0.
        THEORY: For a minimisation problem the best solution is the one
                closest to zero (global minimum).  Returning any other
                individual would steer the algorithm in the wrong direction.
        """
        pop = _make_evaluated_population([[-1.0, 0.0, 0.0],
                                          [2.0, 1.0, 0.0],
                                          [1.0, 1.0, 1.0]])
        best = pop.get_best_individual(is_minimization=True)
        assert best.fitness == pytest.approx(1.0)

    def test_get_best_maximization_returns_maximum_fitness(self):
        """
        WHAT: Same population, call get_best_individual(is_minimization=False).
        EXPECTED: Returns the individual with the highest fitness.
        THEORY: For a maximisation problem the best solution has the highest
                objective value.  The parameter flag must flip the comparison.
        """
        pop = _make_evaluated_population([[-1.0, 0.0, 0.0],
                                          [2.0, 1.0, 0.0],
                                          [1.0, 1.0, 1.0]])
        best = pop.get_best_individual(is_minimization=False)
        assert best.fitness == pytest.approx(5.0)

    def test_get_best_before_evaluation_raises(self):
        """
        WHAT: Call get_best_individual() without calling evaluate() first.
        EXPECTED: ValueError is raised.
        THEORY: Comparing individuals with fitness=None would throw a
                TypeError in Python's min/max.  An explicit guard with a
                clear error message is better than an obscure crash.
        """
        pop = RealPopulation(3, NUM_VARS, DOMAIN)
        with pytest.raises(ValueError, match="not been evaluated"):
            pop.get_best_individual()
