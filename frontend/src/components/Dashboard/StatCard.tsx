'use client';

import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
    title: string;
    value: string;
    icon: LucideIcon;
    color: 'profit' | 'loss' | 'cyan' | 'gold' | 'blue';
    subtitle?: string;
}

const colorStyles = {
    profit: {
        iconBg: 'bg-neon-green/10',
        iconColor: 'text-neon-green',
        valueColor: 'text-neon-green glow-green',
        border: 'border-neon-green/20',
    },
    loss: {
        iconBg: 'bg-neon-red/10',
        iconColor: 'text-neon-red',
        valueColor: 'text-neon-red glow-red',
        border: 'border-neon-red/20',
    },
    cyan: {
        iconBg: 'bg-neon-cyan/10',
        iconColor: 'text-neon-cyan',
        valueColor: 'text-neon-cyan',
        border: 'border-neon-cyan/20',
    },
    gold: {
        iconBg: 'bg-neon-gold/10',
        iconColor: 'text-neon-gold',
        valueColor: 'text-neon-gold glow-gold',
        border: 'border-neon-gold/20',
    },
    blue: {
        iconBg: 'bg-blue-500/10',
        iconColor: 'text-blue-400',
        valueColor: 'text-blue-400',
        border: 'border-blue-500/20',
    },
};

export default function StatCard({ title, value, icon: Icon, color, subtitle }: StatCardProps) {
    const styles = colorStyles[color];

    return (
        <div className={`glass-panel rounded-xl p-4 border ${styles.border} 
                        transition-all duration-300 hover:scale-[1.02] fade-in`}>
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wider">{title}</p>
                    <p className={`text-xl font-bold mt-1 font-mono ${styles.valueColor}`}>
                        {value}
                    </p>
                    {subtitle && (
                        <p className="text-xs text-gray-600 mt-1">{subtitle}</p>
                    )}
                </div>
                <div className={`p-2.5 rounded-lg ${styles.iconBg}`}>
                    <Icon className={`w-5 h-5 ${styles.iconColor}`} />
                </div>
            </div>
        </div>
    );
}
