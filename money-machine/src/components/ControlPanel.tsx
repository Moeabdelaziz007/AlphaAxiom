'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useAppStore } from '@/store/useAppStore';
import { startTrading, stopTrading, setAlwaysOnTop, setIgnoreMouseEvents } from '@/lib/tauri';

export function ControlPanel() {
    const { tradingActive, setTradingActive, connected } = useAppStore();
    const [loading, setLoading] = useState(false);
    const [isAlwaysOnTop, setIsAlwaysOnTop] = useState(true);
    const [isGhostMode, setIsGhostMode] = useState(false);

    const handleToggleTrading = async () => {
        if (!connected) return;

        setLoading(true);
        try {
            if (tradingActive) {
                const success = await stopTrading();
                if (success) setTradingActive(false);
            } else {
                const success = await startTrading();
                if (success) setTradingActive(true);
            }
        } catch (error) {
            console.error('Failed to toggle trading:', error);
        } finally {
            setLoading(false);
        }
    };

    const toggleAlwaysOnTop = async () => {
        const newState = !isAlwaysOnTop;
        await setAlwaysOnTop(newState);
        setIsAlwaysOnTop(newState);
    };

    const toggleGhostMode = async () => {
        const newState = !isGhostMode;
        await setIgnoreMouseEvents(newState);
        setIsGhostMode(newState);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="glass-card p-6"
        >
            <h3 className="text-sm font-medium text-[var(--text-secondary)] mb-4 flex justify-between items-center">
                <span>Control Panel</span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full ${connected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                    {connected ? 'CONNECTED' : 'OFFLINE'}
                </span>
            </h3>

            <div className="space-y-4">
                {/* Main Trading Button */}
                <button
                    onClick={handleToggleTrading}
                    disabled={!connected || loading}
                    className={`w-full py-4 px-6 rounded-xl font-semibold text-lg transition-all duration-300 ${tradingActive
                        ? 'btn-danger'
                        : 'btn-primary'
                        } ${(!connected || loading) && 'opacity-50 cursor-not-allowed'}`}
                >
                    {loading ? (
                        <span className="flex items-center justify-center gap-2">
                            Processing...
                        </span>
                    ) : tradingActive ? (
                        '⏸ Stop Trading'
                    ) : (
                        '▶ Start Trading'
                    )}
                </button>

                {/* Window Controls (Wispr Flow) */}
                <div className="grid grid-cols-2 gap-3">
                    <button
                        onClick={toggleAlwaysOnTop}
                        className={`glass-card-subtle py-2 px-3 text-xs font-medium transition-colors flex items-center justify-center gap-2 ${isAlwaysOnTop ? 'text-[var(--profit-green)] bg-[var(--profit-green)]/10' : 'text-[var(--text-secondary)]'
                            }`}
                    >
                        📌 {isAlwaysOnTop ? 'On Top' : 'Floating'}
                    </button>
                    <button
                        onClick={toggleGhostMode}
                        title="Click-Through Mode (Exit via Tray)"
                        className={`glass-card-subtle py-2 px-3 text-xs font-medium transition-colors flex items-center justify-center gap-2 ${isGhostMode ? 'text-[var(--accent-blue)] bg-[var(--accent-blue)]/10' : 'text-[var(--text-secondary)]'
                            }`}
                    >
                        👻 {isGhostMode ? 'Ghost' : 'Interactive'}
                    </button>
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-2 gap-3">
                    <button disabled={!connected} className="glass-card-subtle py-3 px-4 text-sm hover:bg-white/5 disabled:opacity-50 text-[var(--text-secondary)]">
                        📊 History
                    </button>
                    <button disabled={!connected} className="glass-card-subtle py-3 px-4 text-sm hover:bg-white/5 disabled:opacity-50 text-[var(--text-secondary)]">
                        ⚙️ Config
                    </button>
                </div>
            </div>
        </motion.div>
    );
}
