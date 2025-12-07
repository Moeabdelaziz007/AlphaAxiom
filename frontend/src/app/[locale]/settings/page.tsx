"use client";
import React, { useState } from 'react';
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
        { name: 'Groq LLM', status: 'active', desc: 'Llama 3.3 70B', icon: Bot },
        { name: 'Gemini (Analysis)', status: 'inactive', desc: 'RAG & Research', icon: Globe },
        { name: 'Telegram Bot', status: 'active', desc: '@Antigravity_bbot', icon: Bell },
    ];

    return (
        <div className="flex flex-col h-full overflow-hidden">
            <div className="p-6 border-b border-gray-800">
                <h1 className="text-2xl font-bold text-white">Settings</h1>
                <p className="text-gray-500 text-sm">Configure your trading terminal</p>
            </div>
            <div className="flex-1 overflow-y-auto p-6">
                <div className="max-w-3xl mx-auto space-y-6">
                    <div className="glass-card p-6">
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
                                            <Icon size={18} className={isActive ? 'text-emerald-400' : 'text-gray-400'} />
                                            <div>
                                                <p className="text-white font-medium">{conn.name}</p>
                                                <p className="text-xs text-gray-500">{conn.desc}</p>
                                            </div>
                                        </div>
                                        <span className={isActive ? 'text-emerald-400 text-xs' : 'text-gray-500 text-xs'}>
                                            {isActive ? 'Active' : 'Inactive'}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                    <button onClick={handleSave} className="w-full btn-primary py-4 flex items-center justify-center gap-2">
                        {saved ? <Check size={18} /> : <Save size={18} />} {saved ? 'Saved!' : 'Save Settings'}
                    </button>
                </div>
            </div>
        </div>
    );
}
