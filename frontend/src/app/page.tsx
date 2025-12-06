'use client';

import React, { useState } from 'react';
import { TrendingUp, Zap, ShieldCheck, DollarSign, AlertTriangle, Sparkles } from 'lucide-react';
import TopBar from '@/components/Dashboard/TopBar';
import MainChart from '@/components/Dashboard/MainChart';
import OrderPanel from '@/components/Dashboard/OrderPanel';
import StatCard from '@/components/Dashboard/StatCard';
import AssetSelector from '@/components/Dashboard/AssetSelector';
import SentinelAI from '@/components/Dashboard/SentinelAI';
import LivePrice from '@/components/Dashboard/LivePrice';
import MomentumGauge from '@/components/Dashboard/MomentumGauge';
import ConnectionHeartbeat from '@/components/Dashboard/ConnectionHeartbeat';
import SentinelChat from '@/components/Dashboard/SentinelChat';
import { AssetType, ASSETS } from '@/lib/types';
import { useMarketData } from '@/hooks/useMarketData';

export default function TradingDashboard() {
    const [activeAsset, setActiveAsset] = useState<AssetType>('CRYPTO');
    const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');

    // Live market data للأصل المحدد
    const { data: marketData, isConnected } = useMarketData(selectedSymbol);

    // Demo portfolio stats (يمكن ربطها بالـ API لاحقاً)
    const stats = {
        totalPnl: '+$12,450.80',
        openPositions: '3 Active',
        riskLevel: 'LOW (1.8%)',
        winRate: '67.3%',
    };

    const handleAssetChange = (asset: AssetType) => {
        setActiveAsset(asset);
        setSelectedSymbol(ASSETS[asset][0]);
    };

    return (
        <div className="min-h-screen bg-terminal-black text-gray-100 terminal-grid">
            {/* Top Navigation Bar */}
            <TopBar />

            {/* Main Content */}
            <div className="p-6 space-y-5">

                {/* Connection Heartbeat - يعطي شعور بالأمان */}
                <ConnectionHeartbeat />

                {/* Philosophy Banner - Glassmorphism */}
                <div className="glass-panel neon-border rounded-xl px-6 py-4 fade-in">
                    <p className="text-sm text-gray-300">
                        <span className="text-neon-cyan font-bold glow-cyan">
                            <Sparkles className="inline w-4 h-4 mr-1" />
                            PHILOSOPHY:
                        </span>{' '}
                        "معظم المتداولين يخسرون لأنهم يتدخلون عاطفيًا. هذا النظام يزيل العاطفة.
                        أنت تعطيه الأوامر (الخطة)، وهو ينفذها <span className="text-neon-cyan">كالجراح بدقة المليمتر</span> بناءً على الرياضيات فقط."
                    </p>
                </div>

                {/* Live Prices Row - 3 أصول رئيسية */}
                <div className="grid grid-cols-3 gap-4">
                    <LivePrice symbol="BTC/USDT" name="Bitcoin" color="cyan" />
                    <LivePrice symbol="AAPL" name="Apple Stock" color="blue" />
                    <LivePrice symbol="GLD" name="Gold ETF" color="gold" />
                </div>

                {/* Stats Row */}
                <div className="grid grid-cols-4 gap-4">
                    <StatCard
                        title="Total PNL"
                        value={stats.totalPnl}
                        icon={TrendingUp}
                        color="profit"
                        subtitle="This Month"
                    />
                    <StatCard
                        title="Open Positions"
                        value={stats.openPositions}
                        icon={Zap}
                        color="cyan"
                    />
                    <StatCard
                        title="Risk Level"
                        value={stats.riskLevel}
                        icon={ShieldCheck}
                        color="gold"
                    />
                    <StatCard
                        title="Win Rate"
                        value={stats.winRate}
                        icon={DollarSign}
                        color="blue"
                        subtitle="Last 30 Trades"
                    />
                </div>

                {/* Asset Selector */}
                <div className="flex items-center justify-between">
                    <AssetSelector
                        activeAsset={activeAsset}
                        onAssetChange={handleAssetChange}
                    />

                    {/* Symbol Selector - Glassmorphism buttons */}
                    <div className="flex gap-2">
                        {ASSETS[activeAsset].map((symbol) => (
                            <button
                                key={symbol}
                                onClick={() => setSelectedSymbol(symbol)}
                                className={`px-4 py-2 rounded-lg text-xs font-medium transition-all btn-neon ${selectedSymbol === symbol
                                    ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50 shadow-[0_0_15px_rgba(0,242,234,0.3)]'
                                    : 'glass-panel text-gray-400 hover:text-gray-200'
                                    }`}
                            >
                                {symbol}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Main Grid: Chart + Order Panel + Sentinel AI */}
                <div className="grid grid-cols-12 gap-5">
                    {/* Left: Chart + Momentum + Sentinel AI */}
                    <div className="col-span-8 space-y-5">
                        <div className="chart-container">
                            <MainChart
                                activeAsset={activeAsset}
                                selectedSymbol={selectedSymbol}
                            />
                        </div>

                        {/* Momentum Gauge - عنصر الإبهار */}
                        <MomentumGauge symbol={selectedSymbol} />

                        {/* Sentinel AI Terminal */}
                        <div className="h-[280px]">
                            <SentinelAI />
                        </div>
                    </div>

                    {/* Right: Order Panel */}
                    <div className="col-span-4">
                        <OrderPanel
                            selectedSymbol={selectedSymbol}
                            currentPrice={marketData?.price || 0}
                        />
                    </div>
                </div>

                {/* Footer */}
                <div className="glass-panel-dark rounded-xl text-center text-xs text-gray-500 py-4 mt-8">
                    <p>
                        <span className="text-neon-cyan glow-cyan">QUANTUM TRADING</span> SYSTEM v0.1 |
                        Powered by <span className="text-neon-cyan">SENTINEL AI</span> &
                        <span className="text-neon-gold"> ANTIGRAVITY</span> Algorithm
                    </p>
                    <p className="mt-2 flex items-center justify-center gap-2">
                        <AlertTriangle size={12} className="text-neon-gold" />
                        Trading involves risk. Trade responsibly.
                    </p>
                </div>
            </div>

            {/* Sentinel Chat - Floating AI Assistant */}
            <SentinelChat />
        </div>
    );
}
