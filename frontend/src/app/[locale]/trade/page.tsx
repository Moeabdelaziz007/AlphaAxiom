"use client";
import React, { useState, useEffect, useCallback } from 'react';
import { StatCard } from '@/components/SharedComponents';
import { TradingChart } from '@/components/TradingChart';
import { TradeModal } from '@/components/ui/TradeModal';
import { ArrowUp, ArrowDown, DollarSign, LineChart, CheckCircle, XCircle } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://trading-brain-v1.amrikyy.workers.dev";
const SYSTEM_KEY = process.env.NEXT_PUBLIC_SYSTEM_KEY || "";

const getHeaders = () => ({
    'Content-Type': 'application/json',
    ...(SYSTEM_KEY && { 'X-System-Key': SYSTEM_KEY })
});

export default function TradePage() {
    const [symbol, setSymbol] = useState('SPY');
    const [side, setSide] = useState<'buy' | 'sell'>('buy');
    const [qty, setQty] = useState('10');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
    const [portfolio, setPortfolio] = useState<{ buying_power: string; portfolio_value: string } | null>(null);
    const [isModalOpen, setModalOpen] = useState(false);

    const fetchPortfolio = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/account`, { headers: getHeaders() });
            if (res.ok) setPortfolio(await res.json());
        } catch (e) { console.error(e); }
    }, []);

    useEffect(() => { fetchPortfolio(); }, [fetchPortfolio]);

    const initiateTrade = () => { setResult(null); setModalOpen(true); };

    const executeTrade = async () => {
        setLoading(true);
        setResult(null);
        try {
            const res = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({ message: `${side} ${qty} ${symbol}` })
            });
            const data = await res.json();
            if (data.trade_executed?.status === 'success') {
                setResult({ type: 'success', message: `Order executed: ${side.toUpperCase()} ${qty} ${symbol}` });
                fetchPortfolio();
            } else {
                setResult({ type: 'error', message: data.trade_executed?.error || 'Order failed' });
            }
        } catch {
            setResult({ type: 'error', message: 'Trade failed' });
        }
        setLoading(false);
        setModalOpen(false);
    };

    const assets = ['SPY', 'AAPL', 'TSLA', 'GOOGL', 'NVDA', 'BTC'];

    return (
        <div className="flex h-full">
            <div className="flex-1 p-6 flex flex-col gap-4">
                <div className="flex gap-2 overflow-x-auto pb-2">
                    {assets.map((a) => (
                        <button key={a} onClick={() => setSymbol(a)}
                            className={`px-4 py-2 rounded-xl font-mono ${symbol === a ? 'bg-cyan-500/20 text-cyan-400' : 'glass-card text-gray-400'}`}>
                            {a}
                        </button>
                    ))}
                </div>
                <div className="flex-1 glass-card overflow-hidden min-h-[400px]">
                    <TradingChart symbol={symbol} timeframe="1H" />
                </div>
            </div>
            <div className="w-[340px] glass-card-strong border-l border-white/5 p-6 flex flex-col gap-5">
                <div className="grid grid-cols-2 gap-3">
                    <StatCard label="Buying Power" value={`$${portfolio ? parseFloat(portfolio.buying_power).toLocaleString() : '200K'}`} icon={DollarSign} color="green" />
                    <StatCard label="Portfolio" value={`$${portfolio ? parseFloat(portfolio.portfolio_value).toLocaleString() : '100K'}`} icon={LineChart} color="cyan" />
                </div>
                <div className="space-y-4">
                    <input type="text" value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} className="w-full bg-black/30 border border-white/5 rounded-xl py-3 px-4 font-mono" />
                    <div className="grid grid-cols-2 gap-3">
                        <button onClick={() => setSide('buy')} className={`py-3 rounded-xl font-semibold flex items-center justify-center gap-2 ${side === 'buy' ? 'bg-emerald-500/20 text-emerald-400' : 'glass-card text-gray-400'}`}>
                            <ArrowUp size={16} /> BUY
                        </button>
                        <button onClick={() => setSide('sell')} className={`py-3 rounded-xl font-semibold flex items-center justify-center gap-2 ${side === 'sell' ? 'bg-rose-500/20 text-rose-400' : 'glass-card text-gray-400'}`}>
                            <ArrowDown size={16} /> SELL
                        </button>
                    </div>
                    <input type="number" value={qty} onChange={(e) => setQty(e.target.value)} className="w-full bg-black/30 border border-white/5 rounded-xl py-3 px-4 font-mono" placeholder="Quantity" />
                    <button onClick={initiateTrade} disabled={loading || !symbol || !qty}
                        className={`w-full py-4 rounded-xl font-bold text-white flex items-center justify-center gap-2 ${side === 'buy' ? 'bg-gradient-to-r from-emerald-500 to-emerald-600' : 'bg-gradient-to-r from-rose-500 to-rose-600'} disabled:opacity-50`}>
                        {side === 'buy' ? <ArrowUp size={18} /> : <ArrowDown size={18} />} {side.toUpperCase()} {qty} {symbol}
                    </button>
                    {result && (
                        <div className={`p-4 rounded-xl border flex items-start gap-2 ${result.type === 'success' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                            {result.type === 'success' ? <CheckCircle size={16} /> : <XCircle size={16} />}
                            <p className="text-sm">{result.message}</p>
                        </div>
                    )}
                </div>
            </div>
            <TradeModal isOpen={isModalOpen} onClose={() => setModalOpen(false)} onConfirm={executeTrade} details={{ symbol, side, qty: parseInt(qty) || 0 }} loading={loading} />
        </div>
    );
}
