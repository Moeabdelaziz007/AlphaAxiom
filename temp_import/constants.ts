// Color Palette
export const COLORS = {
  background: '#0A0A1A',
  core: '#00FFFF', // Cyan
  shadow: '#FF0055', // Crimson
  textPrimary: '#F1F5F9', // Gray-100
  textSecondary: '#94A3B8', // Gray-400
  grid: '#1e293b',
  success: '#10B981',
  warning: '#F59E0B',
};

// Types
export interface FitnessDataPoint {
  generation: number;
  fitness: number;
  avgFitness: number;
}

export interface CircuitBreaker {
  id: string;
  name: string;
  status: 'CLOSED' | 'OPEN' | 'HALF-OPEN';
  latency: string;
  lastReset: string;
  totalCycles: number;
  avgLatency: string;
}

// Mock Data
export const MOCK_FITNESS_DATA: FitnessDataPoint[] = Array.from({ length: 20 }, (_, i) => ({
  generation: i * 5,
  fitness: 60 + Math.random() * 30 + (i * 1.5), // Upward trend with noise
  avgFitness: 50 + (i * 1.2),
}));

export const MOCK_CIRCUIT_BREAKERS: CircuitBreaker[] = [
  { 
    id: 'cb1', 
    name: 'EXCHANGE_API_V1', 
    status: 'CLOSED', 
    latency: '45ms',
    lastReset: '2h 15m ago',
    totalCycles: 142,
    avgLatency: '42ms'
  },
  { 
    id: 'cb2', 
    name: 'RISK_ENGINE_CORE', 
    status: 'CLOSED', 
    latency: '12ms',
    lastReset: '14d ago',
    totalCycles: 12,
    avgLatency: '10ms'
  },
  { 
    id: 'cb3', 
    name: 'SENTIMENT_STREAM', 
    status: 'OPEN', 
    latency: 'TIMEOUT',
    lastReset: '1m 30s ago',
    totalCycles: 853,
    avgLatency: '85ms'
  },
];

export const CORE_MONOLOGUE = [
  "Analyzing liquidity depth in order book...",
  "Bullish divergence detected on RSI (14).",
  "Momentum vectors aligning with macro trend.",
  "Probability of upside breakout: 78.4%.",
  "Proposal: Increase position size by 15%."
];

export const SHADOW_MONOLOGUE = [
  "Wait. Volatility profile expanding rapidly.",
  "Detected institutional sell wall at 98.5k.",
  "Historical drawdown correlation suggests trap.",
  "Regret analysis indicates potential 12% loss.",
  "Counter-Proposal: Hedge with OTM Puts immediately."
];