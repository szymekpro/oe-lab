import React from 'react';
import { 
    Paper, 
    Typography, 
    Box, 
    Alert,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    useTheme
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { OptimizationResult as OptResultType } from '../types';

interface OptimizationResultProps {
    result: OptResultType | null;
    error: string | null;
}

const OptimizationResult: React.FC<OptimizationResultProps> = ({ result, error }) => {
    const theme = useTheme();

    if (error) {
        return (
            <Alert severity="error" sx={{ mb: 4 }}>
                {error}
            </Alert>
        );
    }

    if (!result) return null;

    const isSuccess = result.status === 'success';

    const successBgColor = theme.palette.mode === 'light' ? '#f8fff8' : 'rgba(76, 175, 80, 0.1)';
    const boxBgColor = theme.palette.mode === 'light' ? '#fff' : 'rgba(0, 0, 0, 0.3)';
    const boxBorderColor = theme.palette.mode === 'light' ? '#e0e0e0' : 'rgba(255, 255, 255, 0.1)';
    const codeBgColor = theme.palette.mode === 'light' ? '#f0f0f0' : 'rgba(0, 0, 0, 0.4)';

    return (
        <Paper elevation={3} sx={{ p: 4, mb: 4, backgroundColor: isSuccess ? successBgColor : 'background.paper' }}>
            <Typography variant="h5" component="h2" gutterBottom color={isSuccess ? 'success.main' : 'text.primary'}>
                Optimization Results
            </Typography>
            
            <Alert severity={isSuccess ? "success" : "info"} sx={{ mb: 3 }}>
                {result.message}
            </Alert>

            {result.results && (
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>Best Individual:</Typography>
                    <Box sx={{ backgroundColor: boxBgColor, p: 2, borderRadius: 1, border: `1px solid ${boxBorderColor}` }}>
                        <Typography variant="body1">
                            <strong>Fitness:</strong> {result.results.best_fitness}
                        </Typography>
                        <Typography variant="body1" sx={{ mt: 1 }}>
                            <strong>Decoded Variables:</strong> 
                            <Box component="span" sx={{ fontFamily: 'monospace', ml: 1, backgroundColor: codeBgColor, px: 1, py: 0.5, borderRadius: 1 }}>
                                [{result.results.best_decoded_variables.map(v => v.toFixed(6)).join(', ')}]
                            </Box>
                        </Typography>
                    </Box>
                </Box>
            )}

            <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography fontWeight="bold">Show full JSON response</Typography>
                </AccordionSummary>
                <AccordionDetails>
                    <Box 
                        component="pre" 
                        sx={{ 
                            backgroundColor: codeBgColor, 
                            color: theme.palette.mode === 'light' ? '#333' : '#e0e0e0', 
                            p: 2, 
                            borderRadius: 1,
                            overflowX: 'auto',
                            fontSize: '0.875rem'
                        }}
                    >
                        {JSON.stringify(result, null, 2)}
                    </Box>
                </AccordionDetails>
            </Accordion>
        </Paper>
    );
};

export default OptimizationResult;