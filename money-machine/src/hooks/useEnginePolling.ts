'use client';

import { useEffect, useCallback } from 'react';
import { useAppStore } from '@/store/useAppStore';
import { getPortfolio, getStatus, ping } from '@/lib/tauri';

/**
 * Hook to poll engine data at regular intervals
 */
export function useEnginePolling(intervalMs: number = 5000) {
    const { setPortfolio, setEngineStatus, setConnected, setError } = useAppStore((state) => ({
        setPortfolio: state.setPortfolio,
        setEngineStatus: state.setEngineStatus,
        setConnected: (connected: boolean) => useAppStore.setState({ connected }),
        setError: state.setError,
    }));

    const fetchData = useCallback(async () => {
        try {
            // Health check
            const isAlive = await ping();
            if (!isAlive) {
                setError('Engine not responding');
                return;
            }

            // Fetch status
            const status = await getStatus();
            setEngineStatus(status);

            // Fetch portfolio
            const portfolio = await getPortfolio();
            setPortfolio(portfolio);

            setError(null);
        } catch (err) {
            console.error('Engine polling error:', err);
            setError(err instanceof Error ? err.message : 'Unknown error');
        }
    }, [setPortfolio, setEngineStatus, setError]);

    useEffect(() => {
        // Initial fetch
        fetchData();

        // Set up polling interval
        const interval = setInterval(fetchData, intervalMs);

        return () => clearInterval(interval);
    }, [fetchData, intervalMs]);
}
