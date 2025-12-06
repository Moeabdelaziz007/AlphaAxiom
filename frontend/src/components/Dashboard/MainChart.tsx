'use client';

import React, { useEffect, useRef, useState } from 'react';
import { AssetType, DEMO_MODE } from '@/lib/types';
import { BarChart3, TrendingUp, TrendingDown, Activity } from 'lucide-react';

interface MainChartProps {
    activeAsset: AssetType;
    selectedSymbol: string;
}

// Demo candlestick data generator with Volume
const generateDemoCandles = (basePrice: number) => {
    const candles = [];
    let price = basePrice;
    const now = Date.now();

    for (let i = 100; i >= 0; i--) {
        const change = (Math.random() - 0.48) * (basePrice * 0.005);
        const open = price;
        const close = price + change;
        const high = Math.max(open, close) + Math.random() * (basePrice * 0.002);
        const low = Math.min(open, close) - Math.random() * (basePrice * 0.002);
        // Generate volume with occasional spikes (big orders)
        const isSpike = Math.random() > 0.9;
        const baseVolume = 1000000 + Math.random() * 500000;
        const volume = isSpike ? baseVolume * (3 + Math.random() * 2) : baseVolume;

        candles.push({
            time: new Date(now - i * 60000).toISOString(),
            open: open.toFixed(2),
            high: high.toFixed(2),
            low: low.toFixed(2),
            close: close.toFixed(2),
            volume: volume,
            isSpike: isSpike,
        });

        price = close;
    }
    return candles;
};

export default function MainChart({ activeAsset, selectedSymbol }: MainChartProps) {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const [chartLib, setChartLib] = useState<any>(null);
    const chartRef = useRef<any>(null);
    const [footprintAlerts, setFootprintAlerts] = useState<string[]>([]);

    // Dynamic import of lightweight-charts (client-side only)
    useEffect(() => {
        let isMounted = true;
        import('lightweight-charts').then((mod) => {
            if (isMounted) {
                setChartLib(mod);
            }
        }).catch(() => {
            console.log('Chart library will be loaded when installed');
        });
        return () => { isMounted = false; };
    }, []);

    useEffect(() => {
        if (!chartLib || !chartContainerRef.current) return;

        let isDisposed = false;

        // Clear previous chart safely
        if (chartRef.current) {
            try {
                chartRef.current.remove();
            } catch (e) {
                // Chart already disposed
            }
            chartRef.current = null;
        }

        const chart = chartLib.createChart(chartContainerRef.current, {
            layout: {
                background: { type: 'solid', color: '#050505' },
                textColor: '#9ca3af',
            },
            grid: {
                vertLines: { color: 'rgba(0, 242, 234, 0.05)' },
                horzLines: { color: 'rgba(0, 242, 234, 0.05)' },
            },
            width: chartContainerRef.current.clientWidth,
            height: 380,
            crosshair: {
                mode: 0,
                vertLine: { color: 'rgba(0, 242, 234, 0.3)', labelBackgroundColor: '#00f2ea' },
                horzLine: { color: 'rgba(0, 242, 234, 0.3)', labelBackgroundColor: '#00f2ea' },
            },
            rightPriceScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
            },
            timeScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
                timeVisible: true,
            },
        });

        chartRef.current = chart;

        // Candlestick series
        const candleSeries = chart.addCandlestickSeries({
            upColor: '#00ff9d',
            downColor: '#ff0055',
            borderUpColor: '#00ff9d',
            borderDownColor: '#ff0055',
            wickUpColor: '#00ff9d',
            wickDownColor: '#ff0055',
        });

        // Volume series (histogram)
        const volumeSeries = chart.addHistogramSeries({
            color: '#26a69a',
            priceFormat: { type: 'volume' },
            priceScaleId: '',
        });

        volumeSeries.priceScale().applyOptions({
            scaleMargins: { top: 0.85, bottom: 0 },
        });

        // Base prices for different assets
        const basePrices: Record<string, number> = {
            'BTC/USDT': 98420,
            'ETH/USDT': 3850,
            'SOL/USDT': 235,
            'TSLA': 350,
            'NVDA': 142,
            'SPY': 590,
            'QQQ': 520,
            'XAUUSD': 2750,
            'XAGUSD': 32,
            'AAPL': 242,
            'GLD': 185,
        };

        const basePrice = basePrices[selectedSymbol] || 100;
        const candles = generateDemoCandles(basePrice);

        // Set candlestick data
        candleSeries.setData(candles.map(c => ({
            time: Math.floor(new Date(c.time).getTime() / 1000) as any,
            open: parseFloat(c.open),
            high: parseFloat(c.high),
            low: parseFloat(c.low),
            close: parseFloat(c.close),
        })));

        // Set volume data with color based on price direction
        volumeSeries.setData(candles.map(c => ({
            time: Math.floor(new Date(c.time).getTime() / 1000) as any,
            value: c.volume,
            color: parseFloat(c.close) >= parseFloat(c.open)
                ? (c.isSpike ? '#00ff9d' : 'rgba(0, 255, 157, 0.4)')
                : (c.isSpike ? '#ff0055' : 'rgba(255, 0, 85, 0.4)'),
        })));

        // Detect footprint alerts (big orders)
        const spikes = candles.filter(c => c.isSpike);
        if (spikes.length > 0) {
            const alerts = spikes.slice(-3).map((s, i) =>
                `🐋 Whale Alert: ${(s.volume / 1000000).toFixed(1)}M volume detected`
            );
            setFootprintAlerts(alerts);
        }

        chart.timeScale().fitContent();

        // Handle resize
        const handleResize = () => {
            if (chartContainerRef.current) {
                chart.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };

        window.addEventListener('resize', handleResize);

        // Update chart in demo mode
        let updateInterval: NodeJS.Timeout;
        if (DEMO_MODE) {
            updateInterval = setInterval(() => {
                if (isDisposed) return;
                const lastCandle = candles[candles.length - 1];
                const newClose = parseFloat(lastCandle.close) + (Math.random() - 0.5) * (basePrice * 0.001);
                const time = Math.floor(Date.now() / 1000) as any;

                candleSeries.update({
                    time,
                    open: parseFloat(lastCandle.close),
                    high: Math.max(parseFloat(lastCandle.close), newClose) + Math.random() * 5,
                    low: Math.min(parseFloat(lastCandle.close), newClose) - Math.random() * 5,
                    close: newClose,
                });

                // Update volume
                const newVolume = 800000 + Math.random() * 400000;
                volumeSeries.update({
                    time,
                    value: newVolume,
                    color: newClose >= parseFloat(lastCandle.close)
                        ? 'rgba(0, 255, 157, 0.4)'
                        : 'rgba(255, 0, 85, 0.4)',
                });
            }, 1000);
        }

        return () => {
            isDisposed = true;
            window.removeEventListener('resize', handleResize);
            if (updateInterval) clearInterval(updateInterval);
            try {
                chart.remove();
            } catch (e) {
                // Chart already disposed - ignore
            }
        };
    }, [chartLib, activeAsset, selectedSymbol]);

    return (
        <div className="glass-panel neon-border rounded-xl overflow-hidden fade-in">
            {/* Chart Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
                <div className="flex items-center gap-3">
                    <BarChart3 className="w-5 h-5 text-neon-cyan" />
                    <span className="text-lg font-bold text-white glow-cyan">{selectedSymbol}</span>
                    <span className="text-xs text-gray-500 bg-terminal-gray px-2 py-0.5 rounded">1M</span>
                </div>
                <div className="flex gap-1">
                    {['1m', '5m', '15m', '1H', '4H', '1D'].map((tf) => (
                        <button
                            key={tf}
                            className="px-2 py-1 text-xs text-gray-500 hover:text-neon-cyan 
                                       hover:bg-neon-cyan/10 rounded transition-colors"
                        >
                            {tf}
                        </button>
                    ))}
                </div>
            </div>

            {/* Footprint Alerts (Big Orders) */}
            {footprintAlerts.length > 0 && (
                <div className="px-4 py-2 bg-neon-gold/5 border-b border-neon-gold/20 flex items-center gap-2 overflow-x-auto">
                    <Activity className="w-4 h-4 text-neon-gold flex-shrink-0" />
                    {footprintAlerts.map((alert, i) => (
                        <span key={i} className="text-xs text-neon-gold whitespace-nowrap fade-in">
                            {alert}
                        </span>
                    ))}
                </div>
            )}

            {/* Chart Container */}
            <div ref={chartContainerRef} className="w-full h-[380px]">
                {!chartLib && (
                    <div className="w-full h-full flex items-center justify-center text-gray-500">
                        <div className="text-center">
                            <div className="animate-pulse text-neon-cyan text-4xl mb-4">📊</div>
                            <p>Loading Chart...</p>
                            <p className="text-xs text-gray-600 mt-2">TradingView Lightweight Charts</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Volume Legend */}
            <div className="px-4 py-2 border-t border-white/10 flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                        <span className="w-3 h-3 bg-neon-green/40 rounded"></span>
                        Buy Volume
                    </span>
                    <span className="flex items-center gap-1">
                        <span className="w-3 h-3 bg-neon-red/40 rounded"></span>
                        Sell Volume
                    </span>
                    <span className="flex items-center gap-1">
                        <span className="w-3 h-3 bg-neon-gold rounded"></span>
                        Whale Orders
                    </span>
                </div>
                <span className="text-neon-cyan">Volume + Footprint Active</span>
            </div>
        </div>
    );
}
