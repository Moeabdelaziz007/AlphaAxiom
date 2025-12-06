"use client";
import React, { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard, LineChart, Wallet, History, Bot, Settings, LogOut, Zap,
    Send, TrendingUp, TrendingDown, Activity, Bell, RefreshCw, ChevronRight
} from 'lucide-react';
import { TradingChart } from '@/components/TradingChart';

const API_BASE = "https://trading-brain-v1.amrikyy1.workers.dev";

// ==================== SIDEBAR ====================
const routes = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard', color: 'text-cyan-400' },
    { path: '/trade', icon: LineChart, label: 'Terminal', color: 'text-green-400' },
    { path: '/portfolio', icon: Wallet, label: 'Portfolio', color: 'text-yellow-400' },
    { path: '/history', icon: History, label: 'History', color: 'text-purple-400' },
    { path: '/automation', icon: Bot, label: 'Auto-Pilot', color: 'text-red-400' },
    { path: '/settings', icon: Settings, label: 'Settings', color: 'text-gray-400' },
];

function Sidebar() {
    const pathname = usePathname();
    return (
        <div className="w-[260px] h-full glass-card-strong flex flex-col shrink-0">
            {/* Logo */}
            <div className="p-6 border-b border-white/5">
                <div className="flex items-center gap-3">
                    <div className="w-11 h-11 gradient-cyan rounded-xl flex items-center justify-center glow-cyan">
                        <Zap size={22} className="text-white" />
                    </div>
                    <div>
                        <h1 className="font-bold text-white tracking-wide">ANTIGRAVITY</h1>
                        <p className="text-[10px] text-gray-500">Trading LLM v2.0</p>
                    </div>
                </div>
            </div>

            {/* Nav */}
            <nav className="flex-1 p-4 space-y-1">
                {routes.map((route) => {
                    const Icon = route.icon;
                    const isActive = pathname === route.path;
                    return (
                        <Link key={route.path} href={route.path}
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${isActive ? 'glass-card border-cyan-500/30 text-white' : 'text-gray-400 hover:bg-white/5 hover:text-white'
                                }`}
                        >
                            <Icon size={20} className={isActive ? route.color : ''} />
                            <span className="text-sm font-medium">{route.label}</span>
                        </Link>
                    );
                })}
            </nav>

            {/* Status */}
            <div className="p-4 border-t border-white/5">
                <div className="bento-item p-3 space-y-2">
                    <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">AI Status</span>
                        <div className="flex items-center gap-1.5">
                            <div className="w-2 h-2 rounded-full bg-green-500 status-pulse" />
                            <span className="text-xs text-green-400">Online</span>
                        </div>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">Model</span>
                        <span className="text-xs text-cyan-400">Groq + Gemini</span>
                    </div>
                </div>
            </div>

            {/* Logout */}
            <div className="p-4 pt-0">
                <button className="flex items-center gap-3 px-4 py-3 w-full text-gray-500 hover:text-red-400 hover:bg-white/5 rounded-xl transition-all">
                    <LogOut size={18} />
                    <span className="text-sm">Disconnect</span>
                </button>
            </div>
        </div>
    );
}

// ==================== MAIN DASHBOARD ====================
export default function Dashboard() {
    const [messages, setMessages] = useState([
        { role: 'ai', content: '🧠 AntigravityTradingLLM Online. Ask me to analyze markets, execute trades, or check news.' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [portfolio, setPortfolio] = useState({ portfolio_value: '100000', buying_power: '200000', cash: '100000' });
    const [activeSymbol, setActiveSymbol] = useState('SPY');
    const [systemStatus, setSystemStatus] = useState({ trades_today: 0, max_trades: 10 });
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const watchlist = [
        { symbol: 'SPY', name: 'S&P 500', change: 1.24 },
        { symbol: 'AAPL', name: 'Apple', change: 2.15 },
        { symbol: 'TSLA', name: 'Tesla', change: -0.87 },
        { symbol: 'GOOGL', name: 'Alphabet', change: 0.56 },
        { symbol: 'GLD', name: 'Gold ETF', change: 0.34 },
        { symbol: 'BTC', name: 'Bitcoin', change: 3.21 },
    ];

    const fetchData = useCallback(async () => {
        try {
            const [accRes, statusRes] = await Promise.all([
                fetch(`${API_BASE}/api/account`),
                fetch(`${API_BASE}/api/status`)
            ]);
            if (accRes.ok) setPortfolio(await accRes.json());
            if (statusRes.ok) setSystemStatus(await statusRes.json());
        } catch (e) { console.error(e); }
    }, []);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, [fetchData]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;
        setMessages(prev => [...prev, { role: 'user', content: input }]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: input })
            });
            const data = await res.json();

            if (data.type === 'SHOW_CHART' && data.symbol) setActiveSymbol(data.symbol);
            if (data.trade_executed?.status === 'success') setTimeout(fetchData, 1000);

            setMessages(prev => [...prev, { role: 'ai', content: data.reply || JSON.stringify(data) }]);
        } catch {
            setMessages(prev => [...prev, { role: 'ai', content: '⚠️ Connection error' }]);
        }
        setLoading(false);
    };

    return (
        <div className="flex h-screen overflow-hidden">
            <div className="animated-bg" />
            <Sidebar />

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Top Bar */}
                <header className="h-16 glass-card-strong border-b border-white/5 flex items-center justify-between px-6 shrink-0">
                    <div className="flex items-center gap-4">
                        <h1 className="text-lg font-bold">Dashboard</h1>
                        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/30">
                            <div className="w-2 h-2 rounded-full bg-green-500 status-pulse" />
                            <span className="text-green-400 text-xs font-medium">Live</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-6">
                        <button onClick={fetchData} className="p-2 hover:bg-white/5 rounded-lg transition-all">
                            <RefreshCw size={18} className="text-gray-400" />
                        </button>
                        <button className="p-2 hover:bg-white/5 rounded-lg transition-all relative">
                            <Bell size={18} className="text-gray-400" />
                            <div className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
                        </button>
                        <div className="flex items-center gap-3 pl-4 border-l border-white/10">
                            <div className="w-8 h-8 gradient-purple rounded-lg flex items-center justify-center">
                                <span className="text-white text-sm font-bold">M</span>
                            </div>
                            <span className="text-sm text-gray-300">Mohamed</span>
                        </div>
                    </div>
                </header>

                {/* Dashboard Grid */}
                <div className="flex-1 p-6 overflow-auto">
                    <div className="grid grid-cols-12 gap-4 h-full">

                        {/* Stats Row */}
                        <div className="col-span-3 bento-item flex flex-col">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs text-gray-500 uppercase">Portfolio Value</span>
                                <Wallet size={16} className="text-cyan-400" />
                            </div>
                            <div className="text-2xl font-bold text-white">
                                ${parseFloat(portfolio.portfolio_value).toLocaleString()}
                            </div>
                            <div className="flex items-center gap-1 mt-1">
                                <TrendingUp size={14} className="text-green-400" />
                                <span className="text-sm text-green-400">+2.4% today</span>
                            </div>
                        </div>

                        <div className="col-span-3 bento-item flex flex-col">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs text-gray-500 uppercase">Buying Power</span>
                                <Activity size={16} className="text-green-400" />
                            </div>
                            <div className="text-2xl font-bold text-green-400">
                                ${parseFloat(portfolio.buying_power).toLocaleString()}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">Available for trading</div>
                        </div>

                        <div className="col-span-3 bento-item flex flex-col">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs text-gray-500 uppercase">Trades Today</span>
                                <LineChart size={16} className="text-purple-400" />
                            </div>
                            <div className="text-2xl font-bold text-white">
                                {systemStatus.trades_today}/{systemStatus.max_trades}
                            </div>
                            <div className="w-full h-1.5 bg-gray-800 rounded-full mt-2">
                                <div className="h-full gradient-purple rounded-full" style={{ width: `${(systemStatus.trades_today / systemStatus.max_trades) * 100}%` }} />
                            </div>
                        </div>

                        <div className="col-span-3 bento-item flex flex-col">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs text-gray-500 uppercase">AI Status</span>
                                <Bot size={16} className="text-cyan-400" />
                            </div>
                            <div className="text-2xl font-bold text-cyan-400">Active</div>
                            <div className="text-xs text-gray-500 mt-1">Groq + Gemini MoE</div>
                        </div>

                        {/* Chart Area */}
                        <div className="col-span-8 row-span-2 bento-item p-0 overflow-hidden">
                            <div className="h-full">
                                <TradingChart symbol={activeSymbol} timeframe="1H" />
                            </div>
                        </div>

                        {/* Watchlist */}
                        <div className="col-span-4 row-span-2 bento-item flex flex-col">
                            <div className="flex items-center justify-between mb-4">
                                <span className="text-sm font-bold">Watchlist</span>
                                <button className="text-xs text-cyan-400 hover:underline">+ Add</button>
                            </div>
                            <div className="flex-1 space-y-2 overflow-auto">
                                {watchlist.map((item) => (
                                    <button key={item.symbol} onClick={() => setActiveSymbol(item.symbol)}
                                        className={`w-full flex items-center justify-between p-3 rounded-xl transition-all ${activeSymbol === item.symbol ? 'bg-cyan-500/10 border border-cyan-500/30' : 'hover:bg-white/5'
                                            }`}
                                    >
                                        <div className="text-left">
                                            <div className="font-bold text-white">{item.symbol}</div>
                                            <div className="text-xs text-gray-500">{item.name}</div>
                                        </div>
                                        <div className={`flex items-center gap-1 ${item.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                            {item.change >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                                            <span className="text-sm font-medium">{item.change >= 0 ? '+' : ''}{item.change}%</span>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Chat */}
                        <div className="col-span-12 bento-item flex flex-col" style={{ height: '280px' }}>
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 gradient-green rounded-lg flex items-center justify-center">
                                        <Bot size={16} className="text-white" />
                                    </div>
                                    <div>
                                        <div className="font-bold text-sm">Sentinel AI</div>
                                        <div className="text-xs text-green-400">Ready</div>
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    {['Analyze SPY', 'Buy 5 AAPL', 'News TSLA'].map((q) => (
                                        <button key={q} onClick={() => setInput(q)}
                                            className="text-xs px-3 py-1.5 rounded-full bg-white/5 text-gray-400 hover:text-cyan-400 hover:bg-cyan-500/10 transition-all"
                                        >{q}</button>
                                    ))}
                                </div>
                            </div>

                            <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                                {messages.map((msg, i) => (
                                    <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                        <div className={`max-w-[70%] px-4 py-2.5 text-sm ${msg.role === 'user' ? 'chat-bubble-user text-cyan-100' : 'chat-bubble-ai text-gray-300'
                                            }`}>
                                            {msg.content}
                                        </div>
                                    </div>
                                ))}
                                {loading && (
                                    <div className="flex justify-start">
                                        <div className="chat-bubble-ai px-4 py-2.5 flex items-center gap-1">
                                            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
                                            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                                            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>

                            <div className="mt-4 relative">
                                <input type="text" value={input} onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                    placeholder="Ask Sentinel AI..."
                                    className="input-glass w-full pr-12"
                                />
                                <button onClick={handleSend} disabled={loading}
                                    className="absolute right-2 top-1/2 -translate-y-1/2 p-2 gradient-cyan rounded-lg disabled:opacity-50"
                                >
                                    <Send size={16} className="text-white" />
                                </button>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
}
