export type RepresentationType = 'binary' | 'real';
export type PyGADRepresentationType = 'binary' | 'real';

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
    representation_type: RepresentationType;
    alpha: number;
    beta: number;
    sigma: number;
}

export interface PyGADParams {
    function_name: string;
    num_variables: number;
    num_generations: number;
    sol_per_pop: number;
    num_parents_mating: number;
    parent_selection: string;
    crossover_type: string;
    mutation_type: string;
    crossover_probability: number;
    mutation_probability: number;
    k_tournament: number;
    keep_elitism: number;
    representation: PyGADRepresentationType;
    bits_per_var: number;
    is_minimization: boolean;
    use_custom_crossover: boolean;
    use_gaussian_mutation: boolean;
    parallel_threads: number;
}

export interface HistoryPoint {
    epoch: number;
    best_fitness: number;
    average_fitness: number;
    worst_fitness: number;
    std_fitness?: number;
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

export interface PyGADResult {
    status: string;
    message: string;
    received_params?: Record<string, unknown>;
    results?: {
        execution_time: number;
        best_fitness: number;
        best_decoded_variables: number[];
        history: HistoryPoint[];
        domain: [number, number];
        function_name: string;
    };
}

export interface MealPyParams {
    function_name: string;
    num_variables: number;
    epoch: number;
    pop_size: number;
    wf: number;
    cr: number;
    strategy: number;
    is_minimization: boolean;
    seed: number | null;
}

export interface MealPyResult {
    status: string;
    message: string;
    received_params?: Record<string, unknown>;
    results?: {
        execution_time: number;
        best_fitness: number;
        best_decoded_variables: number[];
        history: HistoryPoint[];
        domain: [number, number];
        function_name: string;
        wf: number;
        cr: number;
        strategy: number;
    };
}
