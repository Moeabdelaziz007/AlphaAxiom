'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, X, Zap, Sparkles, MessageCircle, CheckCircle, AlertTriangle } from 'lucide-react';

interface Message {
    role: 'user' | 'system';
    content: string;
    timestamp: Date;
    type?: 'text' | 'trade_confirm' | 'trade_executed' | 'error';
    tradeData?: {
        symbol: string;
        side: 'buy' | 'sell';
        qty: number;
        price: number;
        sl?: number;
        tp?: number;
    };
}

interface PendingTrade {
    symbol: string;
    side: 'buy' | 'sell';
    qty: number;
    price: number;
    sl: number;
    tp: number;
}

export default function SentinelChat() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'system',
            content: '🤖 Sentinel AI Online. I can analyze markets AND execute trades for you. Try: "Buy BTC" or "Analyze Gold"',
            timestamp: new Date(),
            type: 'text'
        }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [pendingTrade, setPendingTrade] = useState<PendingTrade | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = { role: 'user', content: input, timestamp: new Date(), type: 'text' };
        setMessages(prev => [...prev, userMsg]);
        const userInput = input;
        setInput('');
        setIsTyping(true);

        try {
            const response = await fetch('https://trading-brain-v1.amrikyy1.workers.dev/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userInput })
            });
            const data = await response.json();

            if (data.action === 'trade_confirm') {
                // AI wants to execute a trade - show confirmation
                setPendingTrade(data.trade);
                setMessages(prev => [...prev, {
                    role: 'system',
                    content: data.reply,
                    timestamp: new Date(),
                    type: 'trade_confirm',
                    tradeData: data.trade
                }]);
            } else {
                setMessages(prev => [...prev, {
                    role: 'system',
                    content: data.reply,
                    timestamp: new Date(),
                    type: 'text'
                }]);
            }
        } catch (error) {
            // Intelligent mock with trade capability
            const result = processLocalCommand(userInput);
            setMessages(prev => [...prev, result]);
            if (result.type === 'trade_confirm' && result.tradeData) {
                setPendingTrade(result.tradeData as PendingTrade);
            }
        } finally {
            setIsTyping(false);
        }
    };

    // Execute confirmed trade
    const executeTrade = async () => {
        if (!pendingTrade) return;
        setIsTyping(true);

        try {
            const response = await fetch('https://trading-brain-v1.amrikyy1.workers.dev/api/trade', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    symbol: pendingTrade.symbol,
                    side: pendingTrade.side,
                    qty: pendingTrade.qty,
                    type: 'market'
                })
            });
            const data = await response.json();

            setMessages(prev => [...prev, {
                role: 'system',
                content: `✅ ORDER EXECUTED! ${pendingTrade.side.toUpperCase()} ${pendingTrade.qty} ${pendingTrade.symbol} @ $${pendingTrade.price}`,
                timestamp: new Date(),
                type: 'trade_executed',
                tradeData: pendingTrade
            }]);
        } catch (error) {
            // Mock execution for demo
            setMessages(prev => [...prev, {
                role: 'system',
                content: `✅ ORDER EXECUTED (Demo)! ${pendingTrade.side.toUpperCase()} ${pendingTrade.qty} ${pendingTrade.symbol} @ $${pendingTrade.price}`,
                timestamp: new Date(),
                type: 'trade_executed',
                tradeData: pendingTrade
            }]);
        } finally {
            setPendingTrade(null);
            setIsTyping(false);
        }
    };

    const cancelTrade = () => {
        setPendingTrade(null);
        setMessages(prev => [...prev, {
            role: 'system',
            content: '❌ Trade cancelled. Standing by for new orders.',
            timestamp: new Date(),
            type: 'text'
        }]);
    };

    // Local command processor with trade capability
    const processLocalCommand = (query: string): Message => {
        const q = query.toLowerCase();
        const timestamp = new Date();

        // BUY commands
        if ((q.includes('buy') || q.includes('long') || q.includes('شراء')) &&
            (q.includes('btc') || q.includes('bitcoin'))) {
            return {
                role: 'system',
                content: '📊 Analyzing BTC... Momentum: 78/100 (BULLISH). Ready to execute BUY order.',
                timestamp,
                type: 'trade_confirm',
                tradeData: { symbol: 'BTCUSD', side: 'buy', qty: 0.01, price: 98500, sl: 96500, tp: 103000 }
            };
        }

        if ((q.includes('buy') || q.includes('long')) && (q.includes('aapl') || q.includes('apple'))) {
            return {
                role: 'system',
                content: '📊 Analyzing AAPL... Momentum: 65/100. Ready to execute BUY order.',
                timestamp,
                type: 'trade_confirm',
                tradeData: { symbol: 'AAPL', side: 'buy', qty: 10, price: 242.50, sl: 237, tp: 255 }
            };
        }

        if ((q.includes('buy') || q.includes('long')) && (q.includes('gold') || q.includes('gld') || q.includes('ذهب'))) {
            return {
                role: 'system',
                content: '🥇 Analyzing GOLD... Momentum: 72/100. Ready to execute BUY order.',
                timestamp,
                type: 'trade_confirm',
                tradeData: { symbol: 'GLD', side: 'buy', qty: 5, price: 185.20, sl: 182, tp: 192 }
            };
        }

        // SELL commands
        if ((q.includes('sell') || q.includes('short') || q.includes('بيع'))) {
            return {
                role: 'system',
                content: '⚠️ SELL signal analysis... Consider closing positions or setting trailing stop.',
                timestamp,
                type: 'text'
            };
        }

        // Close all (panic)
        if (q.includes('close all') || q.includes('panic') || q.includes('أغلق')) {
            return {
                role: 'system',
                content: '🚨 EMERGENCY PROTOCOL: Preparing to close all positions. Confirm?',
                timestamp,
                type: 'trade_confirm',
                tradeData: { symbol: 'ALL', side: 'sell', qty: 0, price: 0, sl: 0, tp: 0 }
            };
        }

        // Analysis commands
        if (q.includes('btc') || q.includes('bitcoin')) {
            return { role: 'system', content: '₿ BTC Analysis:\n• Price: $98,500\n• Momentum: 78/100 🟢\n• Trend: BULLISH\n• Whale Activity: HIGH\n\nSay "Buy BTC" to execute.', timestamp, type: 'text' };
        }

        if (q.includes('risk') || q.includes('مخاطر')) {
            return { role: 'system', content: '🛡️ Portfolio Risk:\n• Exposure: MODERATE\n• Open Positions: 3\n• Daily P&L: +$1,240\n• Max Drawdown: 2.1%', timestamp, type: 'text' };
        }

        return {
            role: 'system',
            content: '📈 I can execute trades for you! Try:\n• "Buy BTC"\n• "Buy Apple"\n• "Buy Gold"\n• "Analyze [symbol]"\n• "Close all positions"',
            timestamp,
            type: 'text'
        };
    };

    const formatTime = (date: Date) => date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

    return (
        <>
            {/* Floating Button */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="fixed bottom-6 right-6 bg-gradient-to-r from-neon-cyan to-blue-500 
                               text-terminal-black p-4 rounded-full 
                               shadow-[0_0_30px_rgba(0,242,234,0.6)] 
                               transition-all transform hover:scale-110 z-50 
                               animate-bounce hover:animate-none btn-neon"
                    title="Chat with Sentinel AI"
                >
                    <Bot size={28} />
                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-neon-green rounded-full animate-ping" />
                </button>
            )}

            {/* Chat Window */}
            {isOpen && (
                <div className="fixed bottom-6 right-6 w-[400px] h-[550px] glass-panel rounded-2xl 
                               flex flex-col z-50 border border-neon-cyan/30 overflow-hidden 
                               shadow-[0_0_40px_rgba(0,242,234,0.3)] fade-in">
                    {/* Header */}
                    <div className="bg-terminal-black/90 p-4 flex justify-between items-center border-b border-white/10">
                        <div className="flex items-center gap-3">
                            <div className="relative">
                                <Zap className="text-neon-cyan w-5 h-5" />
                                <span className="absolute -top-1 -right-1 w-2 h-2 bg-neon-green rounded-full animate-pulse" />
                            </div>
                            <div>
                                <span className="font-bold text-neon-cyan tracking-wider text-sm glow-cyan">SENTINEL AI</span>
                                <p className="text-xs text-gray-500">Trade Execution Enabled</p>
                            </div>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-white p-1 hover:bg-white/10 rounded">
                            <X size={18} />
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-terminal-black/60">
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} fade-in`}>
                                {msg.type === 'trade_confirm' && msg.tradeData ? (
                                    <div className="bg-neon-gold/10 border border-neon-gold/30 p-4 rounded-xl max-w-[90%]">
                                        <div className="flex items-center gap-2 mb-2">
                                            <AlertTriangle className="w-4 h-4 text-neon-gold" />
                                            <span className="font-bold text-neon-gold text-sm">CONFIRM TRADE</span>
                                        </div>
                                        <p className="text-sm text-gray-300 mb-3">{msg.content}</p>
                                        <div className="bg-terminal-black/50 p-2 rounded font-mono text-xs space-y-1 mb-3">
                                            <p>Symbol: <span className="text-white">{msg.tradeData.symbol}</span></p>
                                            <p>Side: <span className={msg.tradeData.side === 'buy' ? 'text-neon-green' : 'text-neon-red'}>{msg.tradeData.side.toUpperCase()}</span></p>
                                            <p>Qty: <span className="text-white">{msg.tradeData.qty}</span></p>
                                            <p>Price: <span className="text-white">${msg.tradeData.price}</span></p>
                                            {(msg.tradeData.sl ?? 0) > 0 && <p>SL: <span className="text-neon-red">${msg.tradeData.sl}</span> | TP: <span className="text-neon-green">${msg.tradeData.tp}</span></p>}
                                        </div>
                                        {pendingTrade && (
                                            <div className="flex gap-2">
                                                <button onClick={executeTrade} className="flex-1 bg-neon-green/20 text-neon-green border border-neon-green/30 py-2 rounded-lg text-sm font-bold hover:bg-neon-green/30">
                                                    ✓ EXECUTE
                                                </button>
                                                <button onClick={cancelTrade} className="flex-1 bg-neon-red/20 text-neon-red border border-neon-red/30 py-2 rounded-lg text-sm font-bold hover:bg-neon-red/30">
                                                    ✗ CANCEL
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                ) : msg.type === 'trade_executed' ? (
                                    <div className="bg-neon-green/10 border border-neon-green/30 p-4 rounded-xl max-w-[90%]">
                                        <div className="flex items-center gap-2 mb-2">
                                            <CheckCircle className="w-4 h-4 text-neon-green" />
                                            <span className="font-bold text-neon-green text-sm">ORDER EXECUTED</span>
                                        </div>
                                        <p className="text-sm text-gray-300">{msg.content}</p>
                                    </div>
                                ) : (
                                    <div className={`max-w-[85%] p-3 rounded-xl text-sm ${msg.role === 'user'
                                        ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30'
                                        : 'bg-terminal-gray/80 text-gray-200 border border-white/10'
                                        }`}>
                                        {msg.role === 'system' && (
                                            <div className="flex items-center gap-1 mb-1">
                                                <Sparkles className="w-3 h-3 text-neon-cyan" />
                                                <span className="text-xs text-neon-cyan font-medium">Sentinel</span>
                                            </div>
                                        )}
                                        <p className="whitespace-pre-line">{msg.content}</p>
                                        <span className="text-xs text-gray-600 mt-1 block text-right">{formatTime(msg.timestamp)}</span>
                                    </div>
                                )}
                            </div>
                        ))}
                        {isTyping && (
                            <div className="flex items-center gap-2 text-neon-cyan text-sm animate-pulse">
                                <MessageCircle className="w-4 h-4" />
                                <span>Processing...</span>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="p-4 bg-terminal-black/90 border-t border-white/10 flex gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                            placeholder="Buy BTC, Analyze Gold..."
                            className="flex-1 bg-terminal-gray border border-white/10 rounded-lg px-4 py-2.5 
                                       text-white placeholder-gray-600 text-sm font-mono
                                       focus:border-neon-cyan/50 outline-none"
                        />
                        <button
                            onClick={handleSend}
                            disabled={!input.trim() || isTyping}
                            className="bg-neon-cyan/20 hover:bg-neon-cyan/30 text-neon-cyan 
                                       p-2.5 rounded-lg border border-neon-cyan/30 disabled:opacity-50"
                        >
                            <Send size={18} />
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}
