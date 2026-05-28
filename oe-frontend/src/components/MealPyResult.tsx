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
    useTheme,
    Chip,
    Stack,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DownloadIcon from '@mui/icons-material/Download';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import CloseIcon from '@mui/icons-material/Close';
import { LineChart } from '@mui/x-charts/LineChart';
import { MealPyResult as MealPyResultType } from '../types';

const STRATEGY_LABELS: Record<number, string> = {
    0: 'DE/rand/1',
    1: 'DE/best/1',
    2: 'DE/rand-to-best/1',
    3: 'DE/rand/2',
    4: 'DE/best/2',
    5: 'DE/rand-to-best/2',
};

interface MealPyResultProps {
    result: MealPyResultType | null;
    error: string | null;
}

const MealPyResult: React.FC<MealPyResultProps> = ({ result, error }) => {
    const theme = useTheme();
    const [chartDialogOpen, setChartDialogOpen] = React.useState(false);
    const [stdDialogOpen, setStdDialogOpen] = React.useState(false);

    const handleDownload = () => {
        if (!result) return;
        const now = new Date().toISOString().replace(/[:.]/g, '-');
        const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = `mealpy-result-${now}.json`;
        anchor.click();
        URL.revokeObjectURL(url);
    };

    const isSuccess = result?.status === 'success';
    const history  = result?.results?.history ?? [];

    const epochs = React.useMemo(() => history.map((p) => p.epoch),            [history]);
    const best   = React.useMemo(() => history.map((p) => p.best_fitness),     [history]);
    const avg    = React.useMemo(() => history.map((p) => p.average_fitness),  [history]);
    const worst  = React.useMemo(() => history.map((p) => p.worst_fitness),    [history]);
    const stdDev = React.useMemo(
        () => history.map((p) => (p as any).std_fitness ?? null),
        [history],
    );

    if (error) return <Alert severity="error" sx={{ mb: 4 }}>{error}</Alert>;
    if (!result) return null;

    const successBgColor = theme.palette.mode === 'light' ? '#f8fff8' : 'rgba(76, 175, 80, 0.1)';
    const boxBgColor     = theme.palette.mode === 'light' ? '#fff'    : 'rgba(0, 0, 0, 0.3)';
    const boxBorderColor = theme.palette.mode === 'light' ? '#e0e0e0' : 'rgba(255,255,255,0.1)';
    const codeBgColor    = theme.palette.mode === 'light' ? '#f0f0f0' : 'rgba(0, 0, 0, 0.4)';

    const fmt = (v: number | null) =>
        v === null || !Number.isFinite(v)
            ? 'N/A'
            : v.toLocaleString('en-US', { useGrouping: false, maximumSignificantDigits: 17 });

    const renderFitnessChart = (height: number, width?: number, large = false) => (
        <LineChart
            width={width}
            height={height}
            skipAnimation
            sx={{
                '& .MuiChartsLegend-label':   { fontSize: large ? 20 : 16 },
                '& .MuiChartsAxis-tickLabel': { fontSize: large ? 20 : 16 },
            }}
            xAxis={[{ label: 'Epoch', scaleType: 'linear', data: epochs }]}
            series={[
                { label: 'Best fitness',    data: best,  color: theme.palette.success.main, showMark: false, valueFormatter: fmt },
                { label: 'Average fitness', data: avg,   color: theme.palette.info.main,    showMark: false, valueFormatter: fmt },
                { label: 'Worst fitness',   data: worst, color: theme.palette.error.main,   showMark: false, valueFormatter: fmt },
            ]}
            margin={{ left: 20, right: 20, top: 20, bottom: 20 }}
            grid={{ vertical: true, horizontal: true }}
        />
    );

    const renderStdChart = (height: number, width?: number, large = false) => (
        <LineChart
            width={width}
            height={height}
            skipAnimation
            sx={{
                '& .MuiChartsLegend-label':   { fontSize: large ? 20 : 16 },
                '& .MuiChartsAxis-tickLabel': { fontSize: large ? 20 : 16 },
            }}
            xAxis={[{ label: 'Epoch', scaleType: 'linear', data: epochs }]}
            series={[{
                label: 'Std Dev (fitness)',
                data: stdDev as number[],
                color: theme.palette.warning.main,
                showMark: false,
                valueFormatter: fmt,
            }]}
            margin={{ left: 20, right: 20, top: 20, bottom: 20 }}
            grid={{ vertical: true, horizontal: true }}
        />
    );

    return (
        <Paper
            elevation={3}
            sx={{ p: 4, mb: 4, backgroundColor: isSuccess ? successBgColor : 'background.paper' }}
        >
            <Typography
                variant="h5"
                component="h2"
                gutterBottom
                color={isSuccess ? 'success.main' : 'text.primary'}
            >
                Optimization Results
            </Typography>

            <Alert severity={isSuccess ? 'success' : 'info'} sx={{ mb: 3 }}>
                {result.message}
            </Alert>

            {result.results && (
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>Best Solution:</Typography>

                    {/* ── Info chips ── */}
                    <Stack direction="row" flexWrap="wrap" gap={1} sx={{ mb: 1.5 }}>
                        <Chip
                            label={`Function: ${result.results.function_name}`}
                            variant="outlined" size="small"
                        />
                        <Chip
                            label={`Domain: [${result.results.domain?.join(', ')}]`}
                            variant="outlined" size="small"
                        />
                        <Chip
                            label={`Strategy: ${STRATEGY_LABELS[result.results.strategy] ?? result.results.strategy}`}
                            variant="outlined" size="small" color="primary"
                        />
                        <Chip
                            label={`wf = ${result.results.wf}`}
                            variant="outlined" size="small" color="primary"
                        />
                        <Chip
                            label={`cr = ${result.results.cr}`}
                            variant="outlined" size="small" color="primary"
                        />
                    </Stack>

                    {/* ── Metrics ── */}
                    <Box
                        sx={{
                            backgroundColor: boxBgColor,
                            p: 2,
                            borderRadius: 1,
                            border: `1px solid ${boxBorderColor}`,
                        }}
                    >
                        <Typography variant="body1">
                            <strong>Execution Time:</strong>{' '}
                            {result.results.execution_time != null
                                ? `${result.results.execution_time.toFixed(4)} s`
                                : 'N/A'}
                        </Typography>
                        <Typography variant="body1">
                            <strong>Best Fitness:</strong>{' '}
                            {fmt(result.results.best_fitness)}
                        </Typography>
                        <Typography variant="body1" sx={{ mt: 1 }}>
                            <strong>Decoded Variables:</strong>
                            <Box
                                component="span"
                                sx={{
                                    fontFamily: 'monospace',
                                    ml: 1,
                                    backgroundColor: codeBgColor,
                                    px: 1,
                                    py: 0.5,
                                    borderRadius: 1,
                                }}
                            >
                                [{result.results.best_decoded_variables.map((v) => v.toFixed(6)).join(', ')}]
                            </Box>
                        </Typography>
                    </Box>
                </Box>
            )}

            {/* ── Fitness convergence chart ── */}
            {history.length > 0 && (
                <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="h6" gutterBottom>
                            Fitness Across Iterations:
                        </Typography>
                        <Button
                            variant="outlined"
                            size="small"
                            startIcon={<ZoomInIcon />}
                            onClick={() => setChartDialogOpen(true)}
                            sx={{
                                mb: 1,
                                color: 'text.primary',
                                borderColor: 'divider',
                                '&:hover': { borderColor: 'text.secondary', backgroundColor: 'action.hover' },
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

            {/* ── Std Dev chart ── */}
            {history.length > 0 && stdDev.some((v) => v !== null) && (
                <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="h6" gutterBottom>
                            Standard Deviation of Fitness per Generation
                        </Typography>
                        <Button
                            variant="outlined"
                            size="small"
                            startIcon={<ZoomInIcon />}
                            onClick={() => setStdDialogOpen(true)}
                            sx={{
                                mb: 1,
                                color: 'text.primary',
                                borderColor: 'divider',
                                '&:hover': { borderColor: 'text.secondary', backgroundColor: 'action.hover' },
                            }}
                        >
                            Open Large View
                        </Button>
                    </Box>
                    <Box sx={{ backgroundColor: boxBgColor, p: 1, borderRadius: 1, border: `1px solid ${boxBorderColor}` }}>
                        {renderStdChart(300, 700)}
                    </Box>
                </Box>
            )}

            {/* Fitness chart dialog */}
            <Dialog
                open={chartDialogOpen}
                onClose={() => setChartDialogOpen(false)}
                maxWidth={false}
                fullWidth
                PaperProps={{ sx: { width: '96vw', maxWidth: '96vw', backgroundColor: theme.palette.background.paper } }}
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

            {/* Std-dev chart dialog */}
            <Dialog
                open={stdDialogOpen}
                onClose={() => setStdDialogOpen(false)}
                maxWidth={false}
                fullWidth
                PaperProps={{ sx: { width: '96vw', maxWidth: '96vw', backgroundColor: theme.palette.background.paper } }}
            >
                <DialogTitle sx={{ pr: 6 }}>
                    Standard Deviation (Large View)
                    <IconButton
                        aria-label="close"
                        onClick={() => setStdDialogOpen(false)}
                        sx={{ position: 'absolute', right: 8, top: 8 }}
                    >
                        <CloseIcon />
                    </IconButton>
                </DialogTitle>
                <DialogContent dividers sx={{ overflowX: 'auto', p: 2 }}>
                    {renderStdChart(760, 1800, true)}
                </DialogContent>
            </Dialog>

            {/* ── Download ── */}
            <Box sx={{ mb: 3, display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={handleDownload}
                    disabled={!result.results}
                    sx={{
                        color: 'text.primary',
                        borderColor: 'divider',
                        '&:hover': { borderColor: 'text.secondary', backgroundColor: 'action.hover' },
                    }}
                >
                    Save Result as JSON
                </Button>
            </Box>

            {/* ── Raw JSON ── */}
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
                            fontSize: '0.875rem',
                        }}
                    >
                        {JSON.stringify(result, null, 2)}
                    </Box>
                </AccordionDetails>
            </Accordion>
        </Paper>
    );
};

export default MealPyResult;
