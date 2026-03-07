from flask_restx import Namespace, Resource, fields
from flask import request

algorithm_ns = Namespace("optimizations", description="Genetic algorithm optimization", path="/optimizations")

algorithm_params_model = algorithm_ns.model("AlgorithmParams", {
    "function_name": fields.String(default="hypersphere", description="Name of the test function"),
    "num_variables": fields.Integer(default=2, description="Number of variables"),
    "precision": fields.Integer(default=6, description="Decimal precision"),
    "population_size": fields.Integer(default=50, description="Size of the population"),
    "epochs": fields.Integer(default=100, description="Number of epochs/generations"),
    "selection_method": fields.String(default="roulette", description="Selection method type"),
    "crossover_method": fields.String(default="one_point", description="Crossover method type"),
    "mutation_method": fields.String(default="one_point", description="Mutation method type"),
    "crossover_prob": fields.Float(default=0.8, description="Probability of crossover"),
    "mutation_prob": fields.Float(default=0.01, description="Probability of mutation"),
    "inversion_prob": fields.Float(default=0.05, description="Probability of inversion"),
    "elite_strategy": fields.Boolean(default=True, description="Whether to use elitism strategy"),
})

optimization_result_model = algorithm_ns.model("OptimizationResult", {
    "status": fields.String,
    "message": fields.String,
    "received_params": fields.Raw,
    "dummy_results": fields.Raw,
})

DEFAULTS = {
    "function_name": "hypersphere",
    "num_variables": 2,
    "precision": 6,
    "population_size": 50,
    "epochs": 100,
    "selection_method": "roulette",
    "crossover_method": "one_point",
    "mutation_method": "one_point",
    "crossover_prob": 0.8,
    "mutation_prob": 0.01,
    "inversion_prob": 0.05,
    "elite_strategy": True,
}


def parse_params(data: dict) -> dict:
    return {
        "function_name": str(data.get("function_name", DEFAULTS["function_name"])),
        "num_variables": int(data.get("num_variables", DEFAULTS["num_variables"])),
        "precision": int(data.get("precision", DEFAULTS["precision"])),
        "population_size": int(data.get("population_size", DEFAULTS["population_size"])),
        "epochs": int(data.get("epochs", DEFAULTS["epochs"])),
        "selection_method": str(data.get("selection_method", DEFAULTS["selection_method"])),
        "crossover_method": str(data.get("crossover_method", DEFAULTS["crossover_method"])),
        "mutation_method": str(data.get("mutation_method", DEFAULTS["mutation_method"])),
        "crossover_prob": float(data.get("crossover_prob", DEFAULTS["crossover_prob"])),
        "mutation_prob": float(data.get("mutation_prob", DEFAULTS["mutation_prob"])),
        "inversion_prob": float(data.get("inversion_prob", DEFAULTS["inversion_prob"])),
        "elite_strategy": bool(data.get("elite_strategy", DEFAULTS["elite_strategy"])),
    }


@algorithm_ns.route("/")
class OptimizationJob(Resource):

    @algorithm_ns.expect(algorithm_params_model, validate=False)
    @algorithm_ns.marshal_with(optimization_result_model, code=200)
    @algorithm_ns.doc(description="Performs the optimization job based on the provided parameters and returns results.")
    def post(self):
        """Perform optimization job"""
        data = algorithm_ns.payload or {}
        params = parse_params(data)

        return {
            "status": "success",
            "message": "OK.",
            "received_params": params,
            "dummy_results": {
                "best_fitness": 0.001,
                "best_solution": [0.001, -0.002],
            },
        }, 200
