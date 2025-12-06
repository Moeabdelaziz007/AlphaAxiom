'use client';

import React, { useState } from 'react';
import { ShoppingCart, TrendingUp, TrendingDown, AlertTriangle, DollarSign, Target, Shield } from 'lucide-react';
import { tradingApi } from '@/lib/api';

interface OrderPanelProps {
    selectedSymbol: string;
    currentPrice: number;
}

export default function OrderPanel({ selectedSymbol, currentPrice }: OrderPanelProps) {
    const [orderType, setOrderType] = useState<'market' | 'limit'>('market');
    const [side, setSide] = useState<'buy' | 'sell'>('buy');
    const [quantity, setQuantity] = useState('1');
    const [limitPrice, setLimitPrice] = useState('');
    const [stopLoss, setStopLoss] = useState('');
    const [takeProfit, setTakeProfit] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    const displayPrice = currentPrice > 0 ? currentPrice : 100.00;
    const orderValue = parseFloat(quantity) * displayPrice;

    const handleSubmit = async () => {
        setIsSubmitting(true);
        setMessage(null);

        try {
            const orderData = {
                symbol: selectedSymbol.replace('/', ''),
                side: side,
                type: orderType,
                qty: parseFloat(quantity),
                limit_price: orderType === 'limit' ? parseFloat(limitPrice) : undefined,
            };

            const response = await tradingApi.placeOrder(orderData);
            setMessage({ type: 'success', text: `Order placed: ${response.id || 'Success!'}` });
        } catch (error) {
            setMessage({ type: 'error', text: 'Order failed. Check API connection.' });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="glass-panel neon-border rounded-xl p-5 h-full flex flex-col fade-in">
            {/* Header */}
            <div className="flex items-center justify-between mb-5">
                <div className="flex items-center gap-2">
                    <ShoppingCart className="w-5 h-5 text-neon-cyan" />
                    <span className="text-sm font-bold text-neon-cyan glow-cyan">ORDER PANEL</span>
                </div>
                <span className="text-xs text-gray-500 font-mono">{selectedSymbol}</span>
            </div>

            {/* Buy/Sell Toggle */}
            <div className="grid grid-cols-2 gap-2 mb-5">
                <button
                    onClick={() => setSide('buy')}
                    className={`py-3 rounded-lg font-bold text-sm transition-all btn-neon ${side === 'buy'
                            ? 'bg-neon-green/20 text-neon-green border border-neon-green/50 shadow-[0_0_15px_rgba(0,255,157,0.3)]'
                            : 'glass-panel text-gray-500 hover:text-gray-300'
                        }`}
                >
                    <TrendingUp className="inline w-4 h-4 mr-1" />
                    BUY
                </button>
                <button
                    onClick={() => setSide('sell')}
                    className={`py-3 rounded-lg font-bold text-sm transition-all btn-neon ${side === 'sell'
                            ? 'bg-neon-red/20 text-neon-red border border-neon-red/50 shadow-[0_0_15px_rgba(255,0,85,0.3)]'
                            : 'glass-panel text-gray-500 hover:text-gray-300'
                        }`}
                >
                    <TrendingDown className="inline w-4 h-4 mr-1" />
                    SELL
                </button>
            </div>

            {/* Order Type */}
            <div className="mb-4">
                <label className="text-xs text-gray-500 block mb-2">ORDER TYPE</label>
                <div className="grid grid-cols-2 gap-2">
                    <button
                        onClick={() => setOrderType('market')}
                        className={`py-2 rounded text-xs font-medium transition-all ${orderType === 'market'
                                ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30'
                                : 'glass-panel text-gray-500'
                            }`}
                    >
                        MARKET
                    </button>
                    <button
                        onClick={() => setOrderType('limit')}
                        className={`py-2 rounded text-xs font-medium transition-all ${orderType === 'limit'
                                ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30'
                                : 'glass-panel text-gray-500'
                            }`}
                    >
                        LIMIT
                    </button>
                </div>
            </div>

            {/* Quantity */}
            <div className="mb-4">
                <label className="text-xs text-gray-500 block mb-2">
                    <DollarSign className="inline w-3 h-3 mr-1" />
                    QUANTITY
                </label>
                <input
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    className="w-full bg-terminal-gray border border-white/10 rounded-lg px-3 py-2.5 text-sm font-mono
                               focus:border-neon-cyan/50 focus:ring-1 focus:ring-neon-cyan/30 transition-all outline-none"
                    min="0.01"
                    step="0.01"
                />
            </div>

            {/* Limit Price (conditional) */}
            {orderType === 'limit' && (
                <div className="mb-4 fade-in">
                    <label className="text-xs text-gray-500 block mb-2">
                        <Target className="inline w-3 h-3 mr-1" />
                        LIMIT PRICE
                    </label>
                    <input
                        type="number"
                        value={limitPrice}
                        onChange={(e) => setLimitPrice(e.target.value)}
                        placeholder={displayPrice.toFixed(2)}
                        className="w-full bg-terminal-gray border border-white/10 rounded-lg px-3 py-2.5 text-sm font-mono
                                   focus:border-neon-cyan/50 focus:ring-1 focus:ring-neon-cyan/30 transition-all outline-none"
                    />
                </div>
            )}

            {/* Stop Loss & Take Profit */}
            <div className="grid grid-cols-2 gap-3 mb-5">
                <div>
                    <label className="text-xs text-gray-500 block mb-2">
                        <Shield className="inline w-3 h-3 mr-1 text-neon-red" />
                        STOP LOSS
                    </label>
                    <input
                        type="number"
                        value={stopLoss}
                        onChange={(e) => setStopLoss(e.target.value)}
                        placeholder="0.00"
                        className="w-full bg-terminal-gray border border-white/10 rounded-lg px-3 py-2 text-xs font-mono
                                   focus:border-neon-red/50 outline-none"
                    />
                </div>
                <div>
                    <label className="text-xs text-gray-500 block mb-2">
                        <Target className="inline w-3 h-3 mr-1 text-neon-green" />
                        TAKE PROFIT
                    </label>
                    <input
                        type="number"
                        value={takeProfit}
                        onChange={(e) => setTakeProfit(e.target.value)}
                        placeholder="0.00"
                        className="w-full bg-terminal-gray border border-white/10 rounded-lg px-3 py-2 text-xs font-mono
                                   focus:border-neon-green/50 outline-none"
                    />
                </div>
            </div>

            {/* Order Summary */}
            <div className="glass-panel-dark rounded-lg p-3 mb-5">
                <div className="flex justify-between text-xs mb-2">
                    <span className="text-gray-500">Market Price</span>
                    <span className="text-neon-cyan font-mono">${displayPrice.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-xs">
                    <span className="text-gray-500">Order Value</span>
                    <span className="text-white font-mono font-bold">${orderValue.toLocaleString()}</span>
                </div>
            </div>

            {/* Message */}
            {message && (
                <div className={`mb-4 p-3 rounded-lg text-xs fade-in ${message.type === 'success' ? 'bg-neon-green/10 text-neon-green' : 'bg-neon-red/10 text-neon-red'
                    }`}>
                    {message.text}
                </div>
            )}

            {/* Submit Button */}
            <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className={`w-full py-3 rounded-lg font-bold text-sm transition-all btn-neon ${side === 'buy'
                        ? 'bg-neon-green/20 text-neon-green border border-neon-green/50 hover:bg-neon-green/30'
                        : 'bg-neon-red/20 text-neon-red border border-neon-red/50 hover:bg-neon-red/30'
                    } ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
                {isSubmitting ? 'PROCESSING...' : `${side.toUpperCase()} ${selectedSymbol}`}
            </button>

            {/* Risk Warning */}
            <div className="mt-4 flex items-center gap-2 text-xs text-gray-600">
                <AlertTriangle className="w-3 h-3 text-neon-gold" />
                <span>Demo Mode - Paper Trading</span>
            </div>
        </div>
    );
}
