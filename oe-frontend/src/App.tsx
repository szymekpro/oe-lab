import { useState, useMemo } from 'react';
import {
  Container, Typography, Box, ThemeProvider, createTheme, CssBaseline,
  IconButton, Tabs, Tab, Paper
} from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import ScienceIcon from '@mui/icons-material/Science';
import PsychologyAltIcon from '@mui/icons-material/PsychologyAlt';
import BiotechIcon from '@mui/icons-material/Biotech';
import HubIcon from '@mui/icons-material/Hub';
import OptimizationForm from './components/OptimizationForm';
import OptimizationResult from './components/OptimizationResult';
import PyGADForm from './components/PyGADForm';
import PyGADResult from './components/PyGADResult';
import MealPyForm from './components/MealPyForm';
import MealPyResult from './components/MealPyResult';
import alienImg from './alien.png';
import { AlgorithmParams, OptimizationResult as OptResultType, PyGADParams, PyGADResult as PyGADResultType, MealPyParams, MealPyResult as MealPyResultType } from './types';
import './App.css';

function App() {
  const [appMode, setAppMode] = useState<'light' | 'dark' | 'dna'>('light');
  const [activeTab, setActiveTab] = useState(0);

  // ── Custom GA state (P1/P2)
  const [result, setResult] = useState<OptResultType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── PyGAD state (P3)
  const [pygadResult, setPygadResult] = useState<PyGADResultType | null>(null);
  const [pygadLoading, setPygadLoading] = useState(false);
  const [pygadError, setPygadError] = useState<string | null>(null);

  // ── MealPy state (P4)
  const [mealPyResult, setMealPyResult] = useState<MealPyResultType | null>(null);
  const [mealPyLoading, setMealPyLoading] = useState(false);
  const [mealPyError, setMealPyError] = useState<string | null>(null);

  const theme = useMemo(() => {
    const isDna = appMode === 'dna';
    const isLight = appMode === 'light';

    return createTheme({
      palette: {
        mode: isLight ? 'light' : 'dark',
        primary: {
          main: isDna ? '#00e676' : '#1976d2',
        },
        secondary: {
          main: isDna ? '#d500f9' : '#9c27b0',
        },
        background: {
          default: isLight ? '#f5f5f5' : isDna ? '#050a14' : '#121212',
          paper: isLight ? '#ffffff' : isDna ? 'rgba(12, 18, 36, 0.95)' : '#1e1e1e',
        },
        ...(isDna && {
          text: {
            primary: '#e0f2f1',
            secondary: '#b2dfdb',
          }
        })
      },
      shape: {
        borderRadius: 16,
      },
      components: {
        MuiPaper: {
          styleOverrides: {
            root: {
              borderRadius: 16,
              ...(isDna && {
                border: '1px solid rgba(0, 230, 118, 0.2)',
                boxShadow: '0 8px 32px 0 rgba(0, 230, 118, 0.1)',
              }),
            },
          },
        },
      },
      typography: {
        fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      }
    });
  }, [appMode]);

  const toggleColorMode = () => {
    setAppMode((prev) => prev === 'light' ? 'dark' : prev === 'dark' ? 'dna' : 'light');
  };

  const getModeIcon = () => {
    if (appMode === 'light') return <Brightness4Icon />;
    if (appMode === 'dark') return <ScienceIcon />;
    return <Brightness7Icon />;
  };

  const dnaBgStyle = appMode === 'dna' ? {
    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Cpath d='M 0 60 C 30 10, 30 10, 60 60 C 90 110, 90 110, 120 60' fill='none' stroke='%2300e676' stroke-width='3' stroke-opacity='0.15'/%3E%3Cpath d='M 0 60 C 30 110, 30 110, 60 60 C 90 10, 90 10, 120 60' fill='none' stroke='%23d500f9' stroke-width='3' stroke-opacity='0.15'/%3E%3Cline x1='15' y1='34' x2='15' y2='86' stroke='%23ffffff' stroke-opacity='0.05' stroke-width='2'/%3E%3Cline x1='30' y1='10' x2='30' y2='110' stroke='%23ffffff' stroke-opacity='0.05' stroke-width='2'/%3E%3Cline x1='45' y1='34' x2='45' y2='86' stroke='%23ffffff' stroke-opacity='0.05' stroke-width='2'/%3E%3Cline x1='75' y1='34' x2='75' y2='86' stroke='%23ffffff' stroke-opacity='0.05' stroke-width='2'/%3E%3Cline x1='90' y1='10' x2='90' y2='110' stroke='%23ffffff' stroke-opacity='0.05' stroke-width='2'/%3E%3Cline x1='105' y1='34' x2='105' y2='86' stroke='%23ffffff' stroke-opacity='0.05' stroke-width='2'/%3E%3C/svg%3E")`,
    backgroundSize: '150px 150px',
  } : {};

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleSubmit = async (formData: AlgorithmParams) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch('http://localhost:5000/api/optimizations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
      setResult(await response.json());
    } catch (err: any) {
      setError(err.message || 'An error occurred while connecting to the server.');
    } finally {
      setLoading(false);
    }
  };

  const handleMealPySubmit = async (formData: MealPyParams) => {
    setMealPyLoading(true);
    setMealPyError(null);
    setMealPyResult(null);
    try {
      const response = await fetch('http://localhost:5000/api/mealpy/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
      setMealPyResult(await response.json());
    } catch (err: any) {
      setMealPyError(err.message || 'An error occurred while connecting to the server.');
    } finally {
      setMealPyLoading(false);
    }
  };

  const handlePyGADSubmit = async (formData: PyGADParams) => {
    setPygadLoading(true);
    setPygadError(null);
    setPygadResult(null);
    try {
      const response = await fetch('http://localhost:5000/api/pygad/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
      setPygadResult(await response.json());
    } catch (err: any) {
      setPygadError(err.message || 'An error occurred while connecting to the server.');
    } finally {
      setPygadLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', py: 4, ...dnaBgStyle, transition: 'background-color 0.3s' }}>
        <Container maxWidth="md">
          {/* ── Top bar ── */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
            <IconButton
              sx={{ ml: 1 }}
              onClick={toggleColorMode}
              color="inherit"
              title={`Toggle Theme (Current: ${appMode})`}
            >
              {getModeIcon()}
            </IconButton>
          </Box>

          <Typography variant="h3" component="h1" align="center" gutterBottom color="primary.main" fontWeight="bold">
            Optimization Panel
          </Typography>
          <Typography variant="subtitle1" align="center" color="text.secondary" paragraph sx={{ mb: 4 }}>
            Configure and run Genetic Algorithm optimization
          </Typography>

          {appMode === 'dna' && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
              <img src={alienImg} alt="Alien" style={{ maxHeight: '200px', borderRadius: '16px' }} />
            </Box>
          )}

          {/* ── Tab navigation ── */}
          <Paper elevation={1} sx={{ mb: 3 }}>
            <Tabs
              value={activeTab}
              onChange={(_, v) => setActiveTab(v)}
              variant="fullWidth"
              textColor="primary"
              indicatorColor="primary"
            >
              <Tab
                id="tab-custom-ga"
                aria-controls="tabpanel-custom-ga"
                icon={<BiotechIcon />}
                iconPosition="start"
                label="Custom GA (P1 / P2)"
              />
              <Tab
                id="tab-pygad"
                aria-controls="tabpanel-pygad"
                icon={<PsychologyAltIcon />}
                iconPosition="start"
                label="PyGAD (P3)"
              />
              <Tab
                id="tab-mealpy"
                aria-controls="tabpanel-mealpy"
                icon={<HubIcon />}
                iconPosition="start"
                label="MealPy DE (P4)"
              />
            </Tabs>
          </Paper>

          {/* ── Custom GA tab ── */}
          <Box
            role="tabpanel"
            id="tabpanel-custom-ga"
            aria-labelledby="tab-custom-ga"
            hidden={activeTab !== 0}
          >
            {activeTab === 0 && (
              <>
                <OptimizationForm loading={loading} onSubmit={handleSubmit} />
                <OptimizationResult result={result} error={error} />
              </>
            )}
          </Box>

          {/* ── PyGAD tab ── */}
          <Box
            role="tabpanel"
            id="tabpanel-pygad"
            aria-labelledby="tab-pygad"
            hidden={activeTab !== 1}
          >
            {activeTab === 1 && (
              <>
                <PyGADForm loading={pygadLoading} onSubmit={handlePyGADSubmit} />
                <PyGADResult result={pygadResult} error={pygadError} />
              </>
            )}
          </Box>

          {/* ── MealPy DE tab ── */}
          <Box
            role="tabpanel"
            id="tabpanel-mealpy"
            aria-labelledby="tab-mealpy"
            hidden={activeTab !== 2}
          >
            {activeTab === 2 && (
              <>
                <MealPyForm loading={mealPyLoading} onSubmit={handleMealPySubmit} />
                <MealPyResult result={mealPyResult} error={mealPyError} />
              </>
            )}
          </Box>

        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
