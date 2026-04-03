import React from 'react';
import { 
    Paper, 
    Typography, 
    Box, 
    Alert,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    IconButton,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    useTheme
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DownloadIcon from '@mui/icons-material/Download';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import CloseIcon from '@mui/icons-material/Close';
import { LineChart } from '@mui/x-charts/LineChart';
import { OptimizationResult as OptResultType } from '../types';

interface OptimizationResultProps {
    result: OptResultType | null;
    error: string | null;
}

const OptimizationResult: React.FC<OptimizationResultProps> = ({ result, error }) => {
    const theme = useTheme();
    const [chartDialogOpen, setChartDialogOpen] = React.useState(false);

    const extractExecutionTimeFromMessage = (message: string): number | null => {
        const match = message.match(/in\s+([0-9]+(?:\.[0-9]+)?)\s+seconds/i);
        if (!match) return null;

        const parsed = Number(match[1]);
        return Number.isFinite(parsed) ? parsed : null;
    };

    const handleDownload = () => {
        if (!result) return;

        const now = new Date().toISOString().replace(/[:.]/g, '-');
        const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');

        anchor.href = url;
        anchor.download = `optimization-result-${now}.json`;
        anchor.click();

        URL.revokeObjectURL(url);
    };

    const isSuccess = result?.status === 'success';
    const history = result?.results?.history ?? [];
    const executionTime = result?.results?.execution_time ?? (result ? extractExecutionTimeFromMessage(result.message) : null);
    const epochs = React.useMemo(() => history.map((point) => point.epoch), [history]);
    const bestFitnessSeries = React.useMemo(() => history.map((point) => point.best_fitness), [history]);
    const averageFitnessSeries = React.useMemo(() => history.map((point) => point.average_fitness), [history]);
    const worstFitnessSeries = React.useMemo(() => history.map((point) => point.worst_fitness), [history]);

    if (error) {
        return (
            <Alert severity="error" sx={{ mb: 4 }}>
                {error}
            </Alert>
        );
    }

    if (!result) return null;

    const successBgColor = theme.palette.mode === 'light' ? '#f8fff8' : 'rgba(76, 175, 80, 0.1)';
    const boxBgColor = theme.palette.mode === 'light' ? '#fff' : 'rgba(0, 0, 0, 0.3)';
    const boxBorderColor = theme.palette.mode === 'light' ? '#e0e0e0' : 'rgba(255, 255, 255, 0.1)';
    const codeBgColor = theme.palette.mode === 'light' ? '#f0f0f0' : 'rgba(0, 0, 0, 0.4)';

    const formatFitnessValue = (value: number | null): string => {
        if (value === null || !Number.isFinite(value)) return 'N/A';
        return value.toLocaleString('en-US', {
            useGrouping: false,
            maximumSignificantDigits: 17,
        });
    };

    const renderFitnessChart = (height: number, width?: number, large = false) => (
        <LineChart
            width={width}
            height={height}
            skipAnimation
            sx={{
                '& .MuiChartsLegend-label': {
                    fontSize: large ? 20 : 16,
                },
                '& .MuiChartsAxis-tickLabel': {
                    fontSize: large ? 20 : 16,
                },
            }}
            xAxis={[
                {
                    label: 'Epoch',
                    scaleType: 'linear',
                    data: epochs,
                },
            ]}
            series={[
                {
                    label: 'Best fitness',
                    data: bestFitnessSeries,
                    color: theme.palette.success.main,
                    valueFormatter: (value) => formatFitnessValue(value),
                    showMark: false,
                },
                {
                    label: 'Average fitness',
                    data: averageFitnessSeries,
                    color: theme.palette.info.main,
                    valueFormatter: (value) => formatFitnessValue(value),
                    showMark: false,
                },
                {
                    label: 'Worst fitness',
                    data: worstFitnessSeries,
                    color: theme.palette.error.main,
                    valueFormatter: (value) => formatFitnessValue(value),
                    showMark: false,
                },
            ]}
            margin={{ left: 20, right: 20, top: 20, bottom: 20 }}
            grid={{ vertical: true, horizontal: true }}
        />
    );

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
                            <strong>Execution Time:</strong> {executionTime !== null ? `${executionTime.toFixed(4)} s` : 'N/A'}
                        </Typography>
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

            {result.results && history.length > 0 && (
                <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="h6" gutterBottom>Fitness Across Iterations:</Typography>
                        <Button
                            variant="outlined"
                            size="small"
                            startIcon={<ZoomInIcon />}
                            onClick={() => setChartDialogOpen(true)}
                            sx={{
                                mb: 1,
                                color: 'text.primary',
                                borderColor: 'divider',
                                '&:hover': {
                                    borderColor: 'text.secondary',
                                    backgroundColor: 'action.hover',
                                },
                            }}
                        >
                            Open Large View
                        </Button>
                    </Box>
                    <Box sx={{ backgroundColor: boxBgColor, p: 1, borderRadius: 1, border: `1px solid ${boxBorderColor}` }}>
                        {renderFitnessChart(400, 700)}
                    </Box>
                </Box>
            )}

            <Dialog
                open={chartDialogOpen}
                onClose={() => setChartDialogOpen(false)}
                maxWidth={false}
                fullWidth
                PaperProps={{
                    sx: {
                        width: '96vw',
                        maxWidth: '96vw',
                        backgroundColor: theme.palette.background.paper,
                    },
                }}
            >
                <DialogTitle sx={{ pr: 6 }}>
                    Fitness Across Iterations (Large View)
                    <IconButton
                        aria-label="close"
                        onClick={() => setChartDialogOpen(false)}
                        sx={{ position: 'absolute', right: 8, top: 8 }}
                    >
                        <CloseIcon />
                    </IconButton>
                </DialogTitle>
                <DialogContent dividers sx={{ overflowX: 'auto', p: 2 }}>
                    {renderFitnessChart(760, 1800, true)}
                </DialogContent>
            </Dialog>

            <Box sx={{ mb: 3, display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={handleDownload}
                    disabled={!result.results}
                    sx={{
                        color: 'text.primary',
                        borderColor: 'divider',
                        '&:hover': {
                            borderColor: 'text.secondary',
                            backgroundColor: 'action.hover',
                        },
                    }}
                >
                    Save Result as JSON
                </Button>
            </Box>

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