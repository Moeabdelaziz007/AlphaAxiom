'use client';

import React from 'react';
import { Activity, Bell, Settings, User, Zap } from 'lucide-react';

export default function TopBar() {
    return (
        <div className="glass-panel-dark border-b border-white/5 px-6 py-3">
            <div className="flex items-center justify-between">
                {/* Logo & Brand */}
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <Zap className="w-8 h-8 text-neon-cyan" />
                        <span className="absolute -top-1 -right-1 w-2 h-2 bg-neon-green rounded-full animate-ping" />
                    </div>
                    <div>
                        <h1 className="text-lg font-bold text-white">
                            <span className="text-neon-cyan glow-cyan">QUANTUM</span> TRADING
                        </h1>
                        <p className="text-xs text-gray-500">Powered by SENTINEL AI</p>
                    </div>
                </div>

                {/* Center: Market Status */}
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2 px-4 py-1.5 glass-panel rounded-full">
                        <Activity className="w-4 h-4 text-neon-green" />
                        <span className="text-xs text-gray-300">Market Open</span>
                    </div>
                    <div className="text-right">
                        <p className="text-xs text-gray-500">Portfolio Value</p>
                        <p className="text-sm font-bold text-neon-green font-mono glow-green">$124,580.45</p>
                    </div>
                    <div className="text-right">
                        <p className="text-xs text-gray-500">Today&apos;s P&amp;L</p>
                        <p className="text-sm font-bold text-neon-green font-mono">+$1,240.80</p>
                    </div>
                </div>

                {/* Right: Actions */}
                <div className="flex items-center gap-3">
                    <button className="p-2 glass-panel rounded-lg hover:bg-white/5 transition-colors relative">
                        <Bell className="w-5 h-5 text-gray-400" />
                        <span className="absolute top-1 right-1 w-2 h-2 bg-neon-red rounded-full" />
                    </button>
                    <button className="p-2 glass-panel rounded-lg hover:bg-white/5 transition-colors">
                        <Settings className="w-5 h-5 text-gray-400" />
                    </button>
                    <button className="flex items-center gap-2 px-3 py-2 glass-panel rounded-lg hover:bg-white/5 transition-colors">
                        <User className="w-5 h-5 text-neon-cyan" />
                        <span className="text-sm text-gray-300">Demo Account</span>
                    </button>
                </div>
            </div>
        </div>
    );
}
