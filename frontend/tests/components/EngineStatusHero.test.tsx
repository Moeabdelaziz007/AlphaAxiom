import React from 'react';
import { render, screen } from '@testing-library/react';
import { EngineStatusHero } from '../../components/engine-status-hero';
import '@testing-library/jest-dom';

// Mock Lucide icons
jest.mock('lucide-react', () => ({
  Activity: () => <div data-testid="icon-activity" />,
  Zap: () => <div data-testid="icon-zap" />,
  TrendingUp: () => <div data-testid="icon-trending-up" />,
  Brain: () => <div data-testid="icon-brain" />,
}));

// Mock Framer Motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, className, style, ...props }: any) => (
      <div className={className} style={style} {...props}>{children}</div>
    ),
  },
}));

describe('EngineStatusHero Component', () => {
  it('renders correctly with default props', () => {
    render(<EngineStatusHero engineState="stopped" wallet={10000} generation={1} />);
    expect(screen.getByText('AlphaAxiom')).toBeInTheDocument();
    expect(screen.getByText('OFFLINE')).toBeInTheDocument();
    expect(screen.getByText('$10,000')).toBeInTheDocument();
    expect(screen.getByText('Gen 1')).toBeInTheDocument();
  });

  it('displays RUNNING state correctly (Green)', () => {
    render(<EngineStatusHero engineState="running" wallet={5000} generation={5} />);

    const statusLabel = screen.getByText('LIVE');
    expect(statusLabel).toBeInTheDocument();

    // Check color - we can check the inline style of the label or the Zap icon container
    // The component uses stateConfig.running.color = "var(--color-neon-green)" (or similar)
    // and bg = "rgba(57, 255, 20, 0.1)"

    expect(statusLabel).toHaveStyle({
      color: 'var(--color-neon-green)',
      backgroundColor: 'rgba(57, 255, 20, 0.1)'
    });
  });

  it('displays STOPPED state correctly (Red)', () => {
    render(<EngineStatusHero engineState="stopped" wallet={0} generation={0} />);

    const statusLabel = screen.getByText('OFFLINE');
    expect(statusLabel).toBeInTheDocument();

    // stopped.color = "#FF3366"
    expect(statusLabel).toHaveStyle({
      color: '#FF3366'
    });
  });

  it('displays CONNECTING state correctly (Orange)', () => {
    render(<EngineStatusHero engineState="connecting" wallet={0} generation={0} />);

    const statusLabel = screen.getByText('CONNECTING');
    expect(statusLabel).toBeInTheDocument();

    // connecting.color = "#F59E0B"
    expect(statusLabel).toHaveStyle({
      color: '#F59E0B'
    });
  });

  it('displays wallet and generation info', () => {
    render(<EngineStatusHero engineState="running" wallet={12345} generation={42} tradestoday={5} maxTrades={10} />);

    expect(screen.getByText('$12,345')).toBeInTheDocument();
    expect(screen.getByText('Gen 42')).toBeInTheDocument();
    expect(screen.getByText('5/10')).toBeInTheDocument();
  });
});
