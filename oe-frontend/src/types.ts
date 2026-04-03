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

export interface HistoryPoint {
    epoch: number;
    best_fitness: number;
    average_fitness: number;
    worst_fitness: number;
}

export interface OptimizationResult {
    status: string;
    message: string;
    results?: {
        execution_time?: number;
        best_fitness: number;
        best_decoded_variables: number[];
        history: HistoryPoint[];
    };
}
