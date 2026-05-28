"""
Integration-level unit tests for RealGeneticAlgorithm — the engine that
orchestrates the real-valued GA main loop (Projekt 2).

Theory:
    These tests operate at a higher level than the operator tests: they verify
    that the algorithm wires all components (population, selection, crossover,
    mutation, elitism, history) together correctly and produces a coherent
    result.  They do NOT assert that the GA finds the global optimum in every
    run (heuristics are stochastic), but they DO assert structural invariants
    that must hold regardless of the random seed:

    • The history must be produced.
    • Fitness values must improve (or stay the same) when elitism is active.
    • The output interface (best, time, history) must be complete.
    • Any combination of supported operators must run without errors.
"""
import pytest
from engine.functions import Hypersphere
from engine.real_algorithm import RealGeneticAlgorithm
from operators.selection import BestSelection, RouletteSelection, TournamentSelection
from operators.real_crossover import (
    ArithmeticCrossover, LinearCrossover, BlendAlphaCrossover,
    BlendAlphaBetaCrossover, AveragingCrossover,
)
from operators.real_mutation import UniformRealMutation, GaussianMutation


DOMAIN = (-5.0, 5.0)
EPOCHS = 30
POP_SIZE = 20
NUM_VARS = 3


def _default_ga(**kwargs) -> RealGeneticAlgorithm:
    """Factory: returns a minimal valid RealGeneticAlgorithm."""
    fn = Hypersphere()
    defaults = dict(
        test_function=fn,
        population_size=POP_SIZE,
        num_variables=NUM_VARS,
        epochs=EPOCHS,
        selection=RouletteSelection(),
        crossover=BlendAlphaCrossover(alpha=0.5),
        mutation=GaussianMutation(sigma=0.1),
        crossover_prob=0.8,
        mutation_prob=0.05,
        elite_strategy=True,
        is_minimization=True,
    )
    defaults.update(kwargs)
    return RealGeneticAlgorithm(**defaults)


class TestRealAlgorithmOutput:

    def test_run_returns_required_keys(self):
        """
        WHAT: Run the algorithm and inspect the returned dictionary.
        EXPECTED: Keys 'best', 'time', 'history' are all present.
        THEORY: The controller and (future) frontend depend on this exact
                contract.  Missing keys would cause KeyErrors at runtime that
                are hard to debug.
        """
        ga = _default_ga()
        result = ga.run()
        assert "best" in result
        assert "time" in result
        assert "history" in result

    def test_best_individual_has_fitness(self):
        """
        WHAT: Inspect the best individual returned by run().
        EXPECTED: best.fitness is a float (not None).
        THEORY: The final population is evaluated after the last epoch.
                The best individual must have a valid fitness so the
                controller can serialise and return it via the API.
        """
        ga = _default_ga()
        result = ga.run()
        assert result["best"].fitness is not None
        assert isinstance(result["best"].fitness, float)

    def test_best_individual_variables_within_domain(self):
        """
        WHAT: Check all decoded variables of the best solution.
        EXPECTED: Every variable is in [-5, 5].
        THEORY: If any operator fails to clamp values to the domain, the
                best individual could encode an infeasible point.  This test
                catches such regressions.
        """
        ga = _default_ga()
        result = ga.run()
        a, b = DOMAIN
        for v in result["best"].get_decoded_values():
            assert a <= v <= b

    def test_execution_time_is_positive(self):
        """
        WHAT: Inspect the 'time' value in the result.
        EXPECTED: time > 0.
        THEORY: A non-positive execution time would indicate that the timer
                was not started or stopped correctly, or that the algorithm
                completed before it actually ran (e.g., epochs=0 edge case
                handled elsewhere).
        """
        ga = _default_ga()
        result = ga.run()
        assert result["time"] > 0


class TestRealAlgorithmHistory:

    def test_history_length_is_epochs_plus_one(self):
        """
        WHAT: Run for EPOCHS=30 and count history entries.
        EXPECTED: len(history) == 31 (one entry per epoch + final evaluation).
        THEORY: The algorithm records one history point after evaluating the
                population in each epoch (indices 0..EPOCHS-1), then appends
                one more after the final evaluation post-loop.  Total = EPOCHS+1.
        """
        ga = _default_ga(epochs=EPOCHS)
        result = ga.run()
        assert len(result["history"]) == EPOCHS + 1

    def test_history_entries_have_required_keys(self):
        """
        WHAT: Inspect every entry in the history list.
        EXPECTED: Each entry contains 'epoch', 'best_fitness',
                  'average_fitness', 'worst_fitness'.
        THEORY: The frontend uses all four keys to render the convergence
                chart.  A missing key in any epoch causes a partial chart
                or a JavaScript crash.
        """
        ga = _default_ga()
        result = ga.run()
        required = {"epoch", "best_fitness", "average_fitness", "worst_fitness"}
        for entry in result["history"]:
            assert required.issubset(entry.keys()), (
                f"History entry missing keys: {required - entry.keys()}"
            )

    def test_best_fitness_in_history_is_non_increasing_with_elitism(self):
        """
        WHAT: Run with elite_strategy=True and compare consecutive history
              best_fitness values.
        EXPECTED: best_fitness[i+1] <= best_fitness[i] for all i
                  (minimisation problem).
        THEORY: Elitism guarantees that the best individual found so far is
                always carried to the next generation.  Therefore the best
                fitness of the population can only stay the same or improve
                (decrease for minimisation).  Any increase would indicate
                that elitism is broken.
        """
        ga = _default_ga(elite_strategy=True, epochs=50)
        result = ga.run()
        history = result["history"]
        for i in range(len(history) - 1):
            assert history[i + 1]["best_fitness"] <= history[i]["best_fitness"] + 1e-9, (
                f"Best fitness worsened at epoch {i+1}: "
                f"{history[i]['best_fitness']} -> {history[i+1]['best_fitness']}"
            )

    def test_worst_fitness_always_gte_best_in_each_epoch(self):
        """
        WHAT: For every history entry, compare worst and best fitness.
        EXPECTED: worst_fitness >= best_fitness.
        THEORY: Within a single evaluated population the worst individual
                can never have a lower fitness than the best for a minimisation
                problem.  A violation would indicate the history is populated
                with swapped values.
        """
        ga = _default_ga()
        result = ga.run()
        for entry in result["history"]:
            assert entry["worst_fitness"] >= entry["best_fitness"] - 1e-9


class TestRealAlgorithmConvergence:

    def test_minimization_improves_over_run(self):
        """
        WHAT: Compare best fitness at epoch 0 and epoch EPOCHS.
        EXPECTED: Final best_fitness <= initial best_fitness.
        THEORY: Even without elitism, the algorithm should statistically
                improve over 30 epochs on the simple Hypersphere function.
                This is a sanity check that the GA is actually evolving and
                not randomly shuffling the population.
        """
        ga = _default_ga(epochs=50, population_size=30)
        result = ga.run()
        history = result["history"]
        assert history[-1]["best_fitness"] <= history[0]["best_fitness"] + 1e-6

    def test_minimization_reaches_near_zero_for_hypersphere(self):
        """
        WHAT: Run with generous settings (large population, many epochs).
        EXPECTED: Best fitness < 1.0 for Hypersphere f(x) = Σ x_i².
        THEORY: The global minimum of Hypersphere is 0.0 at x = [0,...,0].
                With 200 epochs and population=50 the real-valued GA has
                ample opportunity to get close to it, regardless of the
                random seed.  Fitness > 1.0 would suggest the operators are
                fundamentally broken.
        """
        ga = _default_ga(epochs=200, population_size=50, num_variables=3)
        result = ga.run()
        assert result["best"].fitness < 1.0, (
            f"Expected best fitness < 1.0 but got {result['best'].fitness:.4f}"
        )


class TestRealAlgorithmOperatorCombinations:
    """
    Smoke tests that verify every supported operator combination runs to
    completion without raising an exception.  They do not assert quality.
    """

    @pytest.mark.parametrize("crossover,mutation", [
        (ArithmeticCrossover(),          UniformRealMutation()),
        (LinearCrossover(Hypersphere(),  True), GaussianMutation(0.1)),
        (BlendAlphaCrossover(0.5),       UniformRealMutation()),
        (BlendAlphaBetaCrossover(0.5, 0.3), GaussianMutation(0.2)),
        (AveragingCrossover(),           UniformRealMutation()),
    ])
    def test_operator_combination_runs_without_error(self, crossover, mutation):
        """
        WHAT: Instantiate RealGeneticAlgorithm with the given crossover and
              mutation pair and call run().
        EXPECTED: No exception is raised; result has 'best' key.
        THEORY: Each combination corresponds to a valid experimental setting.
                A crash in any combination would block the user from running
                a specific configuration from the GUI.
        """
        ga = RealGeneticAlgorithm(
            test_function=Hypersphere(),
            population_size=15,
            num_variables=2,
            epochs=10,
            selection=RouletteSelection(),
            crossover=crossover,
            mutation=mutation,
            crossover_prob=0.8,
            mutation_prob=0.05,
        )
        result = ga.run()
        assert "best" in result

    @pytest.mark.parametrize("selection", [
        BestSelection(),
        RouletteSelection(),
        TournamentSelection(),
    ])
    def test_selection_methods_all_work(self, selection):
        """
        WHAT: Run the algorithm with each of the three selection methods.
        EXPECTED: Completes without error.
        THEORY: Selection operators operate on fitness values.  Since
                RealIndividual stores fitness as a plain float (same as
                Individual), all three selection strategies should be
                compatible with the real representation without modification.
        """
        ga = _default_ga(selection=selection, epochs=10)
        result = ga.run()
        assert result["best"].fitness is not None
