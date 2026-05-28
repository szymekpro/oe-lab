from flask_restx import Namespace, Resource, fields
from engine.mealpy_algorithm import MealPyAlgorithm, BENCHMARK_FUNCTIONS

mealpy_ns = Namespace(
    "mealpy",
    description="MealPy Differential Evolution optimization (Projekt 4)",
    path="/mealpy",
)

mealpy_params_model = mealpy_ns.model("MealPyParams", {
    "function_name": fields.String(
        default="hypersphere",
        description="Benchmark function: " + " | ".join(BENCHMARK_FUNCTIONS.keys()),
    ),
    "num_variables":  fields.Integer(default=2,    description="Number of decision variables"),
    "epoch":          fields.Integer(default=100,  description="Number of iterations"),
    "pop_size":       fields.Integer(default=50,   description="Population size"),
    "wf":             fields.Float(default=0.7,    description="DE weighting factor (mutation scale), 0 < wf <= 2"),
    "cr":             fields.Float(default=0.9,    description="DE crossover rate, 0 <= cr <= 1"),
    "strategy":       fields.Integer(default=0,    description="DE strategy (0–5)"),
    "is_minimization": fields.Boolean(default=True, description="True = minimise, False = maximise"),
    "seed":           fields.Integer(default=None, description="Optional RNG seed"),
})

mealpy_result_model = mealpy_ns.model("MealPyResult", {
    "status":         fields.String,
    "message":        fields.String,
    "received_params": fields.Raw,
    "results":        fields.Raw,
})

DEFAULTS = {
    "function_name": "hypersphere",
    "num_variables": 2,
    "epoch":         100,
    "pop_size":      50,
    "wf":            0.7,
    "cr":            0.9,
    "strategy":      0,
    "is_minimization": True,
    "seed":          None,
}


def _parse(data: dict) -> dict:
    def _bool(v, default):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return default

    seed = data.get("seed", DEFAULTS["seed"])
    try:
        seed = int(seed) if seed is not None and seed != "" else None
    except (TypeError, ValueError):
        seed = None

    return {
        "function_name":   str(data.get("function_name",   DEFAULTS["function_name"])),
        "num_variables":   int(data.get("num_variables",   DEFAULTS["num_variables"])),
        "epoch":           int(data.get("epoch",           DEFAULTS["epoch"])),
        "pop_size":        int(data.get("pop_size",        DEFAULTS["pop_size"])),
        "wf":              float(data.get("wf",            DEFAULTS["wf"])),
        "cr":              float(data.get("cr",            DEFAULTS["cr"])),
        "strategy":        int(data.get("strategy",        DEFAULTS["strategy"])),
        "is_minimization": _bool(data.get("is_minimization"), DEFAULTS["is_minimization"]),
        "seed":            seed,
    }


@mealpy_ns.route("/")
class MealPyOptimizationJob(Resource):

    @mealpy_ns.expect(mealpy_params_model, validate=False)
    @mealpy_ns.marshal_with(mealpy_result_model, code=200)
    @mealpy_ns.doc(description="Run DE (Differential Evolution) optimization via MealPy.")
    def post(self):
        """Perform MealPy Differential Evolution optimization"""
        data = mealpy_ns.payload or {}
        params = _parse(data)

        de = MealPyAlgorithm(
            function_name   = params["function_name"],
            num_variables   = params["num_variables"],
            epoch           = params["epoch"],
            pop_size        = params["pop_size"],
            wf              = params["wf"],
            cr              = params["cr"],
            strategy        = params["strategy"],
            is_minimization = params["is_minimization"],
            seed            = params["seed"],
        )

        res = de.run()

        return {
            "status": "success",
            "message": (
                "MealPy DE finished in {:.4f}s. "
                "Function: {}, Domain: {}, "
                "wf={}, cr={}, strategy={}.".format(
                    res["execution_time"],
                    res["function_name"],
                    res["domain"],
                    res["wf"], res["cr"], res["strategy"],
                )
            ),
            "received_params": params,
            "results": {
                "execution_time":         res["execution_time"],
                "best_fitness":           res["best_fitness"],
                "best_decoded_variables": res["best_decoded_variables"],
                "history":                res["history"],
                "domain":                 res["domain"],
                "function_name":          res["function_name"],
                "wf":                     res["wf"],
                "cr":                     res["cr"],
                "strategy":               res["strategy"],
            },
        }, 200
