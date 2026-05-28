"""
PyGAD-based Genetic Algorithm Engine – Projekt 3
-------------------------------------------------
Wraps the PyGAD library (https://pygad.readthedocs.io/) to run a GA
using the same test functions already present in engine/functions.py
and in the benchmark_functions package used by P1/P2.

Gene encoding
  binary  → gene_type=int, init_range [0,2)  →  each gene is one bit (0 or 1)
             N bits decode a real variable in [low, high].
  real    → gene_type=float, genes are the variables directly.

History format mirrors the custom GA engines so OptimizationResult on the
frontend can display the chart without changes.
"""
from __future__ import annotations

import time
import logging
import threading
from typing import Any, Dict, List, Tuple, Optional

import numpy as np
import pygad
import benchmark_functions as bf

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

BENCHMARK_FUNCTIONS: Dict[str, Any] = {
    "hypersphere": bf.Hypersphere,
    "hyperellipsoid": bf.Hyperellipsoid,
    "rastrigin": bf.Rastrigin,
    "rosenbrock": bf.Rosenbrock,
    "ackley": bf.Ackley,
    "schwefel": bf.Schwefel,
    "griewank": bf.Griewank,
    "himmelblau": bf.Himmelblau,
    "michalewicz": bf.Michalewicz,
    "styblinski_tang": bf.StyblinskiTang,
}

SELECTION_TYPES = {"tournament", "rws", "random", "rank", "sss"}
CROSSOVER_TYPES = {"single_point", "two_points", "uniform", "scattered"}
MUTATION_TYPES  = {"random", "swap", "inversion", "scramble", "adaptive"}


def _decode_binary_individual(
    genes: np.ndarray,
    num_variables: int,
    bits_per_var: int,
    low: float,
    high: float,
) -> List[float]:
    """Decode a flat binary gene array into real-valued variables."""
    decoded = []
    for i in range(num_variables):
        chunk = genes[i * bits_per_var : (i + 1) * bits_per_var]
        max_val = 2 ** bits_per_var - 1
        # Clamp each gene to a valid bit (0 or 1) regardless of mutation drift
        bits = [str(int(abs(int(b))) % 2) for b in chunk]
        int_val = int("".join(bits), 2)
        real_val = low + (high - low) * int_val / max_val
        decoded.append(real_val)
    return decoded


# ──────────────────────────────────────────────────────────────────────────────
# PyGAD-based engine
# ──────────────────────────────────────────────────────────────────────────────

class PyGADAlgorithm:
    """
    Genetic Algorithm engine powered by PyGAD.

    Parameters
    ----------
    function_name       : key in BENCHMARK_FUNCTIONS
    num_variables       : number of real-valued decision variables
    num_generations     : number of GA generations
    sol_per_pop         : population size (solutions per population)
    num_parents_mating  : how many parents mate each generation
    parent_selection    : 'tournament' | 'rws' | 'random' | 'rank' | 'sss'
    crossover_type      : 'single_point' | 'two_points' | 'uniform' | 'scattered'
    mutation_type       : 'random' | 'swap' | 'inversion' | 'scramble' | 'adaptive'
    crossover_probability: probability (0-1) a parent is used for crossover
    mutation_probability : per-gene probability (0-1) of mutation
    k_tournament        : tournament size (used when parent_selection='tournament')
    keep_elitism        : number of elite individuals to carry over
    representation      : 'binary' | 'real'
    bits_per_var        : bits per variable (binary only)
    is_minimization     : True  → negate fitness for PyGAD (maximiser internally)
    use_custom_crossover: use the custom single-point crossover function from spec
    use_gaussian_mutation: use the Gaussian mutation function from spec
    parallel_threads    : number of threads for parallel_processing (0 = disabled)
    """

    def __init__(
        self,
        function_name: str = "hypersphere",
        num_variables: int = 2,
        num_generations: int = 100,
        sol_per_pop: int = 50,
        num_parents_mating: int = 10,
        parent_selection: str = "tournament",
        crossover_type: str = "single_point",
        mutation_type: str = "random",
        crossover_probability: float = 0.8,
        mutation_probability: float = 0.01,
        k_tournament: int = 3,
        keep_elitism: int = 1,
        representation: str = "binary",
        bits_per_var: int = 20,
        is_minimization: bool = True,
        use_custom_crossover: bool = False,
        use_gaussian_mutation: bool = False,
        parallel_threads: int = 0,
    ):
        self.function_name = function_name
        self.num_variables = num_variables
        self.num_generations = num_generations
        self.sol_per_pop = sol_per_pop
        self.num_parents_mating = num_parents_mating
        self.parent_selection = parent_selection
        self.crossover_type = crossover_type
        self.mutation_type = mutation_type
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability
        self.k_tournament = k_tournament
        self.keep_elitism = keep_elitism
        self.representation = representation
        self.bits_per_var = bits_per_var
        self.is_minimization = is_minimization
        self.use_custom_crossover = use_custom_crossover
        self.use_gaussian_mutation = use_gaussian_mutation
        self.parallel_threads = parallel_threads

        # Build benchmark function instance
        bf_cls = BENCHMARK_FUNCTIONS.get(function_name, bf.Hypersphere)
        try:
            self._bf_func = bf_cls(n_dimensions=num_variables)
        except TypeError:
            # Some 2D-only functions ignore n_dimensions
            self._bf_func = bf_cls()

        # Determine domain bounds
        try:
            bounds = self._bf_func.suggested_bounds()
            self._low: float  = float(bounds[0][0])
            self._high: float = float(bounds[1][0])
        except Exception:
            self._low, self._high = -5.0, 5.0

        self.history: List[Dict[str, Any]] = []

        # History lock (on_generation called from potentially parallel threads)
        self._history_lock = threading.Lock()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _decode(self, genes: np.ndarray) -> List[float]:
        if self.representation == "binary":
            return _decode_binary_individual(
                genes, self.num_variables, self.bits_per_var,
                self._low, self._high,
            )
        # real: genes ARE the variables, clipped to domain
        return [float(np.clip(g, self._low, self._high)) for g in genes]

    def _raw_fitness(self, decoded_vars: List[float]) -> float:
        return float(self._bf_func(decoded_vars))

    def _fitness_func(self, ga_instance, solution, solution_idx):
        """
        PyGAD maximises fitness. For minimisation, map the objective to a
        positive, order-preserving value (lower raw → higher fitness); a
        negated fitness (-raw) would invert roulette-wheel (rws) selection.
        """
        decoded = self._decode(solution)
        raw = self._raw_fitness(decoded)
        return 1.0 / (1.0 + raw) if self.is_minimization else raw

    def _on_generation(self, ga_instance):
        """Called after every generation – collect stats for history chart."""
        pop = ga_instance.population
        fitnesses = np.array([
            self._raw_fitness(self._decode(ind)) for ind in pop
        ])
        epoch = ga_instance.generations_completed
        with self._history_lock:
            self.history.append({
                "epoch": epoch,
                "best_fitness":    float(fitnesses.min() if self.is_minimization else fitnesses.max()),
                "average_fitness": float(fitnesses.mean()),
                "worst_fitness":   float(fitnesses.max() if self.is_minimization else fitnesses.min()),
                "std_fitness":     float(fitnesses.std()),
            })

    # ── Custom operators from P3 spec ─────────────────────────────────────────

    @staticmethod
    def _custom_crossover(parents, offspring_size, ga_instance):
        """Single-point crossover as shown in P3 spec (pseudocode)."""
        offspring = []
        idx = 0
        while len(offspring) != offspring_size[0]:
            parent1 = parents[idx % parents.shape[0], :].copy()
            parent2 = parents[(idx + 1) % parents.shape[0], :].copy()
            split = np.random.choice(range(offspring_size[1]))
            parent1[split:] = parent2[split:]
            offspring.append(parent1)
            idx += 1
        return np.array(offspring)

    @staticmethod
    def _gaussian_mutation(offspring, ga_instance):
        """Gaussian (normal) mutation as shown in P3 spec."""
        for chromosome_idx in range(offspring.shape[0]):
            random_gene_idx = np.random.choice(range(offspring.shape[1]))
            offspring[chromosome_idx, random_gene_idx] += np.random.normal(0, 1)
        return offspring

    # ── Main entry point ──────────────────────────────────────────────────────

    def run(self) -> Dict[str, Any]:
        self.history = []

        # Silence PyGAD's own logger output
        logger = logging.getLogger("pygad")
        logger.setLevel(logging.CRITICAL)

        # Gene configuration
        if self.representation == "binary":
            num_genes  = self.num_variables * self.bits_per_var
            gene_type  = int
            init_low   = 0
            init_high  = 2          # [0, 2) → 0 or 1
            rand_min   = None
            rand_max   = None
        else:
            num_genes  = self.num_variables
            gene_type  = float
            init_low   = self._low
            init_high  = self._high
            rand_min   = self._low
            rand_max   = self._high

        crossover_fn = self._custom_crossover if self.use_custom_crossover else self.crossover_type
        mutation_fn  = self._gaussian_mutation if self.use_gaussian_mutation else self.mutation_type

        kwargs: Dict[str, Any] = dict(
            num_generations       = self.num_generations,
            sol_per_pop           = self.sol_per_pop,
            num_parents_mating    = self.num_parents_mating,
            num_genes             = num_genes,
            fitness_func          = self._fitness_func,
            init_range_low        = init_low,
            init_range_high       = init_high,
            gene_type             = gene_type,
            mutation_probability   = self.mutation_probability,
            crossover_probability  = self.crossover_probability,
            parent_selection_type = self.parent_selection,
            crossover_type        = crossover_fn,
            mutation_type         = mutation_fn,
            keep_elitism          = self.keep_elitism,
            K_tournament          = self.k_tournament,
            logger                = None,
            on_generation         = self._on_generation,
            suppress_warnings     = True,
        )

        if self.representation == "real" and rand_min is not None:
            kwargs["random_mutation_min_val"] = rand_min
            kwargs["random_mutation_max_val"] = rand_max

        if self.parallel_threads > 0:
            kwargs["parallel_processing"] = ["thread", self.parallel_threads]

        start_time = time.time()
        ga_instance = pygad.GA(**kwargs)
        ga_instance.run()
        elapsed = time.time() - start_time

        # Best solution
        best_solution, best_solution_fitness, _ = ga_instance.best_solution()
        best_decoded = self._decode(best_solution)
        best_raw = self._raw_fitness(best_decoded)

        return {
            "best_fitness":           best_raw,
            "best_decoded_variables": best_decoded,
            "execution_time":         elapsed,
            "num_generations":        self.num_generations,
            "history":                self.history,
            "function_name":          self.function_name,
            "domain":                 [self._low, self._high],
            "representation":         self.representation,
        }
