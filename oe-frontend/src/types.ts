export interface AlgorithmParams {
    function_name: string;
    num_variables: number;
    precision: number;
    population_size: number;
    epochs: number;
    selection_method: string;
    crossover_method: string;
    mutation_method: string;
    crossover_prob: number;
    mutation_prob: number;
    inversion_prob: number;
    elite_strategy: boolean;
}

export interface OptimizationResult {
    status: string;
    message: string;
    results?: {
        best_fitness: number;
        best_decoded_variables: number[];
        history: any[];
    };
}
