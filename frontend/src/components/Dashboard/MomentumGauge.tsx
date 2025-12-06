'use client';

import React from 'react';
import { Gauge, TrendingUp, TrendingDown, Zap } from 'lucide-react';
import { useMarketData } from '@/hooks/useMarketData';

interface MomentumGaugeProps {
    symbol: string;
}

export default function MomentumGauge({ symbol }: MomentumGaugeProps) {
    const { data, trend } = useMarketData(symbol);

    // Calculate momentum from change_percent (scale to 0-100 where 50 is neutral)
    const rawMomentum = data?.change_percent ? 50 + (data.change_percent * 2) : 50;

    // Default to 50 if momentum is undefined
    const momentum = rawMomentum ?? 50;

    // Calculate visual percentage (clamped 0-100)
    const gaugePercent = Math.min(100, Math.max(0, momentum));

    // Determine signal based on momentum
    const getSignal = () => {
        if (momentum >= 70) return { text: 'STRONG BUY', color: 'text-neon-green', bg: 'bg-neon-green' };
        if (momentum >= 55) return { text: 'BUY', color: 'text-neon-green', bg: 'bg-neon-green' };
        if (momentum >= 45) return { text: 'NEUTRAL', color: 'text-gray-400', bg: 'bg-gray-500' };
        if (momentum >= 30) return { text: 'SELL', color: 'text-neon-red', bg: 'bg-neon-red' };
        return { text: 'STRONG SELL', color: 'text-neon-red', bg: 'bg-neon-red' };
    };

    const signal = getSignal();

    // Gradient based on momentum
    const getGradient = () => {
        if (momentum >= 55) return 'from-neon-green via-neon-cyan to-neon-green';
        if (momentum >= 45) return 'from-gray-500 via-gray-400 to-gray-500';
        return 'from-neon-red via-orange-500 to-neon-red';
    };

    return (
        <div className="glass-panel neon-border rounded-xl p-5 fade-in">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Gauge className="w-5 h-5 text-neon-cyan" />
                    <span className="text-sm font-medium text-gray-300">MOMENTUM GAUGE</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">{symbol}</span>
                    {trend === 'UP' ? (
                        <TrendingUp className="w-4 h-4 text-neon-green" />
                    ) : (
                        <TrendingDown className="w-4 h-4 text-neon-red" />
                    )}
                </div>
            </div>

            {/* Main Gauge */}
            <div className="relative">
                {/* Background Track */}
                <div className="h-4 bg-terminal-gray rounded-full overflow-hidden">
                    {/* Filled Progress */}
                    <div
                        className={`h-full bg-gradient-to-r ${getGradient()} rounded-full transition-all duration-700 ease-out relative`}
                        style={{ width: `${gaugePercent}%` }}
                    >
                        {/* Glow Effect */}
                        <div className="absolute inset-0 animate-pulse opacity-50 bg-white/20 rounded-full" />
                    </div>
                </div>

                {/* Scale Markers */}
                <div className="flex justify-between text-xs text-gray-600 mt-1 px-1">
                    <span>0</span>
                    <span>25</span>
                    <span>50</span>
                    <span>75</span>
                    <span>100</span>
                </div>
            </div>

            {/* Signal Display */}
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-white/5">
                <div className="flex items-center gap-3">
                    <Zap className={`w-5 h-5 ${signal.color}`} />
                    <div>
                        <p className="text-xs text-gray-500">SIGNAL</p>
                        <p className={`text-lg font-bold ${signal.color}`}>{signal.text}</p>
                    </div>
                </div>
                <div className="text-right">
                    <p className="text-xs text-gray-500">MOMENTUM</p>
                    <p className={`text-2xl font-bold font-mono ${signal.color}`}>
                        {momentum.toFixed(1)}%
                    </p>
                </div>
            </div>
        </div>
    );
}
