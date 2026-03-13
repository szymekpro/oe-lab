import React from 'react';
import { 
    Box, 
    FormControlLabel, 
    Checkbox, 
    Paper, 
    Typography
} from '@mui/material';
import { AlgorithmParams } from '../types';
import CustomTextField from './common/CustomTextField';
import CustomButton from './common/CustomButton';

interface OptimizationFormProps {
    loading: boolean;
    onSubmit: (data: AlgorithmParams) => void;
}

const OptimizationForm: React.FC<OptimizationFormProps> = ({ 
    loading, 
    onSubmit 
}) => {
    const handleFormSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const data = new FormData(e.currentTarget);
        
        onSubmit({
            function_name: data.get("function_name") as string,
            num_variables: Number(data.get("num_variables")),
            precision: Number(data.get("precision")),
            population_size: Number(data.get("population_size")),
            epochs: Number(data.get("epochs")),
            selection_method: data.get("selection_method") as string,
            crossover_method: data.get("crossover_method") as string,
            mutation_method: data.get("mutation_method") as string,
            crossover_prob: Number(data.get("crossover_prob")),
            mutation_prob: Number(data.get("mutation_prob")),
            inversion_prob: Number(data.get("inversion_prob")),
            elite_strategy: data.get("elite_strategy") === 'on',
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
                        type="number"
                        label="Number of Variables"
                        name="num_variables"
                        defaultValue={2}
                        gridSpan={6}
                        inputProps={{ min: 1 }}
                    />

                    <CustomTextField
                        type="number"
                        label="Precision (bits)"
                        name="precision"
                        defaultValue={6}
                        gridSpan={4}
                        inputProps={{ min: 1 }}
                    />

                    <CustomTextField
                        type="number"
                        label="Population Size"
                        name="population_size"
                        defaultValue={50}
                        gridSpan={4}
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
                        label="Crossover Method"
                        name="crossover_method"
                        defaultValue="one_point"
                        gridSpan={4}
                        options={[{ value: 'one_point', label: 'One Point' }]}
                    />

                    <CustomTextField
                        label="Mutation Method"
                        name="mutation_method"
                        defaultValue="one_point"
                        gridSpan={4}
                        options={[{ value: 'one_point', label: 'One Point' }]}
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

                    <CustomTextField
                        type="number"
                        label="Inversion Probability"
                        name="inversion_prob"
                        defaultValue={0.05}
                        gridSpan={4}
                        inputProps={{ min: 0, max: 1, step: 0.01 }}
                    />

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