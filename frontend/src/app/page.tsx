"use client";
import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
    Send, Bot, Wallet, TrendingUp, Activity, User,
    Search, Newspaper, Zap, Shield, Settings,
    BarChart3, ChevronRight, AlertCircle,
    Globe, Clock, Target
} from 'lucide-react';
import { TradingChart } from '@/components/TradingChart';

// API Configuration
const API_BASE = "https://trading-brain-v1.amrikyy1.workers.dev";

interface Message {
    role: 'user' | 'system';
    type: 'text' | 'trade_card' | 'error' | 'news';
    content: string;
    details?: {
        symbol?: string;
        side?: string;
        qty?: number;
        order_id?: string;
    };
}

interface Portfolio {
    portfolio_value: string;
    buying_power: string;
    cash: string;
}

// Generate demo candle data
const generateDemoCandles = (symbol: string) => {
    const candles = [];
    let basePrice = symbol === 'SPY' ? 595 : symbol === 'AAPL' ? 245 : symbol === 'TSLA' ? 380 : 100;
    const now = new Date();

    for (let i = 100; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 3600000);
        const open = basePrice + (Math.random() - 0.5) * 5;
        const close = open + (Math.random() - 0.5) * 8;
        const high = Math.max(open, close) + Math.random() * 3;
        const low = Math.min(open, close) - Math.random() * 3;
        const volume = Math.floor(Math.random() * 2000000) + 500000;

        candles.push({
            time: time.toISOString().split('T')[0] + ' ' + time.toISOString().split('T')[1].slice(0, 5),
            open, high, low, close, volume
        });

        basePrice = close;
    }
    return candles;
};

export default function AntigravityTerminal() {
    // State
    const [messages, setMessages] = useState<Message[]>([
        { role: 'system', type: 'text', content: '🧠 ANTIGRAVITY AI Online. I can analyze markets, execute trades, and search for news. Try "Analyze SPY" or "Buy 10 AAPL".' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
    const [activeSymbol, setActiveSymbol] = useState('SPY');
    const [chartData, setChartData] = useState(generateDemoCandles('SPY'));
    const [news, setNews] = useState<string[]>([]);
    const [systemStatus, setSystemStatus] = useState<{ trades_today: number, max_trades: number }>({ trades_today: 0, max_trades: 10 });
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Fetch portfolio and status
    const fetchPortfolio = useCallback(async () => {
        try {
            const [accountRes, statusRes] = await Promise.all([
                fetch(`${API_BASE}/api/account`),
                fetch(`${API_BASE}/api/status`)
            ]);

            if (accountRes.ok) {
                const data = await accountRes.json();
                setPortfolio(data);
            }
            if (statusRes.ok) {
                const status = await statusRes.json();
                setSystemStatus(status);
            }
        } catch (e) {
            console.error("Connection error", e);
        }
    }, []);

    useEffect(() => {
        fetchPortfolio();
        const interval = setInterval(fetchPortfolio, 30000);
        return () => clearInterval(interval);
    }, [fetchPortfolio]);

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, scrollToBottom]);

    // Handle symbol change
    const handleSymbolChange = (symbol: string) => {
        setActiveSymbol(symbol);
        setChartData(generateDemoCandles(symbol));
    };

    // Send message
    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = { role: 'user', type: 'text', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg.content })
            });

            const data = await res.json();

            let aiMsg: Message;

            if (data.trade_executed && data.trade_executed.status === 'success') {
                aiMsg = {
                    role: 'system',
                    type: 'trade_card',
                    content: data.trade_executed.message,
                    details: data.trade_executed
                };
                setTimeout(fetchPortfolio, 1000);
            } else {
                aiMsg = {
                    role: 'system',
                    type: 'text',
                    content: data.reply || data.message || JSON.stringify(data)
                };
            }

            // Check if AI wants to show a chart
            if (data.type === 'SHOW_CHART' || input.toLowerCase().includes('chart') || input.toLowerCase().includes('show')) {
                const symbolMatch = input.match(/\b(SPY|AAPL|TSLA|GOOGL|MSFT|AMZN|GLD)\b/i);
                if (symbolMatch) {
                    handleSymbolChange(symbolMatch[1].toUpperCase());
                }
            }

            setMessages(prev => [...prev, aiMsg]);

        } catch {
            setMessages(prev => [...prev, { role: 'system', type: 'error', content: "⚠️ Connection Lost with Cloud Brain." }]);
        } finally {
            setLoading(false);
        }
    };

    const watchlist = ['SPY', 'AAPL', 'TSLA', 'GOOGL', 'GLD'];

    return (
        <div className="flex h-screen bg-[#030303] text-gray-100 font-sans overflow-hidden">

            {/* ========== LEFT SIDEBAR - Mini Nav ========== */}
            <div className="w-16 bg-[#0a0a0a] border-r border-gray-800/50 flex flex-col items-center py-4 gap-4">
                <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-cyan-500/20">
                    <Zap size={20} className="text-white" />
                </div>

                <div className="flex-1 flex flex-col items-center gap-2 mt-4">
                    <button className="w-10 h-10 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center hover:bg-cyan-500/20 transition-all">
                        <BarChart3 size={18} />
                    </button>
                    <button className="w-10 h-10 rounded-xl text-gray-500 flex items-center justify-center hover:bg-gray-800 transition-all">
                        <Newspaper size={18} />
                    </button>
                    <button className="w-10 h-10 rounded-xl text-gray-500 flex items-center justify-center hover:bg-gray-800 transition-all">
                        <Globe size={18} />
                    </button>
                    <button className="w-10 h-10 rounded-xl text-gray-500 flex items-center justify-center hover:bg-gray-800 transition-all">
                        <Target size={18} />
                    </button>
                </div>

                <div className="flex flex-col items-center gap-2">
                    <button className="w-10 h-10 rounded-xl text-gray-500 flex items-center justify-center hover:bg-gray-800 transition-all">
                        <Settings size={18} />
                    </button>
                </div>
            </div>

            {/* ========== MAIN CONTENT - Chart & Tools ========== */}
            <div className="flex-1 flex flex-col p-4 gap-4 overflow-hidden">

                {/* Top Bar */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                            ANTIGRAVITY TERMINAL
                        </h1>
                        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/30">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                            <span className="text-green-400 text-xs font-medium">v5.0 Live</span>
                        </div>
                    </div>

                    {/* Portfolio Mini */}
                    <div className="flex items-center gap-6">
                        <div className="text-right">
                            <p className="text-xs text-gray-500">Portfolio Value</p>
                            <p className="text-lg font-bold text-white">
                                ${portfolio ? parseFloat(portfolio.portfolio_value).toLocaleString() : '100,000.00'}
                            </p>
                        </div>
                        <div className="text-right">
                            <p className="text-xs text-gray-500">Buying Power</p>
                            <p className="text-lg font-bold text-green-400">
                                ${portfolio ? parseFloat(portfolio.buying_power).toLocaleString() : '200,000.00'}
                            </p>
                        </div>
                        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-900 border border-gray-800">
                            <Shield size={16} className="text-cyan-400" />
                            <span className="text-sm text-gray-400">{systemStatus.trades_today}/{systemStatus.max_trades} trades</span>
                        </div>
                    </div>
                </div>

                {/* Watchlist Bar */}
                <div className="flex items-center gap-2 overflow-x-auto pb-2">
                    {watchlist.map((symbol) => (
                        <button
                            key={symbol}
                            onClick={() => handleSymbolChange(symbol)}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all whitespace-nowrap ${activeSymbol === symbol
                                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 text-cyan-400'
                                    : 'bg-gray-900/50 border border-gray-800/50 text-gray-400 hover:border-gray-700'
                                }`}
                        >
                            <span className="font-medium">{symbol}</span>
                            <span className="text-green-400 text-xs">+0.5%</span>
                        </button>
                    ))}
                    <button className="flex items-center gap-1 px-3 py-2 rounded-lg bg-gray-900/30 border border-dashed border-gray-800 text-gray-600 hover:border-gray-700 transition-all">
                        <Search size={14} />
                        <span className="text-sm">Add Symbol</span>
                    </button>
                </div>

                {/* Chart Area */}
                <div className="flex-1 min-h-0">
                    <TradingChart data={chartData} symbol={activeSymbol} timeframe="1H" />
                </div>

                {/* Bottom Panel - News & Insights */}
                <div className="h-32 bg-gradient-to-r from-gray-900/80 to-gray-900/40 backdrop-blur-sm border border-gray-800/50 rounded-xl p-4 overflow-hidden">
                    <div className="flex items-center gap-2 mb-3">
                        <Newspaper size={14} className="text-cyan-400" />
                        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Market Intelligence</h3>
                        <div className="ml-auto flex items-center gap-1 text-xs text-gray-600">
                            <Clock size={12} />
                            <span>Updated 2m ago</span>
                        </div>
                    </div>
                    <div className="flex gap-4 overflow-x-auto">
                        <div className="flex-shrink-0 p-3 bg-gray-800/30 rounded-lg border border-gray-800/50 max-w-xs">
                            <p className="text-sm text-gray-300 line-clamp-2">SPY reaches new all-time high as tech stocks rally continues...</p>
                            <p className="text-xs text-cyan-400 mt-1">Yahoo Finance • 15m ago</p>
                        </div>
                        <div className="flex-shrink-0 p-3 bg-gray-800/30 rounded-lg border border-gray-800/50 max-w-xs">
                            <p className="text-sm text-gray-300 line-clamp-2">Apple announces new AI features, stock jumps 3% in pre-market...</p>
                            <p className="text-xs text-cyan-400 mt-1">Bloomberg • 1h ago</p>
                        </div>
                        <div className="flex-shrink-0 p-3 bg-gray-800/30 rounded-lg border border-gray-800/50 max-w-xs">
                            <p className="text-sm text-gray-300 line-clamp-2">Fed signals potential rate changes in upcoming meeting...</p>
                            <p className="text-xs text-cyan-400 mt-1">Reuters • 2h ago</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* ========== RIGHT SIDEBAR - Chat ========== */}
            <div className="w-[380px] bg-[#0a0a0a]/80 backdrop-blur-sm border-l border-gray-800/50 flex flex-col">

                {/* Chat Header */}
                <div className="p-4 border-b border-gray-800/50">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-green-500/20">
                            <Bot size={20} className="text-white" />
                        </div>
                        <div>
                            <h2 className="font-bold text-white">Sentinel AI</h2>
                            <p className="text-xs text-green-400">Connected • D1 Database Active</p>
                        </div>
                    </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`flex gap-2 max-w-[90%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                                <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-cyan-500/20' : 'bg-green-500/20'
                                    }`}>
                                    {msg.role === 'user' ? <User size={12} className="text-cyan-400" /> : <Bot size={12} className="text-green-400" />}
                                </div>

                                <div className={`p-3 rounded-2xl text-sm leading-relaxed ${msg.role === 'user'
                                        ? 'bg-cyan-500/10 border border-cyan-500/20 text-cyan-100 rounded-tr-sm'
                                        : 'bg-gray-800/50 border border-gray-700/50 text-gray-300 rounded-tl-sm'
                                    }`}>
                                    {msg.type === 'text' && <p className="whitespace-pre-wrap">{msg.content}</p>}

                                    {msg.type === 'trade_card' && msg.details && (
                                        <div className="space-y-2">
                                            <div className="flex items-center gap-2 text-green-400 font-bold text-xs border-b border-gray-700/50 pb-2">
                                                <TrendingUp size={14} /> ORDER EXECUTED
                                            </div>
                                            <div className="grid grid-cols-2 gap-2 text-xs">
                                                <div>
                                                    <span className="text-gray-500 block">SYMBOL</span>
                                                    <span className="text-white font-bold">{msg.details.symbol}</span>
                                                </div>
                                                <div>
                                                    <span className="text-gray-500 block">SIDE</span>
                                                    <span className={`font-bold ${msg.details.side === 'buy' ? 'text-green-400' : 'text-red-400'}`}>
                                                        {msg.details.side?.toUpperCase()}
                                                    </span>
                                                </div>
                                                <div>
                                                    <span className="text-gray-500 block">QTY</span>
                                                    <span className="text-white">{msg.details.qty}</span>
                                                </div>
                                                <div>
                                                    <span className="text-gray-500 block">ID</span>
                                                    <span className="text-gray-600 text-[10px] truncate block">{msg.details.order_id?.slice(0, 8)}...</span>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {msg.type === 'error' && (
                                        <div className="flex items-center gap-2 text-red-400">
                                            <AlertCircle size={14} />
                                            <span>{msg.content}</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}

                    {loading && (
                        <div className="flex gap-2">
                            <div className="w-7 h-7 rounded-lg bg-green-500/20 flex items-center justify-center">
                                <Bot size={12} className="text-green-400" />
                            </div>
                            <div className="flex items-center gap-1 h-7 px-3 bg-gray-800/50 rounded-2xl">
                                <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" />
                                <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '75ms' }} />
                                <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Quick Actions */}
                <div className="px-4 pb-2">
                    <div className="flex gap-2 overflow-x-auto pb-2">
                        {['Analyze SPY', 'Buy 5 AAPL', 'Market news', 'My positions'].map((action) => (
                            <button
                                key={action}
                                onClick={() => setInput(action)}
                                className="text-xs px-3 py-1.5 rounded-full bg-gray-800/50 border border-gray-700/50 text-gray-400 hover:border-cyan-500/30 hover:text-cyan-400 transition-all whitespace-nowrap"
                            >
                                {action}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Input Area */}
                <div className="p-4 bg-gray-900/50 border-t border-gray-800/50">
                    <div className="relative">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            placeholder="Ask Sentinel to trade, analyze, or search..."
                            className="w-full bg-gray-800/50 text-white border border-gray-700/50 rounded-xl py-3 pl-4 pr-12 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30 transition-all text-sm"
                        />
                        <button
                            onClick={handleSend}
                            disabled={loading}
                            className="absolute right-2 top-2 p-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg transition-all hover:shadow-lg hover:shadow-cyan-500/20 disabled:opacity-50"
                        >
                            <Send size={16} />
                        </button>
                    </div>
                    <p className="text-center text-[10px] text-gray-600 mt-2">
                        Powered by Groq LLM • D1 Database • Zero Cost
                    </p>
                </div>
            </div>
        </div>
    );
}
