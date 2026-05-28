from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import numpy as np
import benchmark_functions as bf


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

DE_DEFAULT_PARAMS: Dict[str, Any] = {"wf": 0.7, "cr": 0.9, "strategy": 0}


def _agent_position(agent: Any) -> np.ndarray:
    pos = getattr(agent, "solution", None)
    if pos is None:
        pos = agent
    return np.asarray(pos, dtype=float)


class MealPyAlgorithm:
    def __init__(
        self,
        function_name: str = "hypersphere",
        num_variables: int = 2,
        epoch: int = 100,
        pop_size: int = 50,
        wf: float = 0.7,
        cr: float = 0.9,
        strategy: int = 0,
        is_minimization: bool = True,
        seed: Optional[int] = None,
    ):
        self.function_name = function_name
        self.num_variables = num_variables
        self.epoch = epoch
        self.pop_size = pop_size
        self.wf = wf
        self.cr = cr
        self.strategy = strategy
        self.is_minimization = is_minimization
        self.seed = seed

        bf_cls = BENCHMARK_FUNCTIONS.get(function_name, bf.Hypersphere)
        try:
            self._bf_func = bf_cls(n_dimensions=num_variables)
        except TypeError:
            self._bf_func = bf_cls()

        try:
            bounds = self._bf_func.suggested_bounds()
            self._low: float = float(bounds[0][0])
            self._high: float = float(bounds[1][0])
        except Exception:
            self._low, self._high = -5.0, 5.0

        self.history: List[Dict[str, Any]] = []

    def _raw_fitness(self, position) -> float:
        return float(self._bf_func(list(np.asarray(position, dtype=float))))

    def _build_history(self, model) -> List[Dict[str, Any]]:
        history: List[Dict[str, Any]] = []
        populations = getattr(model.history, "list_population", None)

        if populations:
            for i, pop in enumerate(populations, start=1):
                fits = np.array([self._raw_fitness(_agent_position(a)) for a in pop])
                history.append({
                    "epoch":           i,
                    "best_fitness":    float(fits.min() if self.is_minimization else fits.max()),
                    "average_fitness": float(fits.mean()),
                    "worst_fitness":   float(fits.max() if self.is_minimization else fits.min()),
                    "std_fitness":     float(fits.std()),
                })
            return history

        best_curve = getattr(model.history, "list_global_best_fit", []) or []
        for i, val in enumerate(best_curve, start=1):
            history.append({
                "epoch":           i,
                "best_fitness":    float(val),
                "average_fitness": float(val),
                "worst_fitness":   float(val),
                "std_fitness":     0.0,
            })
        return history

    def run(self) -> Dict[str, Any]:
        from mealpy import FloatVar
        from mealpy.evolutionary_based.DE import OriginalDE

        self.history = []

        problem = {
            "obj_func":        self._raw_fitness,
            "bounds":          FloatVar(
                lb=[self._low] * self.num_variables,
                ub=[self._high] * self.num_variables,
            ),
            "minmax":          "min" if self.is_minimization else "max",
            "log_to":          None,
            "save_population": True,
        }

        model = OriginalDE(
            epoch=self.epoch,
            pop_size=self.pop_size,
            wf=self.wf,
            cr=self.cr,
            strategy=self.strategy,
        )

        start_time = time.time()
        if self.seed is not None:
            g_best = model.solve(problem, seed=self.seed)
        else:
            g_best = model.solve(problem)
        elapsed = time.time() - start_time

        self.history = self._build_history(model)

        best_position = _agent_position(g_best)
        best_raw = self._raw_fitness(best_position)

        return {
            "best_fitness":           best_raw,
            "best_decoded_variables": [float(x) for x in best_position],
            "execution_time":         elapsed,
            "num_generations":        self.epoch,
            "history":                self.history,
            "function_name":          self.function_name,
            "domain":                 [self._low, self._high],
            "wf":                     self.wf,
            "cr":                     self.cr,
            "strategy":               self.strategy,
        }
