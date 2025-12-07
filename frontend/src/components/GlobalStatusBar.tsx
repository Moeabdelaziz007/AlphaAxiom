"use client";
import React, { useState, useEffect } from 'react';
import { Wifi, Radio, ShieldCheck, Cpu, Search } from 'lucide-react';

interface GlobalStatusBarProps {
    onCommandPaletteOpen?: () => void;
}

export default function GlobalStatusBar({ onCommandPaletteOpen }: GlobalStatusBarProps) {
    const [time, setTime] = useState("");

    useEffect(() => {
        const timer = setInterval(() => {
            const now = new Date();
            setTime(now.toISOString().split('T')[1].split('.')[0] + " UTC");
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="h-12 border-b border-white/10 bg-obsidian/50 backdrop-blur-md flex items-center justify-between px-6 text-xs font-mono select-none z-50 relative">

            {/* Left: System Identity */}
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 text-neon-cyan">
                    <Cpu size={14} className="animate-pulse" />
                    <span className="tracking-widest font-bold font-orbitron text-[11px]">AXIOM ANTIGRAVITY</span>
                </div>
                <span className="text-gray-600 hidden sm:inline">|</span>
                <div className="hidden sm:flex items-center gap-2 text-neon-green">
                    <ShieldCheck size={14} />
                    <span>SECURE</span>
                </div>
            </div>

            {/* Center: The Heartbeat */}
            <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center gap-2">
                <div className="w-16 md:w-24 h-[1px] bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-50" />
                <span className="text-gray-400 tracking-widest text-[10px]">{time}</span>
                <div className="w-16 md:w-24 h-[1px] bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-50" />
            </div>

            {/* Right: Search & Network Status */}
            <div className="flex items-center gap-4 text-gray-400">
                {/* Command Palette Trigger */}
                <button
                    onClick={onCommandPaletteOpen}
                    className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:border-neon-cyan/30 transition-all"
                >
                    <Search size={12} />
                    <span className="text-[10px]">Ctrl+K</span>
                </button>

                <div className="hidden md:flex items-center gap-2">
                    <span className="text-gray-500">PING:</span>
                    <span className="text-neon-green font-bold">12ms</span>
                </div>

                <div className="flex items-center gap-2">
                    <Wifi size={14} className="text-neon-cyan" />
                    <Radio size={14} className="text-neon-magenta animate-pulse" />
                </div>
            </div>
        </div>
    );
}
