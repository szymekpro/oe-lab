import React, { useState } from 'react';
import {
    Box,
    FormControlLabel,
    Checkbox,
    Paper,
    Typography
} from '@mui/material';
import { AlgorithmParams, RepresentationType } from '../types';
import CustomTextField from './common/CustomTextField';
import CustomButton from './common/CustomButton';

interface OptimizationFormProps {
    loading: boolean;
    onSubmit: (data: AlgorithmParams) => void;
}

const BINARY_CROSSOVER_OPTIONS = [
    { value: 'one_point', label: 'One Point' },
    { value: 'two_point', label: 'Two Point' },
    { value: 'uniform', label: 'Uniform' },
    { value: 'grain', label: 'Grain' },
];

const BINARY_MUTATION_OPTIONS = [
    { value: 'one_point', label: 'One Point' },
    { value: 'two_point', label: 'Two Point' },
    { value: 'edge', label: 'Edge Mutation' },
];

const REAL_CROSSOVER_OPTIONS = [
    { value: 'arithmetic', label: 'Arithmetic' },
    { value: 'linear', label: 'Linear' },
    { value: 'blend_alpha', label: 'Blend (BLX-α)' },
    { value: 'blend_alpha_beta', label: 'Blend (BLX-α-β)' },
    { value: 'averaging', label: 'Averaging' },
];

const REAL_MUTATION_OPTIONS = [
    { value: 'uniform_real', label: 'Uniform (real)' },
    { value: 'gaussian', label: 'Gaussian' },
];

const OptimizationForm: React.FC<OptimizationFormProps> = ({
    loading,
    onSubmit
}) => {
    const [representation, setRepresentation] = useState<RepresentationType>('binary');
    const isReal = representation === 'real';

    const handleFormSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const data = new FormData(e.currentTarget);

        onSubmit({
            function_name: data.get("function_name") as string,
            num_variables: Number(data.get("num_variables")),
            precision: Number(data.get("precision") ?? 6),
            population_size: Number(data.get("population_size")),
            epochs: Number(data.get("epochs")),
            selection_method: data.get("selection_method") as string,
            crossover_method: data.get("crossover_method") as string,
            mutation_method: data.get("mutation_method") as string,
            crossover_prob: Number(data.get("crossover_prob")),
            mutation_prob: Number(data.get("mutation_prob")),
            inversion_prob: Number(data.get("inversion_prob") ?? 0.05),
            elite_strategy: data.get("elite_strategy") === 'on',
            representation_type: representation,
            alpha: Number(data.get("alpha") ?? 0.5),
            beta: Number(data.get("beta") ?? 0.5),
            sigma: Number(data.get("sigma") ?? 0.1),
        });
    };

    return (
        <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
            <Typography variant="h5" component="h2" gutterBottom>
                Genetic Algorithm Configuration
            </Typography>
            <form onSubmit={handleFormSubmit}>
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: 3 }}>
                    <CustomTextField
                        label="Test Function"
                        name="function_name"
                        defaultValue="hypersphere"
                        gridSpan={6}
                        options={[{ value: 'hypersphere', label: 'Hypersphere' }]}
                    />

                    <CustomTextField
                        label="Representation"
                        name="representation_type_display"
                        defaultValue={representation}
                        gridSpan={6}
                        options={[
                            { value: 'binary', label: 'Binary' },
                            { value: 'real', label: 'Real-valued' },
                        ]}
                        onChange={(value) => setRepresentation(value as RepresentationType)}
                    />

                    <CustomTextField
                        type="number"
                        label="Number of Variables"
                        name="num_variables"
                        defaultValue={2}
                        gridSpan={isReal ? 6 : 4}
                        inputProps={{ min: 1 }}
                    />

                    {!isReal && (
                        <CustomTextField
                            type="number"
                            label="Precision (bits)"
                            name="precision"
                            defaultValue={6}
                            gridSpan={4}
                            inputProps={{ min: 1 }}
                        />
                    )}

                    <CustomTextField
                        type="number"
                        label="Population Size"
                        name="population_size"
                        defaultValue={50}
                        gridSpan={isReal ? 6 : 4}
                        inputProps={{ min: 2 }}
                    />

                    <CustomTextField
                        type="number"
                        label="Number of Epochs"
                        name="epochs"
                        defaultValue={100}
                        gridSpan={4}
                        inputProps={{ min: 1 }}
                    />

                    <CustomTextField
                        label="Selection Method"
                        name="selection_method"
                        defaultValue="roulette"
                        gridSpan={4}
                        options={[
                            { value: 'roulette', label: 'Roulette Wheel' },
                            { value: 'best', label: 'Best Selection' },
                            { value: 'tournament', label: 'Tournament' }
                        ]}
                    />

                    <CustomTextField
                        key={`crossover-${representation}`}
                        label="Crossover Method"
                        name="crossover_method"
                        defaultValue={isReal ? 'arithmetic' : 'one_point'}
                        gridSpan={4}
                        options={isReal ? REAL_CROSSOVER_OPTIONS : BINARY_CROSSOVER_OPTIONS}
                    />

                    <CustomTextField
                        key={`mutation-${representation}`}
                        label="Mutation Method"
                        name="mutation_method"
                        defaultValue={isReal ? 'gaussian' : 'one_point'}
                        gridSpan={4}
                        options={isReal ? REAL_MUTATION_OPTIONS : BINARY_MUTATION_OPTIONS}
                    />

                    <CustomTextField
                        type="number"
                        label="Crossover Probability"
                        name="crossover_prob"
                        defaultValue={0.8}
                        gridSpan={4}
                        inputProps={{ min: 0, max: 1, step: 0.01 }}
                    />

                    <CustomTextField
                        type="number"
                        label="Mutation Probability"
                        name="mutation_prob"
                        defaultValue={0.01}
                        gridSpan={4}
                        inputProps={{ min: 0, max: 1, step: 0.01 }}
                    />

                    {!isReal && (
                        <CustomTextField
                            type="number"
                            label="Inversion Probability"
                            name="inversion_prob"
                            defaultValue={0.05}
                            gridSpan={4}
                            inputProps={{ min: 0, max: 1, step: 0.01 }}
                        />
                    )}

                    {isReal && (
                        <>
                            <CustomTextField
                                type="number"
                                label="Alpha (BLX / arithmetic)"
                                name="alpha"
                                defaultValue={0.5}
                                gridSpan={4}
                                inputProps={{ min: 0, step: 0.05 }}
                            />
                            <CustomTextField
                                type="number"
                                label="Beta (BLX-α-β)"
                                name="beta"
                                defaultValue={0.5}
                                gridSpan={4}
                                inputProps={{ min: 0, step: 0.05 }}
                            />
                            <CustomTextField
                                type="number"
                                label="Sigma (Gaussian mut.)"
                                name="sigma"
                                defaultValue={0.1}
                                gridSpan={4}
                                inputProps={{ min: 0.0001, step: 'any' }}
                            />
                        </>
                    )}

                    <Box sx={{ gridColumn: { xs: 'span 12', sm: 'span 12' }, display: 'flex', alignItems: 'center' }}>
                        <FormControlLabel
                            control={
                                <Checkbox
                                    defaultChecked={true}
                                    name="elite_strategy"
                                    color="primary"
                                />
                            }
                            label="Elitism Strategy"
                        />
                    </Box>

                    <CustomButton
                        type="submit"
                        loading={loading}
                        loadingText="Calculating..."
                    >
                        Run Optimization
                    </CustomButton>
                </Box>
            </form>
        </Paper>
    );
};

export default OptimizationForm;