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
import PsychologyAltIcon from '@mui/icons-material/PsychologyAlt';
import { PyGADParams, PyGADRepresentationType } from '../types';
import CustomTextField from './common/CustomTextField';
import CustomButton from './common/CustomButton';

interface PyGADFormProps {
    loading: boolean;
    onSubmit: (data: PyGADParams) => void;
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

const SELECTION_OPTIONS = [
    { value: 'tournament', label: 'Tournament' },
    { value: 'rws',        label: 'Roulette Wheel' },
    { value: 'random',     label: 'Random' },
    { value: 'rank',       label: 'Rank' },
    { value: 'sss',        label: 'Steady-State (SSS)' },
];

const CROSSOVER_OPTIONS = [
    { value: 'single_point', label: 'Single Point' },
    { value: 'two_points',   label: 'Two Points' },
    { value: 'uniform',      label: 'Uniform' },
    { value: 'scattered',    label: 'Scattered' },
    { value: 'custom',       label: 'Custom (P3 spec)' },
];

const MUTATION_OPTIONS = [
    { value: 'random',    label: 'Random' },
    { value: 'swap',      label: 'Swap' },
    { value: 'inversion', label: 'Inversion' },
    { value: 'scramble',  label: 'Scramble' },
    { value: 'gaussian',  label: 'Gaussian (P3 spec)' },
];

const PyGADForm: React.FC<PyGADFormProps> = ({ loading, onSubmit }) => {
    const [representation, setRepresentation] = useState<PyGADRepresentationType>('binary');
    const isBinary = representation === 'binary';

    const handleFormSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const data = new FormData(e.currentTarget);

        const crossoverType = data.get('crossover_type') as string;
        const mutationType  = data.get('mutation_type') as string;
        const eliteStrategy = data.get('elite_strategy') === 'on';

        onSubmit({
            function_name:         data.get('function_name') as string,
            num_variables:         Number(data.get('num_variables')),
            num_generations:       Number(data.get('num_generations')),
            sol_per_pop:           Number(data.get('sol_per_pop')),
            num_parents_mating:    Number(data.get('num_parents_mating')),
            parent_selection:      data.get('parent_selection') as string,
            crossover_type:        crossoverType,
            mutation_type:         mutationType,
            crossover_probability: Number(data.get('crossover_probability')),
            mutation_probability:  Number(data.get('mutation_probability')),
            k_tournament:          Number(data.get('k_tournament')),
            keep_elitism:          eliteStrategy ? 1 : 0,
            representation,
            bits_per_var:          isBinary ? Number(data.get('bits_per_var')) : 20,
            is_minimization:       true,
            use_custom_crossover:  crossoverType === 'custom',
            use_gaussian_mutation: mutationType === 'gaussian',
            parallel_threads:      Number(data.get('parallel_threads') ?? 0),
        });
    };

    return (
        <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <PsychologyAltIcon color="secondary" />
                <Typography variant="h5" component="h2">
                    PyGAD Configuration
                </Typography>
                <Chip label="Projekt 3" size="small" color="secondary" variant="outlined" sx={{ ml: 1 }} />
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Uses the <strong>PyGAD</strong> library. Binary mode encodes variables as int genes (0/1);
                real mode uses float genes directly.
            </Typography>

            <Divider sx={{ mb: 3 }} />

            <form onSubmit={handleFormSubmit}>
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: 3 }}>

                    {/* ── Row 1: Test Function | Representation ── */}
                    <CustomTextField
                        label="Test Function"
                        name="function_name"
                        defaultValue="hypersphere"
                        gridSpan={6}
                        options={FUNCTION_OPTIONS}
                    />

                    <CustomTextField
                        label="Representation"
                        name="representation_display"
                        defaultValue={representation}
                        gridSpan={6}
                        options={[
                            { value: 'binary', label: 'Binary' },
                            { value: 'real',   label: 'Real-valued' },
                        ]}
                        onChange={(v) => setRepresentation(v as PyGADRepresentationType)}
                    />

                    {/* ── Row 2: Number of Variables | Bits per Variable (binary) | Population Size ── */}
                    <CustomTextField
                        type="number"
                        label="Number of Variables"
                        name="num_variables"
                        defaultValue={2}
                        gridSpan={isBinary ? 4 : 6}
                        inputProps={{ min: 1, max: 50 }}
                    />

                    {isBinary && (
                        <CustomTextField
                            type="number"
                            label="Bits per Variable"
                            name="bits_per_var"
                            defaultValue={20}
                            gridSpan={4}
                            inputProps={{ min: 4, max: 32 }}
                        />
                    )}

                    <CustomTextField
                        type="number"
                        label="Population Size"
                        name="sol_per_pop"
                        defaultValue={50}
                        gridSpan={isBinary ? 4 : 6}
                        inputProps={{ min: 4 }}
                    />

                    {/* ── Row 3: Number of Epochs | Selection Method | Tournament Size ── */}
                    <CustomTextField
                        type="number"
                        label="Number of Epochs"
                        name="num_generations"
                        defaultValue={100}
                        gridSpan={4}
                        inputProps={{ min: 1 }}
                    />

                    <CustomTextField
                        label="Selection Method"
                        name="parent_selection"
                        defaultValue="tournament"
                        gridSpan={4}
                        options={SELECTION_OPTIONS}
                    />

                    <CustomTextField
                        type="number"
                        label="Tournament Size (K)"
                        name="k_tournament"
                        defaultValue={3}
                        gridSpan={4}
                        inputProps={{ min: 2 }}
                    />

                    {/* ── Row 4: Crossover Method | Mutation Method | Genes Mutated ── */}
                    <CustomTextField
                        key={`crossover-${representation}`}
                        label="Crossover Method"
                        name="crossover_type"
                        defaultValue="single_point"
                        gridSpan={4}
                        options={CROSSOVER_OPTIONS}
                    />

                    <CustomTextField
                        key={`mutation-${representation}`}
                        label="Mutation Method"
                        name="mutation_type"
                        defaultValue="random"
                        gridSpan={4}
                        options={MUTATION_OPTIONS}
                    />

                    <CustomTextField
                        type="number"
                        label="Crossover Probability"
                        name="crossover_probability"
                        defaultValue={0.8}
                        gridSpan={4}
                        inputProps={{ min: 0, max: 1, step: 0.01 }}
                    />

                    <CustomTextField
                        type="number"
                        label="Mutation Probability"
                        name="mutation_probability"
                        defaultValue={0.01}
                        gridSpan={4}
                        inputProps={{ min: 0, max: 1, step: 0.01 }}
                    />

                    {/* ── Row 5: Parents Mating | Parallel Threads ── */}
                    <CustomTextField
                        type="number"
                        label="Parents Mating"
                        name="num_parents_mating"
                        defaultValue={10}
                        gridSpan={4}
                        inputProps={{ min: 2 }}
                    />

                    <CustomTextField
                        type="number"
                        label="Parallel Threads (0=off)"
                        name="parallel_threads"
                        defaultValue={0}
                        gridSpan={4}
                        inputProps={{ min: 0, max: 16 }}
                    />

                    {/* ── Elitism Strategy checkbox – same as OptimizationForm ── */}
                    <Box sx={{ gridColumn: { xs: 'span 12' }, display: 'flex', alignItems: 'center' }}>
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

                    <CustomButton type="submit" loading={loading} loadingText="Running PyGAD...">
                        Run PyGAD Optimization
                    </CustomButton>
                </Box>
            </form>
        </Paper>
    );
};

export default PyGADForm;
