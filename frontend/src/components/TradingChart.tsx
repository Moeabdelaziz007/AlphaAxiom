"use client";
import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, IChartApi, CandlestickSeriesPartialOptions } from 'lightweight-charts';

interface CandleData {
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume?: number;
}

interface TradingChartProps {
    data: CandleData[];
    symbol: string;
    timeframe?: string;
}

export const TradingChart: React.FC<TradingChartProps> = ({ data, symbol, timeframe = "1H" }) => {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (!chartContainerRef.current) return;

        // Clear existing chart
        if (chartRef.current) {
            chartRef.current.remove();
        }

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: '#0a0a0a' },
                textColor: '#6b7280',
            },
            grid: {
                vertLines: { color: '#1f293720' },
                horzLines: { color: '#1f293720' },
            },
            crosshair: {
                mode: 1,
                vertLine: {
                    color: '#22d3ee40',
                    labelBackgroundColor: '#22d3ee',
                },
                horzLine: {
                    color: '#22d3ee40',
                    labelBackgroundColor: '#22d3ee',
                },
            },
            rightPriceScale: {
                borderColor: '#1f2937',
                scaleMargins: { top: 0.1, bottom: 0.2 },
            },
            timeScale: {
                borderColor: '#1f2937',
                timeVisible: true,
                secondsVisible: false,
            },
            width: chartContainerRef.current.clientWidth,
            height: chartContainerRef.current.clientHeight,
        });

        chartRef.current = chart;

        // Candlestick Series
        const candleSeries = chart.addCandlestickSeries({
            upColor: '#22c55e',
            downColor: '#ef4444',
            borderVisible: false,
            wickUpColor: '#22c55e',
            wickDownColor: '#ef4444',
        } as CandlestickSeriesPartialOptions);

        // Volume Series
        const volumeSeries = chart.addHistogramSeries({
            priceFormat: { type: 'volume' },
            priceScaleId: '',
        });
        volumeSeries.priceScale().applyOptions({
            scaleMargins: { top: 0.85, bottom: 0 },
        });

        // Set data
        if (data && data.length > 0) {
            candleSeries.setData(data);

            const volumeData = data.map((item) => ({
                time: item.time,
                value: item.volume || Math.random() * 1000000,
                color: item.close > item.open ? '#22c55e40' : '#ef444440',
            }));
            volumeSeries.setData(volumeData);

            chart.timeScale().fitContent();
            setIsLoading(false);
        }

        // Resize handler
        const handleResize = () => {
            if (chartContainerRef.current && chartRef.current) {
                chartRef.current.applyOptions({
                    width: chartContainerRef.current.clientWidth,
                    height: chartContainerRef.current.clientHeight,
                });
            }
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            if (chartRef.current) {
                chartRef.current.remove();
            }
        };
    }, [data]);

    return (
        <div className="relative w-full h-full rounded-xl overflow-hidden bg-[#0a0a0a] border border-gray-800/50">
            {/* Symbol Badge */}
            <div className="absolute top-4 left-4 z-10 flex items-center gap-3">
                <div className="bg-gradient-to-r from-cyan-500/20 to-transparent backdrop-blur-sm px-4 py-2 rounded-lg border border-cyan-500/30">
                    <span className="text-cyan-400 font-bold text-lg">{symbol}</span>
                    <span className="text-gray-500 ml-2 text-sm">{timeframe}</span>
                </div>

                {/* Timeframe Buttons */}
                <div className="flex gap-1 bg-gray-900/80 backdrop-blur-sm rounded-lg p-1 border border-gray-800/50">
                    {['1m', '5m', '15m', '1H', '4H', '1D'].map((tf) => (
                        <button
                            key={tf}
                            className={`px-2 py-1 text-xs rounded transition-all ${tf === timeframe
                                    ? 'bg-cyan-500/20 text-cyan-400'
                                    : 'text-gray-500 hover:text-gray-300'
                                }`}
                        >
                            {tf}
                        </button>
                    ))}
                </div>
            </div>

            {/* Price Change Badge */}
            <div className="absolute top-4 right-4 z-10">
                <div className="bg-green-500/10 backdrop-blur-sm px-3 py-2 rounded-lg border border-green-500/30">
                    <span className="text-green-400 font-bold">+2.34%</span>
                </div>
            </div>

            {/* Loading State */}
            {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-[#0a0a0a]">
                    <div className="flex flex-col items-center gap-3">
                        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
                        <span className="text-gray-500 text-sm">Loading chart...</span>
                    </div>
                </div>
            )}

            {/* Chart Container */}
            <div ref={chartContainerRef} className="w-full h-full" />
        </div>
    );
};
