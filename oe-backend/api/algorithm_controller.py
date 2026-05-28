from flask_restx import Namespace, Resource, fields
from engine.functions import Hypersphere
from engine.algorithm import GeneticAlgorithm
from engine.real_algorithm import RealGeneticAlgorithm
from operators.selection import BestSelection, RouletteSelection, TournamentSelection
from operators.crossover import OnePointCrossover, TwoPointCrossover, UniformCrossover, GrainCrossover
from operators.mutation import OnePointMutation, TwoPointMutation, EdgeMutation
from operators.inversion import Inversion
from operators.real_crossover import (
    ArithmeticCrossover, LinearCrossover, BlendAlphaCrossover,
    BlendAlphaBetaCrossover, AveragingCrossover,
)
from operators.real_mutation import UniformRealMutation, GaussianMutation

algorithm_ns = Namespace("optimizations", description="Genetic algorithm optimization", path="/optimizations")

algorithm_params_model = algorithm_ns.model("AlgorithmParams", {
    "function_name": fields.String(default="hypersphere", description="Name of the test function"),
    "num_variables": fields.Integer(default=2, description="Number of variables"),
    "precision": fields.Integer(default=6, description="Decimal precision (binary only)"),
    "population_size": fields.Integer(default=50, description="Size of the population"),
    "epochs": fields.Integer(default=100, description="Number of epochs/generations"),
    "selection_method": fields.String(default="roulette",
                                      description="Selection: best | roulette | tournament"),
    "crossover_method": fields.String(default="one_point",
                                      description=(
                                          "Binary: one_point | two_point | uniform | grain. "
                                          "Real: arithmetic | linear | blend_alpha | blend_alpha_beta | averaging"
                                      )),
    "mutation_method": fields.String(default="one_point",
                                     description=(
                                         "Binary: one_point | two_point | edge. "
                                         "Real: uniform_real | gaussian"
                                     )),
    "crossover_prob": fields.Float(default=0.8, description="Probability of crossover"),
    "mutation_prob": fields.Float(default=0.01, description="Probability of mutation"),
    "inversion_prob": fields.Float(default=0.05, description="Probability of inversion (binary only)"),
    "elite_strategy": fields.Boolean(default=True, description="Whether to use elitism strategy"),
    "is_minimization": fields.Boolean(default=True, description="True = minimization, False = maximization"),
    "representation_type": fields.String(default="binary",
                                         description="Chromosome encoding: binary | real"),
    "alpha": fields.Float(default=0.5,
                          description="Alpha parameter for blend_alpha, blend_alpha_beta, arithmetic crossover"),
    "beta": fields.Float(default=0.5, description="Beta parameter for blend_alpha_beta crossover"),
    "sigma": fields.Float(default=0.1, description="Sigma (std dev) for Gaussian mutation"),
})

optimization_result_model = algorithm_ns.model("OptimizationResult", {
    "status": fields.String,
    "message": fields.String,
    "received_params": fields.Raw,
    "results": fields.Raw,
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
    "is_minimization": True,
    "representation_type": "binary",
    "alpha": 0.5,
    "beta": 0.5,
    "sigma": 0.1,
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
        "is_minimization": bool(data.get("is_minimization", DEFAULTS["is_minimization"])),
        "representation_type": str(data.get("representation_type", DEFAULTS["representation_type"])),
        "alpha": float(data.get("alpha", DEFAULTS["alpha"])),
        "beta": float(data.get("beta", DEFAULTS["beta"])),
        "sigma": float(data.get("sigma", DEFAULTS["sigma"])),
    }


def _build_selection(method: str):
    if method == "best":
        return BestSelection()
    if method == "tournament":
        return TournamentSelection()
    return RouletteSelection()


def _build_binary_crossover(method: str):
    if method == "two_point":
        return TwoPointCrossover()
    if method == "uniform":
        return UniformCrossover()
    if method == "grain":
        return GrainCrossover()
    return OnePointCrossover()


def _build_binary_mutation(method: str):
    if method == "two_point":
        return TwoPointMutation()
    if method == "edge":
        return EdgeMutation()
    return OnePointMutation()


def _build_real_crossover(method: str, alpha: float, beta: float, test_func, is_minimization: bool):
    if method == "arithmetic":
        return ArithmeticCrossover()
    if method == "linear":
        return LinearCrossover(test_function=test_func, is_minimization=is_minimization)
    if method == "blend_alpha":
        return BlendAlphaCrossover(alpha=alpha)
    if method == "blend_alpha_beta":
        return BlendAlphaBetaCrossover(alpha=alpha, beta=beta)
    return AveragingCrossover()


def _build_real_mutation(method: str, sigma: float):
    if method == "gaussian":
        return GaussianMutation(sigma=sigma)
    return UniformRealMutation()


@algorithm_ns.route("/")
class OptimizationJob(Resource):

    @algorithm_ns.expect(algorithm_params_model, validate=False)
    @algorithm_ns.marshal_with(optimization_result_model, code=200)
    @algorithm_ns.doc(description="Performs optimization using the Genetic Engine.")
    def post(self):
        """Perform optimization job (binary or real-valued representation)"""
        data = algorithm_ns.payload or {}
        params = parse_params(data)

        test_func = Hypersphere()
        selection = _build_selection(params["selection_method"])

        if params["representation_type"] == "real":
            crossover = _build_real_crossover(
                params["crossover_method"], params["alpha"], params["beta"],
                test_func, params["is_minimization"],
            )
            mutation = _build_real_mutation(params["mutation_method"], params["sigma"])

            ga = RealGeneticAlgorithm(
                test_function=test_func,
                population_size=params["population_size"],
                num_variables=params["num_variables"],
                epochs=params["epochs"],
                selection=selection,
                crossover=crossover,
                mutation=mutation,
                crossover_prob=params["crossover_prob"],
                mutation_prob=params["mutation_prob"],
                elite_strategy=params["elite_strategy"],
                is_minimization=params["is_minimization"],
            )
        else:
            crossover = _build_binary_crossover(params["crossover_method"])
            mutation = _build_binary_mutation(params["mutation_method"])
            inversion = Inversion()

            ga = GeneticAlgorithm(
                test_function=test_func,
                population_size=params["population_size"],
                num_variables=params["num_variables"],
                precision=params["precision"],
                epochs=params["epochs"],
                selection=selection,
                crossover=crossover,
                mutation=mutation,
                crossover_prob=params["crossover_prob"],
                mutation_prob=params["mutation_prob"],
                inversion=inversion,
                inversion_prob=params["inversion_prob"],
                elite_strategy=params["elite_strategy"],
                is_minimization=params["is_minimization"],
            )

        execution_results = ga.run()
        best_individual = execution_results["best"]

        return {
            "status": "success",
            "message": (
                f"Optimization finished successfully in {execution_results['time']:.4f} seconds. "
                f"Representation: {params['representation_type']}."
            ),
            "received_params": params,
            "results": {
                "execution_time": execution_results["time"],
                "best_fitness": best_individual.fitness,
                "best_decoded_variables": best_individual.get_decoded_values(),
                "history": execution_results["history"],
            },
        }, 200
