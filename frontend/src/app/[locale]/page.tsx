'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Bell, Crown, Brain, TrendingUp } from 'lucide-react';

// Use canonical component locations
import { SpiderBrainStatus } from './dashboard-v2/components/SpiderBrainStatus';
import { TwinTurboGauges } from './dashboard-v2/components/TwinTurboGauges';
import { AutonomousSwarm } from './dashboard-v2/components/AutonomousSwarm';
import { ExecutionDeck } from './dashboard-v2/components/ExecutionDeck';
import { PaymentModal } from './dashboard-v2/components/PaymentModal';
import { usePortfolio } from './dashboard-v2/hooks/usePortfolio';

// Import existing dialectic components
import { DialecticWarRoom } from '@/components/dialectic/DialecticWarRoom';
import { EvolutionaryOptimization } from '@/components/dialectic/EvolutionaryOptimization';
import { ResilienceMonitor } from '@/components/dialectic/ResilienceMonitor';
import { StrategyEngine } from '@/components/dialectic/StrategyEngine';

export default function HomePage() {
    const [showPaymentModal, setShowPaymentModal] = useState(false);
    const { portfolio } = usePortfolio();

    return (
        <div className="min-h-screen bg-[#050505]">
            {/* Top Navigation - New Citadel Edition */}
            <nav className="sticky top-0 z-40 bg-[#0A0A1A]/80 backdrop-blur-xl border-b border-white/10">
                <div className="max-w-[1920px] mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        {/* Logo */}
                        <div className="flex items-center gap-2">
                            <Brain className="w-8 h-8 text-[#00FFFF]" />
                            <div>
                                <h1 className="text-xl font-mono font-bold text-white tracking-tight">
                                    AXIOM ANTIGRAVITY
                                </h1>
                                <p className="text-xs text-gray-400 font-mono">
                                    v1.2 Citadel Edition
                                </p>
                            </div>
                        </div>

                        {/* Center - Status */}
                        <div className="hidden lg:flex items-center gap-2 px-4 py-2 bg-[#22C55E]/10 border border-[#22C55E]/30 rounded-lg">
                            <div className="w-2 h-2 rounded-full bg-[#22C55E] animate-pulse"></div>
                            <span className="text-sm font-mono text-[#22C55E] font-bold">
                                MAINNET: 7/7 Agents Online
                            </span>
                        </div>

                        {/* Right - Actions */}
                        <div className="flex items-center gap-4">
                            <button className="p-2 hover:bg-white/5 rounded-lg transition-colors">
                                <Search className="w-5 h-5 text-gray-400" />
                            </button>
                            <button className="p-2 hover:bg-white/5 rounded-lg transition-colors relative">
                                <Bell className="w-5 h-5 text-gray-400" />
                                <span className="absolute top-1 right-1 w-2 h-2 bg-[#EF4444] rounded-full"></span>
                            </button>
                            <button
                                onClick={() => setShowPaymentModal(true)}
                                className="flex items-center gap-2 px-4 py-2 bg-[#FFD700]/10 border border-[#FFD700]/30 rounded-lg hover:bg-[#FFD700]/20 transition-all"
                            >
                                <Crown className="w-4 h-4 text-[#FFD700]" />
                                <span className="text-sm font-mono text-[#FFD700] font-bold">
                                    UPGRADE
                                </span>
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-[1920px] mx-auto px-6 py-6 space-y-6">
                {/* Spider Web Brain Status */}
                <SpiderBrainStatus />

                {/* Top Stats Row */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Bot Scores */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-[#0A0A1A]/50 backdrop-blur-xl border border-white/10 rounded-xl p-6"
                    >
                        <h3 className="text-sm font-mono text-gray-400 mb-4">BOT_SCORES</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between items-center">
                                <span className="text-xs font-mono text-gray-500">PnL Today</span>
                                <span className={`text-lg font-mono font-bold ${portfolio.todayPnL >= 0 ? 'text-[#22C55E]' : 'text-[#EF4444]'}`}>
                                    {portfolio.todayPnL >= 0 ? '+' : ''}{portfolio.todayPnL.toFixed(2)}
                                </span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-xs font-mono text-gray-500">Win Rate</span>
                                <span className="text-lg font-mono font-bold text-[#00FFFF]">
                                    {portfolio.winRate}%
                                </span>
                            </div>
                        </div>
                    </motion.div>

                    {/* Main Chart Placeholder */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="bg-[#0A0A1A]/50 backdrop-blur-xl border border-white/10 rounded-xl p-6 flex items-center justify-center"
                    >
                        <div className="text-center">
                            <TrendingUp className="w-12 h-12 text-[#00FFFF] mx-auto mb-2" />
                            <p className="text-sm font-mono text-gray-400">MAIN_CHART</p>
                            <p className="text-xs font-mono text-gray-600 mt-1">TradingView Integration</p>
                        </div>
                    </motion.div>

                    {/* Portfolio */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="bg-[#0A0A1A]/50 backdrop-blur-xl border border-white/10 rounded-xl p-6"
                    >
                        <h3 className="text-sm font-mono text-gray-400 mb-4">PORTFOLIO</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between items-center">
                                <span className="text-xs font-mono text-gray-500">Balance</span>
                                <span className="text-lg font-mono font-bold text-white">
                                    ${portfolio.balance.toLocaleString()}
                                </span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-xs font-mono text-gray-500">Positions</span>
                                <span className="text-lg font-mono font-bold text-[#00FFFF]">
                                    {portfolio.positions.length}
                                </span>
                            </div>
                        </div>
                    </motion.div>
                </div>

                {/* Self-Play Learning Loop */}
                <div className="bg-[#0A0A1A]/50 backdrop-blur-xl border border-white/10 rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <Brain className="w-6 h-6 text-[#A855F7]" />
                        <h2 className="text-xl font-mono font-bold text-white tracking-tight">
                            SELF_PLAY_LEARNING_LOOP
                        </h2>
                    </div>
                    <div className="space-y-6">
                        <DialecticWarRoom />
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <ResilienceMonitor />
                            <EvolutionaryOptimization />
                        </div>
                        <StrategyEngine />
                    </div>
                </div>

                {/* Twin-Turbo Engines */}
                <TwinTurboGauges />

                {/* Bottom Row */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* AI Chat Placeholder */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-[#0A0A1A]/50 backdrop-blur-xl border border-white/10 rounded-xl p-6 flex items-center justify-center"
                    >
                        <div className="text-center">
                            <Brain className="w-12 h-12 text-[#A855F7] mx-auto mb-2" />
                            <p className="text-sm font-mono text-gray-400">AI_CHAT</p>
                            <p className="text-xs font-mono text-gray-600 mt-1">GLM-4.5 Integration</p>
                        </div>
                    </motion.div>

                    {/* Execution Deck */}
                    <ExecutionDeck />

                    {/* Autonomous Swarm */}
                    <div className="lg:col-span-1">
                        <AutonomousSwarm />
                    </div>
                </div>
            </main>

            {/* Payment Modal */}
            <PaymentModal isOpen={showPaymentModal} onClose={() => setShowPaymentModal(false)} />
        </div>
    );
}
