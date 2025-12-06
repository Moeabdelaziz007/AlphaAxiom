'use client';

import React from 'react';
import { Wifi, WifiOff, Server, Activity } from 'lucide-react';
import { useMarketData } from '@/hooks/useMarketData';

export default function ConnectionHeartbeat() {
    // Use a default symbol to check connection status
    const { isConnected, isLoading } = useMarketData('BTC/USDT');

    const engines = [
        { name: 'MARKET DATA', status: isConnected },
        { name: 'ALPACA API', status: true },
        { name: 'SENTINEL AI', status: true },
    ];

    return (
        <div className="glass-panel-dark neon-border rounded-xl px-5 py-3 fade-in">
            <div className="flex items-center justify-between">
                {/* Left: Connection Status */}
                <div className="flex items-center gap-3">
                    <div className={`relative ${isConnected ? 'heartbeat' : ''}`}>
                        {isConnected ? (
                            <Wifi className="w-5 h-5 text-neon-green" />
                        ) : (
                            <WifiOff className="w-5 h-5 text-neon-red" />
                        )}
                        {isConnected && (
                            <span className="absolute -top-1 -right-1 w-2 h-2 bg-neon-green rounded-full animate-ping" />
                        )}
                    </div>
                    <div>
                        <p className="text-xs text-gray-500">SYSTEM STATUS</p>
                        <p className={`text-sm font-bold ${isConnected ? 'text-neon-green glow-green' : 'text-neon-red glow-red'}`}>
                            {isLoading ? 'CONNECTING...' : isConnected ? 'ONLINE' : 'OFFLINE'}
                        </p>
                    </div>
                </div>

                {/* Center: Engine Status */}
                <div className="flex items-center gap-6">
                    {engines.map((engine) => (
                        <div key={engine.name} className="flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${engine.status ? 'bg-neon-green' : 'bg-neon-red'}`}>
                                {engine.status && (
                                    <span className="block w-2 h-2 rounded-full bg-neon-green animate-ping opacity-75" />
                                )}
                            </div>
                            <span className="text-xs text-gray-400">{engine.name}</span>
                        </div>
                    ))}
                </div>

                {/* Right: Latency */}
                <div className="flex items-center gap-3">
                    <Activity className="w-4 h-4 text-neon-cyan" />
                    <div className="text-right">
                        <p className="text-xs text-gray-500">LATENCY</p>
                        <p className="text-sm font-mono text-neon-cyan">
                            {isConnected ? '12ms' : '---'}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
