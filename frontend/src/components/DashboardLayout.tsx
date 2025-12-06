"use client";
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard, LineChart, Wallet, History, Bot, Settings, LogOut,
    ChevronRight, User, Bell
} from 'lucide-react';

const routes = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/trade', icon: LineChart, label: 'Terminal' },
    { path: '/portfolio', icon: Wallet, label: 'Portfolio' },
    { path: '/history', icon: History, label: 'History' },
    { path: '/automation', icon: Bot, label: 'Auto-Pilot' },
];

interface DashboardLayoutProps {
    children: React.ReactNode;
    title?: string;
    subtitle?: string;
}

export function DashboardLayout({ children, title, subtitle }: DashboardLayoutProps) {
    const pathname = usePathname();

    return (
        <div className="flex h-screen overflow-hidden">
            {/* Sidebar */}
            <aside className="w-64 h-screen glass-card-strong flex flex-col shrink-0 border-r border-white/5">
                {/* Logo */}
                <div className="p-5 border-b border-white/5">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl overflow-hidden glow-cyan hover-scale cursor-pointer">
                            <img src="/logo.png" alt="Antigravity" className="w-full h-full object-cover" />
                        </div>
                        <div>
                            <h1 className="font-semibold text-white tracking-tight">ANTIGRAVITY</h1>
                            <p className="text-[10px] text-gray-500 font-mono">v2.0 • MoE Brain</p>
                        </div>
                    </div>
                </div>

                {/* User Profile */}
                <div className="p-4 border-b border-white/5">
                    <div className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.02] hover:bg-white/5 transition-colors cursor-pointer">
                        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                            <User size={16} className="text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">Mohamed</p>
                            <p className="text-xs text-gray-500">Pro Trader</p>
                        </div>
                        <span className="px-2 py-0.5 text-[10px] font-medium bg-cyan-500/20 text-cyan-400 rounded-full border border-cyan-500/30">PRO</span>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-3 space-y-1">
                    {routes.map((route) => {
                        const Icon = route.icon;
                        const isActive = pathname === route.path;
                        return (
                            <Link key={route.path} href={route.path} className={`nav-item ${isActive ? 'active' : ''} hover-scale`}>
                                <Icon size={18} />
                                <span className="text-sm font-medium">{route.label}</span>
                                {isActive && <ChevronRight size={14} className="ml-auto opacity-50" />}
                            </Link>
                        );
                    })}
                </nav>

                {/* Bottom Actions */}
                <div className="p-3 border-t border-white/5 space-y-1">
                    <Link href="/settings" className={`nav-item ${pathname === '/settings' ? 'active' : ''}`}>
                        <Settings size={18} />
                        <span className="text-sm">Settings</span>
                    </Link>
                    <button className="nav-item w-full text-left hover:text-red-400">
                        <LogOut size={18} />
                        <span className="text-sm">Disconnect</span>
                    </button>
                </div>

                {/* Status */}
                <div className="p-4 border-t border-white/5">
                    <div className="status-online">
                        <span className="status-dot"></span>
                        <span>Sentinel AI Online</span>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Top Bar */}
                {title && (
                    <header className="h-14 glass-card-strong border-b border-white/5 flex items-center justify-between px-6 shrink-0">
                        <div className="flex items-center gap-4">
                            <div>
                                <h1 className="text-lg font-semibold text-white">{title}</h1>
                                {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
                            </div>
                            <div className="status-online ml-4">
                                <span className="status-dot"></span>
                                <span>Live</span>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <button className="p-2 hover:bg-white/5 rounded-lg transition-colors relative">
                                <Bell size={18} className="text-gray-400" />
                                <span className="absolute top-1 right-1 w-2 h-2 bg-rose-500 rounded-full"></span>
                            </button>
                        </div>
                    </header>
                )}

                {/* Page Content */}
                <main className="flex-1 overflow-auto">
                    {children}
                </main>
            </div>
        </div>
    );
}

// Skeleton Components
export function CardSkeleton() {
    return (
        <div className="glass-card p-6 animate-pulse">
            <div className="h-4 bg-white/5 rounded w-1/3 mb-4"></div>
            <div className="h-8 bg-white/10 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-white/5 rounded w-1/4"></div>
        </div>
    );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
    return (
        <div className="glass-card overflow-hidden">
            <div className="p-4 border-b border-white/5">
                <div className="h-5 bg-white/10 rounded w-1/4 animate-pulse"></div>
            </div>
            <div className="divide-y divide-white/5">
                {Array.from({ length: rows }).map((_, i) => (
                    <div key={i} className="p-4 flex gap-4 animate-pulse">
                        <div className="h-4 bg-white/5 rounded flex-1"></div>
                        <div className="h-4 bg-white/5 rounded w-20"></div>
                        <div className="h-4 bg-white/5 rounded w-24"></div>
                        <div className="h-4 bg-white/5 rounded w-16"></div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export function ChartSkeleton() {
    return (
        <div className="glass-card h-full flex items-center justify-center">
            <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white/5 animate-pulse"></div>
                <div className="h-4 bg-white/5 rounded w-32 mx-auto animate-pulse"></div>
            </div>
        </div>
    );
}

// Empty State Component
export function EmptyState({
    icon: Icon,
    title,
    description,
    action,
    actionLabel
}: {
    icon: React.ElementType;
    title: string;
    description: string;
    action?: () => void;
    actionLabel?: string;
}) {
    return (
        <div className="flex flex-col items-center justify-center py-16 px-8 text-center">
            <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mb-4">
                <Icon size={28} className="text-gray-500" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">{title}</h3>
            <p className="text-gray-500 text-sm max-w-sm mb-6">{description}</p>
            {action && actionLabel && (
                <button onClick={action} className="btn-primary">
                    {actionLabel}
                </button>
            )}
        </div>
    );
}

// Stat Card Component
export function StatCard({
    label,
    value,
    change,
    icon: Icon,
    color = 'cyan'
}: {
    label: string;
    value: string | number;
    change?: string;
    icon: React.ElementType;
    color?: 'cyan' | 'green' | 'red';
}) {
    const colorClasses = {
        cyan: 'text-cyan-400',
        green: 'text-emerald-400',
        red: 'text-rose-400',
    };

    return (
        <div className="stat-card">
            <div className="flex items-center justify-between mb-2">
                <span className="stat-label">{label}</span>
                <Icon size={16} className={colorClasses[color]} />
            </div>
            <div className="stat-value font-mono">{value}</div>
            {change && (
                <div className={`text-sm mt-1 font-mono ${change.startsWith('+') ? 'text-emerald-400' : change.startsWith('-') ? 'text-rose-400' : 'text-gray-400'}`}>
                    {change}
                </div>
            )}
        </div>
    );
}
