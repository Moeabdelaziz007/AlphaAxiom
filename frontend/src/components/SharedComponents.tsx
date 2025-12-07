import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

// ==================== STAT CARD ====================
interface StatCardProps {
    title?: string; // Made optional to fit usage
    label?: string; // Some pages use label
    value: string | number;
    change?: string;
    positive?: boolean;
    icon?: React.ElementType;
    color?: 'cyan' | 'green' | 'red' | 'yellow' | 'purple' | 'gray';
    status?: string;
}

export function StatCard({ title, label, value, change, positive, icon: Icon, color = 'cyan', status }: StatCardProps) {
    // Map color props to Tailwind classes if needed, or just use string interp for simple cases
    // Handling the variation between Dashboard usage (title) and History usage (label, color)
    const effectiveTitle = title || label;
    const colorClass =
        color === 'green' ? 'text-emerald-400' :
            color === 'red' ? 'text-rose-400' :
                color === 'yellow' ? 'text-yellow-400' :
                    color === 'purple' ? 'text-purple-400' :
                        'text-cyan-400';

    return (
        <div className="glass-card p-4 flex items-center justify-between hover:border-cyan-500/30 transition-all hover-glow-border cursor-default h-full">
            <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-widest">{effectiveTitle}</p>
                <h3 className={`text-xl font-bold mt-1 font-mono ${status === 'online' ? 'text-emerald-400' : status === 'offline' ? 'text-rose-400' : 'text-white'}`}>
                    {value}
                </h3>
                {change && (
                    <span className={`text-xs flex items-center gap-0.5 font-mono ${positive ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {positive ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />} {change}
                    </span>
                )}
            </div>
            <div className={`opacity-60 bg-${color === 'cyan' ? 'cyan' : color}-500/10 p-2 rounded-lg`}>
                {Icon && <Icon size={20} className={colorClass} />}
            </div>
        </div>
    );
}

// ==================== EMPTY STATE ====================
interface EmptyStateProps {
    icon: React.ElementType;
    title: string;
    description: string;
    action?: () => void;
    actionLabel?: string;
}

export function EmptyState({ icon: Icon, title, description, action, actionLabel }: EmptyStateProps) {
    return (
        <div className="flex flex-col items-center justify-center p-8 text-center">
            <div className="bg-white/5 p-4 rounded-full mb-4">
                <Icon size={32} className="text-gray-500" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
            <p className="text-sm text-gray-400 max-w-sm mb-6">{description}</p>
            {action && actionLabel && (
                <button
                    onClick={action}
                    className="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-colors text-sm font-medium hover-glow-cyan"
                >
                    {actionLabel}
                </button>
            )}
        </div>
    );
}

// ==================== TABLE SKELETON ====================
export function TableSkeleton({ rows = 5 }: { rows?: number }) {
    return (
        <div className="w-full animate-pulse">
            <div className="h-10 bg-white/5 rounded-t-xl mb-1" /> {/* Header */}
            {[...Array(rows)].map((_, i) => (
                <div key={i} className="h-14 bg-white/5 mb-1 last:rounded-b-xl" />
            ))}
        </div>
    );
}
