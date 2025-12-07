import React from 'react';

export function CardSkeleton() {
    return (
        <div className="glass-card p-4 flex items-center justify-between border-white/5 animate-pulse">
            <div className="space-y-2 w-full">
                <div className="h-3 bg-white/10 rounded w-1/3" />
                <div className="h-6 bg-white/10 rounded w-2/3" />
                <div className="h-3 bg-white/10 rounded w-1/4" />
            </div>
            <div className="h-8 w-8 bg-white/10 rounded-full" />
        </div>
    );
}

export function ChartSkeleton() {
    return (
        <div className="w-full h-full bg-[#050505] animate-pulse flex flex-col items-center justify-center gap-4">
            <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-cyan-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 rounded-full bg-cyan-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 rounded-full bg-cyan-500 animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <span className="text-xs text-cyan-500/50 font-mono tracking-widest uppercase">Initializing Quantum Core...</span>
        </div>
    );
}
