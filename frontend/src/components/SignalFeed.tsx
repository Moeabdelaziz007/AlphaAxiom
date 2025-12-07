"use client";
import { useState, useEffect } from 'react';
import { Zap, TrendingUp, TrendingDown, AlertCircle, Clock, Sparkles } from 'lucide-react';

interface Signal {
    id: string;
    symbol: string;
    price: number;
    direction: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
    quality: 'S-TIER' | 'A-TIER' | 'B-TIER';
    aexi: number;
    dream: number;
    rsi: number;
    analystBrief: string;
    timestamp: Date;
}

// Demo signals for display
const demoSignals: Signal[] = [
    {
        id: '1',
        symbol: 'BTC/USD',
        price: 68542.00,
        direction: 'BULLISH',
        quality: 'S-TIER',
        aexi: 88.5,
        dream: 74.2,
        rsi: 28.5,
        analystBrief: 'Price extended 4-sigma with chaos metrics indicating structural break. High probability of mean reversion.',
        timestamp: new Date()
    },
    {
        id: '2',
        symbol: 'ETH/USD',
        price: 3842.50,
        direction: 'BULLISH',
        quality: 'A-TIER',
        aexi: 82.1,
        dream: 71.8,
        rsi: 32.4,
        analystBrief: 'Oversold conditions with elevated chaos. Volume dispersion suggests accumulation phase.',
        timestamp: new Date(Date.now() - 1000 * 60 * 15)
    },
    {
        id: '3',
        symbol: 'SPY',
        price: 578.24,
        direction: 'BEARISH',
        quality: 'A-TIER',
        aexi: 84.3,
        dream: 72.5,
        rsi: 74.2,
        analystBrief: 'Overbought with fractal dimension spike. Distribution pattern emerging.',
        timestamp: new Date(Date.now() - 1000 * 60 * 45)
    }
];

function SignalCard({ signal }: { signal: Signal }) {
    const qualityColors = {
        'S-TIER': 'bg-gradient-to-r from-amber-500/10 to-orange-500/10 border-amber-500/20',
        'A-TIER': 'bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border-cyan-500/20',
        'B-TIER': 'bg-white/[0.02] border-white/[0.06]'
    };

    const qualityBadge = {
        'S-TIER': 'bg-gradient-to-r from-amber-500 to-orange-500 text-black',
        'A-TIER': 'bg-gradient-to-r from-cyan-500 to-blue-500 text-black',
        'B-TIER': 'bg-white/10 text-white/60'
    };

    const formatTime = (date: Date) => {
        const now = new Date();
        const diff = Math.floor((now.getTime() - date.getTime()) / 1000 / 60);
        if (diff < 1) return 'Just now';
        if (diff < 60) return `${diff}m ago`;
        return `${Math.floor(diff / 60)}h ago`;
    };

    return (
        <div className={`rounded-xl border p-5 transition-all duration-200 hover:border-white/20 ${qualityColors[signal.quality]}`}>
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${signal.direction === 'BULLISH' ? 'bg-emerald-500/10' : 'bg-rose-500/10'
                        }`}>
                        {signal.direction === 'BULLISH'
                            ? <TrendingUp size={20} className="text-emerald-400" />
                            : <TrendingDown size={20} className="text-rose-400" />
                        }
                    </div>
                    <div>
                        <h3 className="font-semibold text-white text-[15px]">{signal.symbol}</h3>
                        <p className="text-white/40 text-[13px]">${signal.price.toLocaleString()}</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`px-2.5 py-1 rounded-md text-[11px] font-bold ${qualityBadge[signal.quality]}`}>
                        {signal.quality}
                    </span>
                </div>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="bg-white/[0.03] rounded-lg p-3">
                    <p className="text-[11px] text-white/40 mb-1">AEXI</p>
                    <p className="text-[15px] font-semibold text-white">{signal.aexi.toFixed(1)}</p>
                </div>
                <div className="bg-white/[0.03] rounded-lg p-3">
                    <p className="text-[11px] text-white/40 mb-1">DREAM</p>
                    <p className="text-[15px] font-semibold text-white">{signal.dream.toFixed(1)}</p>
                </div>
                <div className="bg-white/[0.03] rounded-lg p-3">
                    <p className="text-[11px] text-white/40 mb-1">RSI</p>
                    <p className={`text-[15px] font-semibold ${signal.rsi < 30 ? 'text-emerald-400' : signal.rsi > 70 ? 'text-rose-400' : 'text-white'
                        }`}>{signal.rsi.toFixed(1)}</p>
                </div>
            </div>

            {/* Analyst Brief */}
            <div className="flex items-start gap-2.5 mb-3">
                <Sparkles size={14} className="text-purple-400 mt-0.5 flex-shrink-0" />
                <p className="text-[13px] text-white/60 leading-relaxed">
                    {signal.analystBrief}
                </p>
            </div>

            {/* Footer */}
            <div className="flex items-center gap-1.5 text-white/30 text-[12px]">
                <Clock size={12} />
                <span>{formatTime(signal.timestamp)}</span>
            </div>
        </div>
    );
}

export default function SignalFeed() {
    const [signals, setSignals] = useState<Signal[]>(demoSignals);

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Zap size={18} className="text-[#00F0FF]" />
                    <h2 className="text-[15px] font-semibold text-white">Live Signals</h2>
                    <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 text-[11px] font-medium rounded-full">
                        {signals.length} Active
                    </span>
                </div>
                <button className="text-[13px] text-white/40 hover:text-white/60 transition-colors">
                    View all →
                </button>
            </div>

            {/* Signal Cards */}
            <div className="space-y-3">
                {signals.map(signal => (
                    <SignalCard key={signal.id} signal={signal} />
                ))}
            </div>

            {/* Empty State */}
            {signals.length === 0 && (
                <div className="text-center py-16">
                    <AlertCircle size={40} className="text-white/20 mx-auto mb-3" />
                    <p className="text-white/40 text-[14px]">No active signals</p>
                    <p className="text-white/20 text-[13px]">Signals appear when AEXI &gt; 80 and Dream &gt; 70</p>
                </div>
            )}
        </div>
    );
}
