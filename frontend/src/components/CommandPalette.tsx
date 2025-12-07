"use client";
import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
    Search, Command, Home, BarChart3, Newspaper,
    Settings, TrendingUp, Zap, X
} from 'lucide-react';

interface CommandItem {
    id: string;
    label: string;
    icon: React.ReactNode;
    action: () => void;
    shortcut?: string;
    category: 'navigation' | 'actions' | 'assets';
}

interface CommandPaletteProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
    const router = useRouter();
    const [search, setSearch] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);

    const commands: CommandItem[] = [
        // Navigation
        { id: 'dashboard', label: 'Dashboard', icon: <Home size={16} />, action: () => router.push('/'), shortcut: '⌘D', category: 'navigation' },
        { id: 'news', label: 'News Hub', icon: <Newspaper size={16} />, action: () => router.push('/news'), shortcut: '⌘N', category: 'navigation' },
        { id: 'signals', label: 'Signal Deck', icon: <Zap size={16} />, action: () => router.push('/signals'), shortcut: '⌘S', category: 'navigation' },
        { id: 'settings', label: 'Settings', icon: <Settings size={16} />, action: () => router.push('/settings'), shortcut: '⌘,', category: 'navigation' },
        // Assets
        { id: 'spy', label: 'SPY - S&P 500 ETF', icon: <TrendingUp size={16} />, action: () => { }, category: 'assets' },
        { id: 'btc', label: 'BTC - Bitcoin', icon: <TrendingUp size={16} />, action: () => { }, category: 'assets' },
        { id: 'qqq', label: 'QQQ - Nasdaq ETF', icon: <TrendingUp size={16} />, action: () => { }, category: 'assets' },
        { id: 'aapl', label: 'AAPL - Apple Inc.', icon: <TrendingUp size={16} />, action: () => { }, category: 'assets' },
    ];

    const filteredCommands = commands.filter(cmd =>
        cmd.label.toLowerCase().includes(search.toLowerCase())
    );

    const handleKeyDown = useCallback((e: KeyboardEvent) => {
        if (!isOpen) return;

        if (e.key === 'Escape') {
            onClose();
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedIndex(prev => Math.min(prev + 1, filteredCommands.length - 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex(prev => Math.max(prev - 1, 0));
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (filteredCommands[selectedIndex]) {
                filteredCommands[selectedIndex].action();
                onClose();
            }
        }
    }, [isOpen, onClose, filteredCommands, selectedIndex]);

    useEffect(() => {
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown]);

    useEffect(() => {
        setSelectedIndex(0);
    }, [search]);

    if (!isOpen) return null;

    const categories = {
        navigation: 'Navigation',
        actions: 'Actions',
        assets: 'Assets'
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh]">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-void/80 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative w-full max-w-xl mx-4 bg-obsidian border border-white/10 rounded-2xl shadow-2xl shadow-neon-cyan/10 overflow-hidden animate-fade-in">
                {/* Search Input */}
                <div className="flex items-center gap-3 p-4 border-b border-white/10">
                    <Search size={20} className="text-gray-500" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Type a command or search..."
                        className="flex-1 bg-transparent text-white placeholder-gray-500 outline-none text-sm"
                        autoFocus
                    />
                    <kbd className="px-2 py-1 text-[10px] bg-white/5 rounded border border-white/10 text-gray-400">
                        ESC
                    </kbd>
                </div>

                {/* Results */}
                <div className="max-h-[300px] overflow-y-auto p-2">
                    {Object.entries(categories).map(([key, label]) => {
                        const items = filteredCommands.filter(cmd => cmd.category === key);
                        if (items.length === 0) return null;

                        return (
                            <div key={key} className="mb-2">
                                <div className="px-3 py-2 text-[10px] text-gray-500 uppercase tracking-wider">
                                    {label}
                                </div>
                                {items.map((cmd, index) => {
                                    const globalIndex = filteredCommands.indexOf(cmd);
                                    return (
                                        <button
                                            key={cmd.id}
                                            onClick={() => { cmd.action(); onClose(); }}
                                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${globalIndex === selectedIndex
                                                    ? 'bg-neon-cyan/10 border border-neon-cyan/30'
                                                    : 'hover:bg-white/5'
                                                }`}
                                        >
                                            <span className="text-gray-400">{cmd.icon}</span>
                                            <span className="flex-1 text-left text-sm text-white">{cmd.label}</span>
                                            {cmd.shortcut && (
                                                <kbd className="px-2 py-1 text-[10px] bg-white/5 rounded text-gray-500">
                                                    {cmd.shortcut}
                                                </kbd>
                                            )}
                                        </button>
                                    );
                                })}
                            </div>
                        );
                    })}

                    {filteredCommands.length === 0 && (
                        <div className="py-8 text-center text-gray-500 text-sm">
                            No results found
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between px-4 py-2 border-t border-white/10 text-[10px] text-gray-500">
                    <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1">
                            <kbd className="px-1 bg-white/5 rounded">↵</kbd> Select
                        </span>
                        <span className="flex items-center gap-1">
                            <kbd className="px-1 bg-white/5 rounded">↑↓</kbd> Navigate
                        </span>
                    </div>
                    <div className="flex items-center gap-1">
                        <Command size={10} />
                        <span>Axiom Antigravity</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
