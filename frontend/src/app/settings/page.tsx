"use client";
import React, { useState } from 'react';
import { DashboardLayout } from '@/components/DashboardLayout';
import { Key, Bell, Shield, Globe, Palette, Save, Check, AlertTriangle, Zap, Bot, Database } from 'lucide-react';

export default function SettingsPage() {
    const [saved, setSaved] = useState(false);
    const [settings, setSettings] = useState({
        apiConnected: true,
        notifications: true,
        darkMode: true,
        autoTrade: false,
        maxTradesPerDay: 10,
        defaultQty: 10,
        telegramAlerts: true,
    });

    const handleSave = () => {
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    const connections = [
        { name: 'Alpaca (Paper Trading)', status: 'active', desc: 'Real-time data & execution', icon: Database },
        { name: 'Groq LLM', status: 'active', desc: 'Llama 3.3 70B • Router AI', icon: Bot },
        { name: 'Gemini (Analysis)', status: 'inactive', desc: 'RAG & Research', icon: Globe },
        { name: 'Telegram Bot', status: 'active', desc: '@Antigravity_bbot', icon: Bell },
    ];

    return (
        <DashboardLayout title="Settings" subtitle="Configure your trading terminal">
            <div className="p-6 max-w-3xl mx-auto">
                {/* API Connections */}
                <div className="glass-card p-6 mb-6">
                    <h2 className="font-semibold text-white mb-4 flex items-center gap-2">
                        <Key size={18} className="text-cyan-400" /> API Connections
                    </h2>
                    <div className="space-y-3">
                        {connections.map((conn) => {
                            const Icon = conn.icon;
                            const isActive = conn.status === 'active';
                            return (
                                <div key={conn.name} className="flex items-center justify-between p-4 bg-black/30 rounded-xl border border-white/5">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isActive ? 'bg-emerald-500/20' : 'bg-gray-500/20'}`}>
                                            <Icon size={18} className={isActive ? 'text-emerald-400' : 'text-gray-400'} />
                                        </div>
                                        <div>
                                            <p className="text-white font-medium">{conn.name}</p>
                                            <p className="text-xs text-gray-500">{conn.desc}</p>
                                        </div>
                                    </div>
                                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${isActive
                                            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                            : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                                        }`}>
                                        {isActive ? 'Active' : 'Inactive'}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Risk Management */}
                <div className="glass-card p-6 mb-6">
                    <h2 className="font-semibold text-white mb-4 flex items-center gap-2">
                        <Shield size={18} className="text-rose-400" /> Risk Management
                    </h2>
                    <div className="space-y-4">
                        <div>
                            <label className="text-sm text-gray-400 block mb-2">Max Trades Per Day</label>
                            <input
                                type="number"
                                value={settings.maxTradesPerDay}
                                onChange={(e) => setSettings({ ...settings, maxTradesPerDay: parseInt(e.target.value) })}
                                className="w-full bg-black/30 border border-white/5 rounded-xl py-3 px-4 outline-none focus:border-cyan-500/50 font-mono"
                            />
                            <p className="text-xs text-gray-600 mt-1 flex items-center gap-1">
                                <AlertTriangle size={12} /> Circuit breaker: stops trading after this limit
                            </p>
                        </div>

                        <div>
                            <label className="text-sm text-gray-400 block mb-2">Default Order Quantity</label>
                            <input
                                type="number"
                                value={settings.defaultQty}
                                onChange={(e) => setSettings({ ...settings, defaultQty: parseInt(e.target.value) })}
                                className="w-full bg-black/30 border border-white/5 rounded-xl py-3 px-4 outline-none focus:border-cyan-500/50 font-mono"
                            />
                        </div>

                        <div className="flex items-center justify-between p-4 bg-black/30 rounded-xl border border-white/5">
                            <div>
                                <p className="text-white font-medium flex items-center gap-2">
                                    <Zap size={16} className="text-cyan-400" /> Auto-Execute Trades
                                </p>
                                <p className="text-xs text-gray-500">Allow AI to execute trades from chat</p>
                            </div>
                            <button
                                onClick={() => setSettings({ ...settings, autoTrade: !settings.autoTrade })}
                                className={`relative w-12 h-6 rounded-full transition-colors ${settings.autoTrade ? 'bg-emerald-500/30' : 'bg-gray-700'}`}
                            >
                                <span className={`absolute top-1 w-4 h-4 rounded-full transition-all ${settings.autoTrade ? 'left-7 bg-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.5)]' : 'left-1 bg-gray-500'
                                    }`}></span>
                            </button>
                        </div>

                        <div className="flex items-center justify-between p-4 bg-black/30 rounded-xl border border-white/5">
                            <div>
                                <p className="text-white font-medium flex items-center gap-2">
                                    <Bell size={16} className="text-cyan-400" /> Telegram Alerts
                                </p>
                                <p className="text-xs text-gray-500">Receive trade notifications in Telegram</p>
                            </div>
                            <button
                                onClick={() => setSettings({ ...settings, telegramAlerts: !settings.telegramAlerts })}
                                className={`relative w-12 h-6 rounded-full transition-colors ${settings.telegramAlerts ? 'bg-cyan-500/30' : 'bg-gray-700'}`}
                            >
                                <span className={`absolute top-1 w-4 h-4 rounded-full transition-all ${settings.telegramAlerts ? 'left-7 bg-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.5)]' : 'left-1 bg-gray-500'
                                    }`}></span>
                            </button>
                        </div>
                    </div>
                </div>

                {/* Appearance */}
                <div className="glass-card p-6 mb-6">
                    <h2 className="font-semibold text-white mb-4 flex items-center gap-2">
                        <Palette size={18} className="text-purple-400" /> Appearance
                    </h2>
                    <div className="flex items-center justify-between p-4 bg-black/30 rounded-xl border border-white/5">
                        <div>
                            <p className="text-white font-medium">Dark Mode</p>
                            <p className="text-xs text-gray-500">Midnight Protocol Theme</p>
                        </div>
                        <button
                            onClick={() => setSettings({ ...settings, darkMode: !settings.darkMode })}
                            className={`relative w-12 h-6 rounded-full transition-colors ${settings.darkMode ? 'bg-cyan-500/30' : 'bg-gray-700'}`}
                        >
                            <span className={`absolute top-1 w-4 h-4 rounded-full transition-all ${settings.darkMode ? 'left-7 bg-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.5)]' : 'left-1 bg-gray-500'
                                }`}></span>
                        </button>
                    </div>
                </div>

                {/* Save Button */}
                <button
                    onClick={handleSave}
                    className="w-full btn-primary py-4 flex items-center justify-center gap-2"
                >
                    {saved ? <><Check size={18} /> Saved!</> : <><Save size={18} /> Save Settings</>}
                </button>
            </div>
        </DashboardLayout>
    );
}
