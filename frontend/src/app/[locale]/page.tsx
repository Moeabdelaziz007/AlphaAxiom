"use client";
import SignalFeed from '@/components/SignalFeed';
import TwinTurboGauges from '@/components/TwinTurboGauges';
import { Activity, Bell, TrendingUp, Zap } from 'lucide-react';

// Stats Card Component
function StatCard({
    label,
    value,
    change,
    icon: Icon
}: {
    label: string;
    value: string;
    change?: string;
    icon: React.ElementType;
}) {
    const isPositive = change?.startsWith('+');

    return (
        <div className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-5 hover:border-white/10 transition-colors">
            <div className="flex items-center justify-between mb-3">
                <span className="text-[13px] text-white/40">{label}</span>
                <Icon size={16} className="text-white/20" />
            </div>
            <div className="flex items-end gap-2">
                <span className="text-2xl font-semibold text-white tracking-tight">{value}</span>
                {change && (
                    <span className={`text-[12px] font-medium mb-1 ${isPositive ? 'text-emerald-400' : 'text-rose-400'
                        }`}>
                        {change}
                    </span>
                )}
            </div>
        </div>
    );
}

export default function SignalHubDashboard() {
    return (
        <div className="min-h-screen bg-[#09090b]">
            {/* Header */}
            <header className="h-14 border-b border-white/[0.06] flex items-center justify-between px-6">
                <div>
                    <h1 className="text-[15px] font-semibold text-white">Signal Hub</h1>
                    <p className="text-[12px] text-white/40">Real-time market intelligence</p>
                </div>
                <div className="flex items-center gap-3">
                    <button className="p-2 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] transition-colors">
                        <Bell size={18} className="text-white/60" />
                    </button>
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                        <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                        <span className="text-[12px] text-emerald-400 font-medium">Live</span>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="p-6 max-w-7xl mx-auto">
                {/* Stats Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <StatCard
                        label="Signals Today"
                        value="12"
                        change="+3"
                        icon={Zap}
                    />
                    <StatCard
                        label="S-TIER Hits"
                        value="4"
                        change="+2"
                        icon={TrendingUp}
                    />
                    <StatCard
                        label="Accuracy Rate"
                        value="78%"
                        change="+5%"
                        icon={Activity}
                    />
                    <StatCard
                        label="Active Assets"
                        value="6"
                        icon={Activity}
                    />
                </div>

                {/* Twin-Turbo Gauges */}
                <div className="mb-8">
                    <TwinTurboGauges />
                </div>

                {/* Signal Feed */}
                <SignalFeed />
            </main>
        </div>
    );
}
