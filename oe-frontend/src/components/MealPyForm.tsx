import React, { useState } from 'react';
import {
    Box,
    FormControlLabel,
    Checkbox,
    Paper,
    Typography,
    Divider,
    Chip,
} from '@mui/material';
import HubIcon from '@mui/icons-material/Hub';
import { MealPyParams } from '../types';
import CustomTextField from './common/CustomTextField';
import CustomButton from './common/CustomButton';

interface MealPyFormProps {
    loading: boolean;
    onSubmit: (data: MealPyParams) => void;
}

const FUNCTION_OPTIONS = [
    { value: 'hypersphere',     label: 'Hypersphere' },
    { value: 'hyperellipsoid',  label: 'Hyperellipsoid' },
    { value: 'rastrigin',       label: 'Rastrigin' },
    { value: 'rosenbrock',      label: 'Rosenbrock' },
    { value: 'ackley',          label: 'Ackley' },
    { value: 'schwefel',        label: 'Schwefel' },
    { value: 'griewank',        label: 'Griewank' },
    { value: 'himmelblau',      label: 'Himmelblau (2D)' },
    { value: 'michalewicz',     label: 'Michalewicz' },
    { value: 'styblinski_tang', label: 'Styblinski-Tang' },
];

const STRATEGY_OPTIONS = [
    { value: '0', label: '0 — DE/rand/1' },
    { value: '1', label: '1 — DE/best/1' },
    { value: '2', label: '2 — DE/rand-to-best/1' },
    { value: '3', label: '3 — DE/rand/2' },
    { value: '4', label: '4 — DE/best/2' },
    { value: '5', label: '5 — DE/rand-to-best/2' },
];

const MealPyForm: React.FC<MealPyFormProps> = ({ loading, onSubmit }) => {
    const [isMinimization, setIsMinimization] = useState(true);

    const handleFormSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const data = new FormData(e.currentTarget);

        const rawSeed = data.get('seed') as string;
        const seed = rawSeed.trim() === '' ? null : Number(rawSeed);

        onSubmit({
            function_name:  data.get('function_name') as string,
            num_variables:  Number(data.get('num_variables')),
            epoch:          Number(data.get('epoch')),
            pop_size:       Number(data.get('pop_size')),
            wf:             Number(data.get('wf')),
            cr:             Number(data.get('cr')),
            strategy:       Number(data.get('strategy')),
            is_minimization: isMinimization,
            seed,
        });
    };

    return (
        <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <HubIcon color="primary" />
                <Typography variant="h5" component="h2">
                    MealPy DE Configuration
                </Typography>
                <Chip label="Projekt 4" size="small" color="primary" variant="outlined" sx={{ ml: 1 }} />
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Uses <strong>Differential Evolution</strong> (DE) from the <strong>MealPy</strong> library.
                DE mutates candidate solutions by combining differences between individuals —
                no gradient required, effective for non-convex continuous problems.
            </Typography>

            <Divider sx={{ mb: 3 }} />

            <form onSubmit={handleFormSubmit}>
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: 3 }}>

                    {/* ── Row 1: Function | Variables ── */}
                    <CustomTextField
                        label="Test Function"
                        name="function_name"
                        defaultValue="hypersphere"
                        gridSpan={6}
                        options={FUNCTION_OPTIONS}
                    />

                    <CustomTextField
                        type="number"
                        label="Number of Variables"
                        name="num_variables"
                        defaultValue={2}
                        gridSpan={6}
                        inputProps={{ min: 1, max: 50 }}
                    />

                    {/* ── Row 2: Epochs | Population size ── */}
                    <CustomTextField
                        type="number"
                        label="Epochs (iterations)"
                        name="epoch"
                        defaultValue={100}
                        gridSpan={6}
                        inputProps={{ min: 1 }}
                    />

                    <CustomTextField
                        type="number"
                        label="Population Size"
                        name="pop_size"
                        defaultValue={50}
                        gridSpan={6}
                        inputProps={{ min: 4 }}
                    />

                    {/* ── Row 3: DE params ── */}
                    <CustomTextField
                        type="number"
                        label="Weighting Factor (wf)"
                        name="wf"
                        defaultValue={0.7}
                        gridSpan={4}
                        inputProps={{ min: 0.01, max: 2, step: 0.01 }}
                    />

                    <CustomTextField
                        type="number"
                        label="Crossover Rate (cr)"
                        name="cr"
                        defaultValue={0.9}
                        gridSpan={4}
                        inputProps={{ min: 0, max: 1, step: 0.01 }}
                    />

                    <CustomTextField
                        label="DE Strategy"
                        name="strategy"
                        defaultValue="0"
                        gridSpan={4}
                        options={STRATEGY_OPTIONS}
                    />

                    {/* ── Row 4: Seed ── */}
                    <CustomTextField
                        type="number"
                        label="RNG Seed (leave empty = random)"
                        name="seed"
                        defaultValue=""
                        gridSpan={6}
                        inputProps={{ min: 0 }}
                    />

                    {/* ── Minimization checkbox ── */}
                    <Box sx={{ gridColumn: 'span 12', display: 'flex', alignItems: 'center' }}>
                        <FormControlLabel
                            control={
                                <Checkbox
                                    checked={isMinimization}
                                    onChange={(e) => setIsMinimization(e.target.checked)}
                                    color="primary"
                                />
                            }
                            label="Minimization (uncheck for maximization)"
                        />
                    </Box>

                    <CustomButton type="submit" loading={loading} loadingText="Running MealPy DE...">
                        Run MealPy Optimization
                    </CustomButton>
                </Box>
            </form>
        </Paper>
    );
};

export default MealPyForm;
