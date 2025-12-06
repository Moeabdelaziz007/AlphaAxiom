// Trading System Types
// نظام التداول الموحد - Type Definitions

export type AssetType = 'CRYPTO' | 'STOCKS' | 'GOLD';

export interface MarketData {
    symbol: string;
    price: number;
    change: number;
    changePercent: number;
    high24h: number;
    low24h: number;
    volume: number;
}

export interface Position {
    id: string;
    symbol: string;
    type: 'LONG' | 'SHORT';
    entryPrice: number;
    currentPrice: number;
    quantity: number;
    pnl: number;
    pnlPercent: number;
    stopLoss?: number;
    takeProfit?: number;
    openTime: Date;
}

export interface Order {
    symbol: string;
    type: 'MARKET' | 'LIMIT';
    side: 'BUY' | 'SELL';
    quantity: number;
    price?: number;
    stopLoss?: number;
    takeProfit?: number;
}

export interface SentinelLog {
    id: string;
    timestamp: Date;
    type: 'INFO' | 'SCAN' | 'SIGNAL' | 'EXECUTE' | 'WARNING' | 'SUCCESS';
    message: string;
}

export interface PortfolioStats {
    totalEquity: number;
    totalPnl: number;
    totalPnlPercent: number;
    openPositions: number;
    riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
    winRate: number;
}

// Demo Mode Configuration
export const DEMO_MODE = true;

// Asset Colors
export const ASSET_COLORS: Record<AssetType, string> = {
    CRYPTO: '#06b6d4',  // Cyan
    STOCKS: '#3b82f6',  // Blue
    GOLD: '#fbbf24',    // Gold
};

// Demo Symbols
export const ASSETS: Record<AssetType, string[]> = {
    CRYPTO: ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'],
    STOCKS: ['TSLA', 'NVDA', 'SPY', 'QQQ'],
    GOLD: ['XAUUSD', 'XAGUSD'],
};
