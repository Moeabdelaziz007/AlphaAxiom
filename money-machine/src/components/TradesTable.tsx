'use client';

import { motion } from 'framer-motion';
import { useAppStore, Trade } from '@/store/useAppStore';

export function TradesTable() {
    const { trades } = useAppStore();

    // Mock data for demo
    const demoTrades: Trade[] = trades.length > 0 ? trades : [
        { id: '1', symbol: 'BTC/USDT', side: 'buy', amount: 0.05, price: 42350, pnl: 120.50, timestamp: Date.now() - 3600000 },
        { id: '2', symbol: 'ETH/USDT', side: 'sell', amount: 1.2, price: 2245, pnl: -45.20, timestamp: Date.now() - 7200000 },
        { id: '3', symbol: 'BTC/USDT', side: 'buy', amount: 0.03, price: 42100, pnl: 85.00, timestamp: Date.now() - 10800000 },
    ];

    const formatTime = (timestamp: number) => {
        return new Date(timestamp).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="glass-card p-6"
        >
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-[var(--text-secondary)]">
                    Recent Trades
                </h3>
                <span className="text-xs text-[var(--text-muted)]">
                    Last 24 hours
                </span>
            </div>

            {demoTrades.length === 0 ? (
                <div className="py-12 text-center text-[var(--text-muted)]">
                    No trades yet
                </div>
            ) : (
                <div className="space-y-3">
                    {demoTrades.map((trade, index) => (
                        <motion.div
                            key={trade.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: index * 0.1 }}
                            className="glass-card-subtle p-4 flex items-center justify-between"
                        >
                            <div className="flex items-center gap-4">
                                <div className={`px-2 py-1 rounded text-xs font-semibold ${trade.side === 'buy'
                                        ? 'bg-[var(--profit-green)]/20 text-[var(--profit-green)]'
                                        : 'bg-[var(--loss-red)]/20 text-[var(--loss-red)]'
                                    }`}>
                                    {trade.side.toUpperCase()}
                                </div>
                                <div>
                                    <div className="font-medium">{trade.symbol}</div>
                                    <div className="text-xs text-[var(--text-muted)]">
                                        {trade.amount} @ ${trade.price.toLocaleString()}
                                    </div>
                                </div>
                            </div>

                            <div className="text-right">
                                <div className={`font-semibold ${trade.pnl >= 0 ? 'text-[var(--profit-green)]' : 'text-[var(--loss-red)]'
                                    }`}>
                                    {trade.pnl >= 0 ? '+' : ''}{trade.pnl.toFixed(2)}
                                </div>
                                <div className="text-xs text-[var(--text-muted)]">
                                    {formatTime(trade.timestamp)}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}
        </motion.div>
    );
}
