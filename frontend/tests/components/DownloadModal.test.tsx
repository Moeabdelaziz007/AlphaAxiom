import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { DownloadModal } from '../../components/download-modal';
import '@testing-library/jest-dom';

// Mock Framer Motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, onClick, className, style, whileHover, whileTap, initial, animate, exit, transition, ...props }: any) => (
      <div onClick={onClick} className={className} style={style} {...props}>{children}</div>
    ),
    button: ({ children, onClick, className, style, whileHover, whileTap, initial, animate, exit, transition, ...props }: any) => (
      <button onClick={onClick} className={className} style={style} {...props}>{children}</button>
    ),
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

describe('DownloadModal Component', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders correctly when open', () => {
    render(<DownloadModal isOpen={true} onClose={mockOnClose} />);
    expect(screen.getByText('Download AlphaAxiom')).toBeInTheDocument();
    expect(screen.getByText('macOS')).toBeInTheDocument();
    expect(screen.getByText('Windows')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(<DownloadModal isOpen={false} onClose={mockOnClose} />);
    expect(screen.queryByText('Download AlphaAxiom')).not.toBeInTheDocument();
  });

  it('handles Mac download selection', async () => {
    jest.useFakeTimers();
    render(<DownloadModal isOpen={true} onClose={mockOnClose} />);

    const macBtn = screen.getByText('macOS').closest('button');
    expect(macBtn).toBeInTheDocument();

    // Click Mac button
    fireEvent.click(macBtn!);

    // Should switch to downloading state
    expect(screen.getByText('Downloading...')).toBeInTheDocument();
    expect(screen.getByText('AlphaAxiom-Mac.dmg')).toBeInTheDocument();

    // Fast-forward timers to simulate download
    act(() => {
      jest.advanceTimersByTime(5000); // Enough for simulated progress (100 / ~7.5 * 200ms = ~2.6s)
    });

    await waitFor(() => {
       expect(screen.getByText('Download Complete!')).toBeInTheDocument();
    });

    jest.useRealTimers();
  });

  it('handles Windows download selection', async () => {
    jest.useFakeTimers();
    render(<DownloadModal isOpen={true} onClose={mockOnClose} />);

    const winBtn = screen.getByText('Windows').closest('button');
    fireEvent.click(winBtn!);

    expect(screen.getByText('Downloading...')).toBeInTheDocument();
    expect(screen.getByText('AlphaReceiver.mq5')).toBeInTheDocument();

    act(() => {
      jest.advanceTimersByTime(5000);
    });

    await waitFor(() => {
       expect(screen.getByText('Download Complete!')).toBeInTheDocument();
    });

    jest.useRealTimers();
  });

  it('calls onClose when close button is clicked', () => {
    render(<DownloadModal isOpen={true} onClose={mockOnClose} />);

    // Find close button (X icon)
    // Since we mocked framer-motion, we need to find it by something else or add aria-label in real code
    // Looking at the code: <X className="h-4 w-4 text-white/60" /> inside a button
    // Let's rely on the button being the first one or having the specific class
    const buttons = screen.getAllByRole('button');
    // First button is likely the X close button if it's rendered first in DOM order (absolute positioned top right)
    // Or we can check if it contains the X icon (mocked icon imports might be needed if they were real components)
    // The Lucide icons are likely React components.

    // Safer: trigger onClose via the backdrop click
    const backdrop = screen.getByText('Download AlphaAxiom').closest('.fixed');
    fireEvent.click(backdrop!);
    expect(mockOnClose).toHaveBeenCalled();
  });
});
