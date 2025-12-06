'use client';

import React, { useEffect, useState, useRef } from 'react';
import { Bot, Terminal, AlertCircle, CheckCircle, Zap, Clock } from 'lucide-react';
import { tradingApi } from '@/lib/api';

interface AILog {
    id: string;
    timestamp: string;
    type: 'info' | 'success' | 'warning' | 'error' | 'signal';
    message: string;
}

export default function SentinelAI() {
    const [logs, setLogs] = useState<AILog[]>([]);
    const [isLive, setIsLive] = useState(true);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Initial fetch
        fetchLogs();

        // Poll for new logs every 5 seconds
        const interval = setInterval(fetchLogs, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchLogs = async () => {
        try {
            const data = await tradingApi.getAILogs();
            if (data?.logs) {
                setLogs(data.logs);
                setIsLive(true);
            }
        } catch (error) {
            // Use demo logs if API fails
            setLogs(getDemoLogs());
            setIsLive(false);
        }
    };

    const getDemoLogs = (): AILog[] => [
        { id: '1', timestamp: new Date().toISOString(), type: 'info', message: 'Initializing SENTINEL AI v2.4...' },
        { id: '2', timestamp: new Date().toISOString(), type: 'success', message: 'Market data stream connected' },
        { id: '3', timestamp: new Date().toISOString(), type: 'signal', message: 'BTC/USDT: Momentum detected at 72.3%' },
        { id: '4', timestamp: new Date().toISOString(), type: 'warning', message: 'Volatility spike on AAPL' },
        { id: '5', timestamp: new Date().toISOString(), type: 'info', message: 'Scanning 15 assets for opportunities...' },
    ];

    // Auto-scroll to bottom on new logs
    useEffect(() => {
        if (containerRef.current) {
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
    }, [logs]);

    const getLogStyle = (type: AILog['type']) => {
        switch (type) {
            case 'success':
                return { icon: CheckCircle, color: 'text-neon-green', bg: 'bg-neon-green/10' };
            case 'warning':
                return { icon: AlertCircle, color: 'text-neon-gold', bg: 'bg-neon-gold/10' };
            case 'error':
                return { icon: AlertCircle, color: 'text-neon-red', bg: 'bg-neon-red/10' };
            case 'signal':
                return { icon: Zap, color: 'text-neon-cyan', bg: 'bg-neon-cyan/10' };
            default:
                return { icon: Terminal, color: 'text-gray-400', bg: 'bg-gray-500/10' };
        }
    };

    const formatTime = (timestamp: string) => {
        return new Date(timestamp).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        });
    };

    return (
        <div className="glass-panel neon-border rounded-xl h-full flex flex-col fade-in overflow-hidden">
            {/* Header */}
            <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Bot className="w-5 h-5 text-neon-cyan" />
                    <span className="text-sm font-bold text-neon-cyan glow-cyan">SENTINEL AI</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${isLive ? 'bg-neon-green animate-pulse' : 'bg-gray-500'}`} />
                    <span className="text-xs text-gray-500">{isLive ? 'LIVE' : 'DEMO'}</span>
                </div>
            </div>

            {/* Logs Container */}
            <div
                ref={containerRef}
                className="flex-1 overflow-y-auto p-3 space-y-2 font-mono text-xs"
            >
                {logs.map((log, index) => {
                    const style = getLogStyle(log.type);
                    const Icon = style.icon;
                    return (
                        <div
                            key={log.id || index}
                            className={`flex items-start gap-2 p-2 rounded ${style.bg} fade-in`}
                            style={{ animationDelay: `${index * 50}ms` }}
                        >
                            <Icon className={`w-4 h-4 ${style.color} mt-0.5 flex-shrink-0`} />
                            <div className="flex-1 min-w-0">
                                <p className={`${style.color}`}>{log.message}</p>
                            </div>
                            <span className="text-gray-600 flex-shrink-0 flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {formatTime(log.timestamp)}
                            </span>
                        </div>
                    );
                })}
            </div>

            {/* Footer */}
            <div className="px-4 py-2 border-t border-white/5 flex items-center justify-between text-xs text-gray-600">
                <span>v2.4.0-quantum</span>
                <span>{logs.length} events</span>
            </div>
        </div>
    );
}
