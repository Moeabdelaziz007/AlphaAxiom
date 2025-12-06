"use client";
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Bot, Wallet, TrendingUp, Activity, User, ShieldAlert } from 'lucide-react';

// إعدادات الـ API الخاص بك
const API_BASE = "https://trading-brain-v1.amrikyy1.workers.dev";

interface Message {
    role: 'user' | 'system';
    type: 'text' | 'trade_card' | 'error';
    content: string;
    details?: {
        symbol: string;
        side: string;
        qty: number;
        order_id: string;
    };
}

interface Portfolio {
    portfolio_value: string;
    buying_power: string;
    cash: string;
}

export default function SmartTradingTerminal() {
    // --- States ---
    const [messages, setMessages] = useState<Message[]>([
        { role: 'system', type: 'text', content: '🧠 Antigravity AI Online. Ready for market analysis and execution.' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // --- 1. جلب بيانات المحفظة عند التحميل ---
    const fetchPortfolio = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/account`);
            if (res.ok) {
                const data = await res.json();
                setPortfolio(data);
            }
        } catch (e) {
            console.error("Connection error", e);
        }
    }, []);

    useEffect(() => {
        fetchPortfolio();
        const interval = setInterval(fetchPortfolio, 10000); // تحديث كل 10 ثواني
        return () => clearInterval(interval);
    }, [fetchPortfolio]);

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, scrollToBottom]);

    // --- 2. إرسال الرسائل (Logic) ---
    const handleSend = async () => {
        if (!input.trim()) return;

        // إضافة رسالة المستخدم
        const userMsg: Message = { role: 'user', type: 'text', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            // الاتصال بـ Cloudflare Worker
            const res = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg.content })
            });

            const data = await res.json();

            // تحليل الرد (هل هو نص عادي أم صفقة؟)
            let aiMsg: Message;

            // إذا كان الرد يحتوي على تفاصيل صفقة
            if (data.trade_executed && data.trade_executed.status === 'success') {
                aiMsg = {
                    role: 'system',
                    type: 'trade_card',
                    content: data.trade_executed.message,
                    details: data.trade_executed
                };
                // تحديث المحفظة فوراً بعد الصفقة
                setTimeout(fetchPortfolio, 1000);
            } else {
                // رد عادي (تحليل أو شات)
                aiMsg = {
                    role: 'system',
                    type: 'text',
                    content: data.reply || data.message || JSON.stringify(data)
                };
            }

            setMessages(prev => [...prev, aiMsg]);

        } catch {
            setMessages(prev => [...prev, { role: 'system', type: 'error', content: "⚠️ Connection Lost with Cloud Brain." }]);
        } finally {
            setLoading(false);
        }
    };

    // --- Render ---
    return (
        <div className="flex h-screen bg-[#050505] text-gray-100 font-mono overflow-hidden">

            {/* LEFT SIDEBAR: Portfolio & Stats */}
            <div className="w-80 bg-[#0a0a0a] border-r border-gray-800 p-6 flex-col gap-6 hidden md:flex">
                <div className="flex items-center gap-2 mb-4">
                    <Activity className="text-cyan-400" />
                    <h1 className="font-bold text-lg tracking-wider">ANTIGRAVITY</h1>
                </div>

                {/* Portfolio Card */}
                <div className="bg-gradient-to-br from-gray-900 to-black border border-gray-800 p-5 rounded-xl shadow-lg relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Wallet size={48} className="text-cyan-500" />
                    </div>
                    <p className="text-gray-400 text-xs uppercase mb-1">Total Equity</p>
                    <h2 className="text-3xl font-bold text-white mb-4">
                        ${portfolio ? parseFloat(portfolio.portfolio_value).toLocaleString() : '100,000.00'}
                    </h2>

                    <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                            <span className="text-gray-500">Buying Power</span>
                            <span className="text-green-400">${portfolio ? parseFloat(portfolio.buying_power).toLocaleString() : '200,000.00'}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                            <span className="text-gray-500">Cash</span>
                            <span className="text-blue-400">${portfolio ? parseFloat(portfolio.cash).toLocaleString() : '100,000.00'}</span>
                        </div>
                    </div>
                </div>

                {/* Active Rules (Sidebar) */}
                <div className="flex-1 overflow-y-auto">
                    <h3 className="text-xs font-bold text-gray-500 uppercase mb-3 flex items-center gap-2">
                        <ShieldAlert size={12} /> Active Automations
                    </h3>
                    <div className="space-y-2">
                        <div className="bg-gray-900/50 border border-gray-800 p-3 rounded text-xs flex justify-between items-center opacity-50">
                            <span>No active rules. Chat with AI to set one.</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* MAIN CHAT AREA */}
            <div className="flex-1 flex flex-col relative">
                {/* Header (Mobile only) */}
                <div className="md:hidden p-4 border-b border-gray-800 bg-[#0a0a0a] flex justify-between">
                    <span className="font-bold text-cyan-400">ANTIGRAVITY</span>
                    <span className="text-green-400">${portfolio ? parseFloat(portfolio.portfolio_value).toLocaleString() : '100k'}</span>
                </div>

                {/* Messages Stream */}
                <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>

                            <div className={`flex gap-3 max-w-[85%] md:max-w-[70%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                                {/* Avatar */}
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-cyan-900/20' : 'bg-green-900/20'
                                    }`}>
                                    {msg.role === 'user' ? <User size={14} className="text-cyan-400" /> : <Bot size={14} className="text-green-400" />}
                                </div>

                                {/* Bubble */}
                                <div className={`p-4 rounded-2xl text-sm leading-relaxed shadow-sm ${msg.role === 'user'
                                        ? 'bg-cyan-950/30 border border-cyan-900/50 text-cyan-100 rounded-tr-none'
                                        : 'bg-[#111] border border-gray-800 text-gray-300 rounded-tl-none'
                                    }`}>

                                    {/* Text Message */}
                                    {msg.type === 'text' && <p className="whitespace-pre-wrap">{msg.content}</p>}

                                    {/* Trade Confirmation Card */}
                                    {msg.type === 'trade_card' && msg.details && (
                                        <div className="mt-1">
                                            <div className="flex items-center gap-2 mb-2 text-green-400 font-bold border-b border-gray-700 pb-2">
                                                <TrendingUp size={16} /> ORDER EXECUTED
                                            </div>
                                            <div className="grid grid-cols-2 gap-4 font-mono text-xs">
                                                <div>
                                                    <span className="text-gray-500 block">SYMBOL</span>
                                                    <span className="text-white text-lg">{msg.details.symbol}</span>
                                                </div>
                                                <div>
                                                    <span className="text-gray-500 block">SIDE</span>
                                                    <span className={`text-lg ${msg.details.side === 'buy' ? 'text-green-400' : 'text-red-400'} uppercase`}>
                                                        {msg.details.side}
                                                    </span>
                                                </div>
                                                <div>
                                                    <span className="text-gray-500 block">QTY</span>
                                                    <span className="text-white">{msg.details.qty}</span>
                                                </div>
                                                <div>
                                                    <span className="text-gray-500 block">ORDER ID</span>
                                                    <span className="text-gray-600 text-[10px] truncate block w-24">{msg.details.order_id}</span>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Error Message */}
                                    {msg.type === 'error' && <p className="text-red-400">{msg.content}</p>}

                                </div>
                            </div>
                        </div>
                    ))}

                    {loading && (
                        <div className="flex gap-3">
                            <div className="w-8 h-8 rounded-full bg-green-900/20 flex items-center justify-center">
                                <Bot size={14} className="text-green-400" />
                            </div>
                            <div className="flex items-center gap-1 h-8">
                                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style={{ animationDelay: '75ms' }}></div>
                                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 md:p-6 bg-[#0a0a0a] border-t border-gray-800">
                    <div className="relative max-w-4xl mx-auto">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            placeholder="Ask Sentinel to trade, analyze, or set rules..."
                            className="w-full bg-[#151515] text-white border border-gray-800 rounded-xl py-4 pl-6 pr-14 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all shadow-inner"
                        />
                        <button
                            onClick={handleSend}
                            disabled={loading}
                            className="absolute right-3 top-3 p-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Send size={18} />
                        </button>
                    </div>
                    <p className="text-center text-[10px] text-gray-600 mt-2">
                        Powered by Dual-Core AI (Groq + Gemini). Zero-Cost Infrastructure.
                    </p>
                </div>
            </div>
        </div>
    );
}
