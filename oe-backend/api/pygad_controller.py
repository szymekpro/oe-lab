from flask_restx import Namespace, Resource, fields
from engine.pygad_algorithm import PyGADAlgorithm, BENCHMARK_FUNCTIONS, SELECTION_TYPES, CROSSOVER_TYPES, MUTATION_TYPES

pygad_ns = Namespace(
    "pygad",
    description="PyGAD-based Genetic Algorithm optimization (Projekt 3)",
    path="/pygad",
)

# ─── Request model ────────────────────────────────────────────────────────────

pygad_params_model = pygad_ns.model("PyGADParams", {
    "function_name": fields.String(
        default="hypersphere",
        description="Benchmark function: " + " | ".join(BENCHMARK_FUNCTIONS.keys()),
    ),
    "num_variables": fields.Integer(default=2, description="Number of decision variables"),
    "num_generations": fields.Integer(default=100, description="Number of generations"),
    "sol_per_pop": fields.Integer(default=50, description="Population size"),
    "num_parents_mating": fields.Integer(default=10, description="Parents mating per generation"),
    "parent_selection": fields.String(
        default="tournament",
        description="Selection: " + " | ".join(SELECTION_TYPES),
    ),
    "crossover_type": fields.String(
        default="single_point",
        description="Crossover: " + " | ".join(CROSSOVER_TYPES) + " | custom",
    ),
    "mutation_type": fields.String(
        default="random",
        description="Mutation: " + " | ".join(MUTATION_TYPES) + " | gaussian",
    ),
    "crossover_probability": fields.Float(default=0.8, description="Probability (0-1) a parent is used for crossover"),
    "mutation_probability": fields.Float(default=0.01, description="Per-gene probability (0-1) of mutation"),
    "k_tournament": fields.Integer(default=3, description="Tournament size"),
    "keep_elitism": fields.Integer(default=1, description="Elite individuals carried over"),
    "representation": fields.String(
        default="binary",
        description="Chromosome encoding: binary | real",
    ),
    "bits_per_var": fields.Integer(default=20, description="Bits per variable (binary only)"),
    "is_minimization": fields.Boolean(default=True, description="True = minimise, False = maximise"),
    "use_custom_crossover": fields.Boolean(default=False, description="Use custom crossover from P3 spec"),
    "use_gaussian_mutation": fields.Boolean(default=False, description="Use Gaussian mutation from P3 spec"),
    "parallel_threads": fields.Integer(default=0, description="Parallel threads (0 = disabled)"),
})

pygad_result_model = pygad_ns.model("PyGADResult", {
    "status": fields.String,
    "message": fields.String,
    "received_params": fields.Raw,
    "results": fields.Raw,
})

# ─── Defaults ────────────────────────────────────────────────────────────────

DEFAULTS = {
    "function_name": "hypersphere",
    "num_variables": 2,
    "num_generations": 100,
    "sol_per_pop": 50,
    "num_parents_mating": 10,
    "parent_selection": "tournament",
    "crossover_type": "single_point",
    "mutation_type": "random",
    "crossover_probability": 0.8,
    "mutation_probability": 0.01,
    "k_tournament": 3,
    "keep_elitism": 1,
    "representation": "binary",
    "bits_per_var": 20,
    "is_minimization": True,
    "use_custom_crossover": False,
    "use_gaussian_mutation": False,
    "parallel_threads": 0,
}


def _parse(data: dict) -> dict:
    def _bool(v, default):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return default

    return {
        "function_name":       str(data.get("function_name",       DEFAULTS["function_name"])),
        "num_variables":       int(data.get("num_variables",        DEFAULTS["num_variables"])),
        "num_generations":     int(data.get("num_generations",      DEFAULTS["num_generations"])),
        "sol_per_pop":         int(data.get("sol_per_pop",          DEFAULTS["sol_per_pop"])),
        "num_parents_mating":  int(data.get("num_parents_mating",   DEFAULTS["num_parents_mating"])),
        "parent_selection":    str(data.get("parent_selection",     DEFAULTS["parent_selection"])),
        "crossover_type":      str(data.get("crossover_type",       DEFAULTS["crossover_type"])),
        "mutation_type":       str(data.get("mutation_type",        DEFAULTS["mutation_type"])),
        "crossover_probability": float(data.get("crossover_probability", DEFAULTS["crossover_probability"])),
        "mutation_probability":  float(data.get("mutation_probability",  DEFAULTS["mutation_probability"])),
        "k_tournament":        int(data.get("k_tournament",         DEFAULTS["k_tournament"])),
        "keep_elitism":        int(data.get("keep_elitism",         DEFAULTS["keep_elitism"])),
        "representation":      str(data.get("representation",       DEFAULTS["representation"])),
        "bits_per_var":        int(data.get("bits_per_var",         DEFAULTS["bits_per_var"])),
        "is_minimization":     _bool(data.get("is_minimization"),   DEFAULTS["is_minimization"]),
        "use_custom_crossover":_bool(data.get("use_custom_crossover"), DEFAULTS["use_custom_crossover"]),
        "use_gaussian_mutation":_bool(data.get("use_gaussian_mutation"), DEFAULTS["use_gaussian_mutation"]),
        "parallel_threads":    int(data.get("parallel_threads",     DEFAULTS["parallel_threads"])),
    }


# ─── Resource ────────────────────────────────────────────────────────────────

@pygad_ns.route("/")
class PyGADOptimizationJob(Resource):

    @pygad_ns.expect(pygad_params_model, validate=False)
    @pygad_ns.marshal_with(pygad_result_model, code=200)
    @pygad_ns.doc(description="Run PyGAD optimization (binary or real representation).")
    def post(self):
        """Perform PyGAD-based genetic algorithm optimization"""
        data   = pygad_ns.payload or {}
        params = _parse(data)

        # Clamp num_parents_mating so it never exceeds sol_per_pop
        if params["num_parents_mating"] > params["sol_per_pop"]:
            params["num_parents_mating"] = params["sol_per_pop"]

        # Map frontend "custom" / "gaussian" aliases
        effective_crossover = params["crossover_type"]
        use_custom = params["use_custom_crossover"]
        if effective_crossover == "custom":
            use_custom = True
            effective_crossover = "single_point"  # fallback label

        effective_mutation = params["mutation_type"]
        use_gaussian = params["use_gaussian_mutation"]
        if effective_mutation == "gaussian":
            use_gaussian = True
            effective_mutation = "random"  # fallback label

        ga = PyGADAlgorithm(
            function_name        = params["function_name"],
            num_variables        = params["num_variables"],
            num_generations      = params["num_generations"],
            sol_per_pop          = params["sol_per_pop"],
            num_parents_mating   = params["num_parents_mating"],
            parent_selection     = params["parent_selection"],
            crossover_type       = effective_crossover,
            mutation_type        = effective_mutation,
            crossover_probability = params["crossover_probability"],
            mutation_probability  = params["mutation_probability"],
            k_tournament         = params["k_tournament"],
            keep_elitism         = params["keep_elitism"],
            representation       = params["representation"],
            bits_per_var         = params["bits_per_var"],
            is_minimization      = params["is_minimization"],
            use_custom_crossover = use_custom,
            use_gaussian_mutation= use_gaussian,
            parallel_threads     = params["parallel_threads"],
        )

        res = ga.run()

        return {
            "status": "success",
            "message": (
                f"PyGAD optimization finished in {res['execution_time']:.4f}s. "
                f"Function: {res['function_name']}, "
                f"Representation: {res['representation']}, "
                f"Domain: {res['domain']}."
            ),
            "received_params": params,
            "results": {
                "execution_time":         res["execution_time"],
                "best_fitness":           res["best_fitness"],
                "best_decoded_variables": res["best_decoded_variables"],
                "history":                res["history"],
                "domain":                 res["domain"],
                "function_name":          res["function_name"],
            },
        }, 200
