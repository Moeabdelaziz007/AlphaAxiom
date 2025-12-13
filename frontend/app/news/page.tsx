"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    TrendingUp, TrendingDown, Minus, RefreshCw, Newspaper,
    ArrowUpRight, Zap, Globe, Activity, Radio
} from "lucide-react";

// ==========================================
// 🛠️ TYPE DEFINITIONS
// ==========================================

interface NewsItem {
    id: number;
    source: string;
    title: string;
    link?: string;
    published_at: string;
}

interface Briefing {
    summary: string;
    sentiment: "Bullish" | "Bearish" | "Neutral";
    created_at: string;
}

const WORKER_API_URL = process.env.NEXT_PUBLIC_WORKER_URL || "https://trading-brain-v1.amrikyy1.workers.dev";

// ==========================================
// 🎨 MICRO-COMPONENTS (Design System)
// ==========================================

// 🌀 Pulsing AI Orb - The "Brain" indicator
const PulsingOrb = ({ state = "idle" }: { state?: "idle" | "analyzing" | "alert" }) => {
    const colors = {
        idle: "from-cyan-500 to-blue-600",
        analyzing: "from-purple-500 to-pink-600",
        alert: "from-red-500 to-orange-600"
    };

    return (
        <div className="relative">
            <motion.div
                className={`w-12 h-12 rounded-full bg-gradient-to-br ${colors[state]} shadow-lg shadow-cyan-500/30`}
                animate={{
                    scale: [1, 1.15, 1],
                    boxShadow: [
                        "0 0 20px rgba(6, 182, 212, 0.3)",
                        "0 0 40px rgba(6, 182, 212, 0.6)",
                        "0 0 20px rgba(6, 182, 212, 0.3)"
                    ]
                }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            >
                <div className="absolute inset-0 flex items-center justify-center">
                    <Activity className="w-5 h-5 text-white/80" />
                </div>
            </motion.div>
            {/* Outer ring */}
            <motion.div
                className="absolute inset-0 rounded-full border-2 border-cyan-400/30"
                animate={{ scale: [1, 1.5], opacity: [0.6, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
            />
        </div>
    );
};

// ⚡ Glitch Text - Cyberpunk header effect
const GlitchText = ({ children, className = "" }: { children: string; className?: string }) => {
    return (
        <div className={`relative font-mono font-bold ${className}`}>
            <span className="relative z-10">{children}</span>
            <motion.span
                className="absolute top-0 left-0 text-cyan-400 opacity-80 z-0"
                animate={{ x: [-2, 2, -2], opacity: [0.8, 0.4, 0.8] }}
                transition={{ duration: 0.3, repeat: Infinity, repeatDelay: 3 }}
            >
                {children}
            </motion.span>
            <motion.span
                className="absolute top-0 left-0 text-red-400 opacity-60 z-0"
                animate={{ x: [2, -2, 2], opacity: [0.6, 0.3, 0.6] }}
                transition={{ duration: 0.3, repeat: Infinity, repeatDelay: 3.1 }}
            >
                {children}
            </motion.span>
        </div>
    );
};

// ⌨️ Typewriter Effect - AI "typing" the summary
const Typewriter = ({ text, speed = 30 }: { text: string; speed?: number }) => {
    const [displayText, setDisplayText] = useState("");
    const [isComplete, setIsComplete] = useState(false);

    useEffect(() => {
        setDisplayText("");
        setIsComplete(false);
        let i = 0;
        const interval = setInterval(() => {
            if (i < text.length) {
                setDisplayText(text.slice(0, i + 1));
                i++;
            } else {
                setIsComplete(true);
                clearInterval(interval);
            }
        }, speed);
        return () => clearInterval(interval);
    }, [text, speed]);

    return (
        <span>
            {displayText}
            {!isComplete && (
                <motion.span
                    className="inline-block w-2 h-5 bg-cyan-400 ml-1"
                    animate={{ opacity: [1, 0] }}
                    transition={{ duration: 0.5, repeat: Infinity }}
                />
            )}
        </span>
    );
};

// 🏷️ Neon Tag - Impact drivers
const NeonTag = ({ children, type = "neutral" }: { children: string; type?: "critical" | "warning" | "positive" | "neutral" }) => {
    const styles = {
        critical: "bg-red-500/20 border-red-500/50 text-red-400 shadow-red-500/20",
        warning: "bg-yellow-500/20 border-yellow-500/50 text-yellow-400 shadow-yellow-500/20",
        positive: "bg-green-500/20 border-green-500/50 text-green-400 shadow-green-500/20",
        neutral: "bg-gray-500/20 border-gray-500/50 text-gray-400 shadow-gray-500/20"
    };

    return (
        <motion.span
            className={`px-3 py-1 text-xs font-mono uppercase tracking-wider rounded-full border ${styles[type]} shadow-lg`}
            whileHover={{ scale: 1.05, boxShadow: "0 0 20px currentColor" }}
        >
            {children}
        </motion.span>
    );
};

// 📊 Glass Card - Main container with animated border
const GlassCard = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => {
    return (
        <div className={`relative rounded-2xl overflow-hidden ${className}`}>
            {/* Animated gradient border */}
            <div className="absolute inset-0 rounded-2xl p-[1px] bg-gradient-to-r from-cyan-500/50 via-purple-500/50 to-cyan-500/50 animate-gradient-x" />
            {/* Glass content */}
            <div className="relative bg-black/80 backdrop-blur-xl rounded-2xl p-6">
                {children}
            </div>
        </div>
    );
};

// ==========================================
// 🧠 MAIN COMPONENT: Intelligence Hub v2.0
// ==========================================

export default function IntelligenceHub() {
    const [news, setNews] = useState<NewsItem[]>([]);
    const [briefing, setBriefing] = useState<Briefing | null>(null);
    const [loading, setLoading] = useState(true);
    const [orbState, setOrbState] = useState<"idle" | "analyzing" | "alert">("idle");

    const fetchData = useCallback(async () => {
        setOrbState("analyzing");
        try {
            const [briefRes, newsRes] = await Promise.all([
                fetch(`${WORKER_API_URL}/api/briefing/latest`),
                fetch(`${WORKER_API_URL}/api/news/latest?limit=15`)
            ]);

            if (briefRes.ok) {
                const briefData = await briefRes.json();
                if (briefData.summary) setBriefing(briefData);
            }

            if (newsRes.ok) {
                const newsData = await newsRes.json();
                setNews(newsData.news || []);
            }

            setOrbState("idle");
        } catch (e) {
            console.error("Intel fetch failed:", e);
            setOrbState("alert");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
        // Auto-refresh every 5 minutes
        const interval = setInterval(fetchData, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, [fetchData]);

    const getSentimentStyle = (sentiment: string) => {
        switch (sentiment) {
            case "Bullish": return { color: "text-green-400", icon: <TrendingUp className="w-8 h-8" />, glow: "shadow-green-500/30" };
            case "Bearish": return { color: "text-red-400", icon: <TrendingDown className="w-8 h-8" />, glow: "shadow-red-500/30" };
            default: return { color: "text-gray-400", icon: <Minus className="w-8 h-8" />, glow: "shadow-gray-500/30" };
        }
    };

    // Market Drivers (would be dynamic from AI in production)
    const marketDrivers = [
        { label: "FED_RATES", type: "warning" as const },
        { label: "BTC_HALVING", type: "positive" as const },
        { label: "CHINA_STIMULUS", type: "critical" as const },
        { label: "AI_SECTOR", type: "positive" as const },
    ];

    if (loading) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <div className="text-center space-y-4">
                    <PulsingOrb state="analyzing" />
                    <motion.p
                        className="text-cyan-400 font-mono text-sm"
                        animate={{ opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                    >
                        INITIALIZING QUANTUM UPLINK...
                    </motion.p>
                </div>
            </div>
        );
    }

    const sentimentStyle = briefing ? getSentimentStyle(briefing.sentiment) : getSentimentStyle("Neutral");

    return (
        <div className="min-h-screen bg-black text-gray-200 font-mono p-4 md:p-8">

            {/* Animated Background Grid */}
            <div className="fixed inset-0 opacity-10 pointer-events-none">
                <div className="absolute inset-0" style={{
                    backgroundImage: `
            linear-gradient(rgba(6, 182, 212, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(6, 182, 212, 0.1) 1px, transparent 1px)
          `,
                    backgroundSize: '50px 50px'
                }} />
            </div>

            <div className="relative z-10 max-w-7xl mx-auto space-y-8">

                {/* ============ HEADER ============ */}
                <motion.div
                    className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-cyan-500/20 pb-6"
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <div className="flex items-center gap-4">
                        <PulsingOrb state={orbState} />
                        <div>
                            <GlitchText className="text-xl md:text-2xl text-white">
                                PERPLEXITY_CORE // INTELLIGENCE_HUB
                            </GlitchText>
                            <p className="text-xs text-gray-500 mt-1 flex items-center gap-2">
                                <Radio className="w-3 h-3 text-cyan-500" />
                                QUANTUM MARKET ANALYSIS SYSTEM v2.0
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <motion.button
                            onClick={fetchData}
                            className="px-4 py-2 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-400 text-xs flex items-center gap-2 hover:bg-cyan-500/20 transition-colors"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                        >
                            <RefreshCw className="w-4 h-4" /> SYNC
                        </motion.button>
                        <div className="text-xs text-gray-600 flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                            ONLINE
                        </div>
                    </div>
                </motion.div>

                {/* ============ AI BRIEFING CARD ============ */}
                <GlassCard className="relative">
                    {/* Sentiment Indicator Glow */}
                    {briefing && (
                        <div className={`absolute -top-20 -right-20 w-40 h-40 rounded-full blur-3xl opacity-20 ${briefing.sentiment === "Bullish" ? "bg-green-500" :
                                briefing.sentiment === "Bearish" ? "bg-red-500" : "bg-gray-500"
                            }`} />
                    )}

                    <div className="relative z-10">
                        {/* Header */}
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center gap-3">
                                <Zap className="w-5 h-5 text-yellow-400" />
                                <span className="text-xs text-gray-400 uppercase tracking-widest">Daily Executive Briefing</span>
                            </div>
                            {briefing && (
                                <motion.div
                                    className={`flex items-center gap-2 px-4 py-2 rounded-full ${sentimentStyle.glow} shadow-lg border border-white/10`}
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    transition={{ type: "spring", stiffness: 200 }}
                                >
                                    {sentimentStyle.icon}
                                    <span className={`text-lg font-bold ${sentimentStyle.color}`}>
                                        {briefing.sentiment.toUpperCase()}
                                    </span>
                                </motion.div>
                            )}
                        </div>

                        {/* AI Summary with Typewriter */}
                        <div className="min-h-[120px] text-lg md:text-xl leading-relaxed text-gray-300">
                            {briefing ? (
                                <Typewriter text={briefing.summary} speed={25} />
                            ) : (
                                <div className="text-gray-500 text-center py-8">
                                    <Globe className="w-12 h-12 mx-auto mb-4 opacity-50" />
                                    <p>Awaiting AI Analysis...</p>
                                    <p className="text-xs mt-2">Daily briefing generates at 08:00 Cairo Time</p>
                                </div>
                            )}
                        </div>

                        {/* Impact Tags */}
                        <div className="flex flex-wrap gap-2 mt-6 pt-6 border-t border-white/5">
                            <span className="text-xs text-gray-500 mr-2">MARKET DRIVERS:</span>
                            {marketDrivers.map((driver, i) => (
                                <NeonTag key={i} type={driver.type}>{driver.label}</NeonTag>
                            ))}
                        </div>

                        {briefing && (
                            <div className="mt-4 text-xs text-gray-600 flex items-center gap-2">
                                <span className="w-1 h-1 rounded-full bg-cyan-500" />
                                Generated by Perplexity Sonar • {new Date(briefing.created_at).toLocaleString()}
                            </div>
                        )}
                    </div>
                </GlassCard>

                {/* ============ NEWS FEED ============ */}
                <div>
                    <div className="flex items-center gap-3 mb-6">
                        <Newspaper className="w-5 h-5 text-cyan-400" />
                        <h2 className="text-lg font-bold text-white">RAW_DATA_STREAM</h2>
                        <span className="text-xs text-gray-500">({news.length} SIGNALS)</span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <AnimatePresence mode="popLayout">
                            {news.map((item, index) => (
                                <motion.a
                                    key={item.id}
                                    href={item.link || "#"}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="group block p-4 rounded-xl bg-gray-900/50 border border-gray-800 hover:border-cyan-500/50 hover:bg-gray-900/80 transition-all"
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                    whileHover={{ scale: 1.02, y: -2 }}
                                >
                                    <div className="flex justify-between items-start mb-2">
                                        <span className="text-xs text-cyan-500 font-bold bg-cyan-950/40 px-2 py-0.5 rounded">
                                            {item.source}
                                        </span>
                                        <span className="text-xs text-gray-600">
                                            {new Date(item.published_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </span>
                                    </div>
                                    <h3 className="text-sm font-medium text-gray-300 group-hover:text-white line-clamp-2">
                                        {item.title}
                                    </h3>
                                    <div className="mt-3 flex justify-end">
                                        <ArrowUpRight size={14} className="text-gray-600 group-hover:text-cyan-400 transition-colors" />
                                    </div>
                                </motion.a>
                            ))}
                        </AnimatePresence>
                    </div>
                </div>

            </div>

            {/* Custom CSS for gradient animation */}
            <style jsx global>{`
        @keyframes gradient-x {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        .animate-gradient-x {
          background-size: 200% 200%;
          animation: gradient-x 3s ease infinite;
        }
      `}</style>
        </div>
    );
}
