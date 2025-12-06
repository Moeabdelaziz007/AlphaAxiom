'use client';

import { useState, useEffect, useRef } from 'react';

const API_BASE = 'https://trading-brain-v1.amrikyy1.workers.dev';

export interface MarketData {
    symbol: string;
    price: number;
    change: number;
    change_percent: number;
    high: number;
    low: number;
    volume: number;
    asset_type: string;
    timestamp: string;
}

export type Trend = 'UP' | 'DOWN' | 'NEUTRAL';

/**
 * useMarketData - Hook لجلب بيانات السوق الحية
 * يعطي شعور "Live" مع كشف اتجاه السعر
 */
export function useMarketData(symbol: string) {
    const [data, setData] = useState<MarketData | null>(null);
    const [trend, setTrend] = useState<Trend>('NEUTRAL');
    const [isConnected, setIsConnected] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const prevPrice = useRef<number>(0);

    useEffect(() => {
        let isMounted = true;

        const fetchData = async () => {
            try {
                const response = await fetch(`${API_BASE}/api/market/${symbol}`);

                if (!response.ok) throw new Error('Failed to fetch');

                const result = await response.json();

                if (isMounted) {
                    // حساب الاتجاه (للـ Pulse Effect)
                    if (prevPrice.current > 0) {
                        if (result.price > prevPrice.current) {
                            setTrend('UP');
                        } else if (result.price < prevPrice.current) {
                            setTrend('DOWN');
                        } else {
                            setTrend('NEUTRAL');
                        }
                    }

                    prevPrice.current = result.price;
                    setData(result);
                    setIsConnected(true);
                    setIsLoading(false);

                    // إعادة تعيين الاتجاه بعد الـ Animation
                    setTimeout(() => setTrend('NEUTRAL'), 1000);
                }
            } catch (error) {
                if (isMounted) {
                    setIsConnected(false);
                    console.error('Market data fetch failed:', error);
                }
            }
        };

        // Fetch فوري + كل 3 ثواني
        fetchData();
        const interval = setInterval(fetchData, 3000);

        return () => {
            isMounted = false;
            clearInterval(interval);
        };
    }, [symbol]);

    return { data, trend, isConnected, isLoading };
}

/**
 * useSystemStatus - حالة النظام العامة
 */
export function useSystemStatus() {
    const [status, setStatus] = useState<any>(null);
    const [isOnline, setIsOnline] = useState(false);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const response = await fetch(`${API_BASE}/api/status`);
                const result = await response.json();
                setStatus(result);
                setIsOnline(true);
            } catch {
                setIsOnline(false);
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    return { status, isOnline };
}

/**
 * useAILogs - سجلات Sentinel AI
 */
export function useAILogs(limit = 20) {
    const [logs, setLogs] = useState<any[]>([]);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const response = await fetch(`${API_BASE}/api/ai/logs?limit=${limit}`);
                const result = await response.json();
                setLogs(result.logs || []);
            } catch {
                // Keep existing logs on error
            }
        };

        fetchLogs();
        const interval = setInterval(fetchLogs, 2000);
        return () => clearInterval(interval);
    }, [limit]);

    return logs;
}

/**
 * useMomentum - تحليل الزخم من Antigravity
 */
export function useMomentum(symbol: string) {
    const [momentum, setMomentum] = useState<any>(null);

    useEffect(() => {
        const analyze = async () => {
            try {
                const response = await fetch(`${API_BASE}/api/analyze`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol }),
                });
                const result = await response.json();
                setMomentum(result);
            } catch {
                // Silent fail
            }
        };

        analyze();
        const interval = setInterval(analyze, 10000); // كل 10 ثواني
        return () => clearInterval(interval);
    }, [symbol]);

    return momentum;
}
