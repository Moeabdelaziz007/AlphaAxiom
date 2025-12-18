'use client';

import { motion } from 'framer-motion';
import { useAppStore } from '@/store/useAppStore';

export function StatusWidget() {
    const { connected, tradingActive, skillsLoaded, uptime } = useAppStore();

    const formatUptime = (seconds: number) => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="glass-card p-6"
        >
            <h3 className="text-sm font-medium text-[var(--text-secondary)] mb-4">
                Engine Status
            </h3>

            <div className="space-y-4">
                {/* Connection Status */}
                <div className="flex items-center justify-between">
                    <span className="text-[var(--text-muted)]">Connection</span>
                    <div className="flex items-center gap-2">
                        <span className={connected ? 'text-[var(--profit-green)]' : 'text-[var(--loss-red)]'}>
                            {connected ? 'Connected' : 'Disconnected'}
                        </span>
                        <div className={`status-dot ${connected ? 'active' : 'error'}`} />
                    </div>
                </div>

                {/* Trading Status */}
                <div className="flex items-center justify-between">
                    <span className="text-[var(--text-muted)]">Trading</span>
                    <div className="flex items-center gap-2">
                        <span className={tradingActive ? 'text-[var(--profit-green)]' : 'text-[var(--text-secondary)]'}>
                            {tradingActive ? 'Active' : 'Paused'}
                        </span>
                        <div className={`status-dot ${tradingActive ? 'active' : 'inactive'}`} />
                    </div>
                </div>

                {/* Skills Loaded */}
                <div className="flex items-center justify-between">
                    <span className="text-[var(--text-muted)]">Skills Loaded</span>
                    <span className="text-[var(--accent-blue)]">{skillsLoaded}</span>
                </div>

                {/* Uptime */}
                <div className="flex items-center justify-between">
                    <span className="text-[var(--text-muted)]">Uptime</span>
                    <span className="text-[var(--text-secondary)]">{formatUptime(uptime)}</span>
                </div>
            </div>
        </motion.div>
    );
}
