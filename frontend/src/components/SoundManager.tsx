"use client";
import React, { createContext, useContext, useState, useCallback } from 'react';
import useSound from 'use-sound';

// Sound URLs (we'll use free sounds from public CDN as fallback)
const SOUNDS = {
    success: '/sounds/success.mp3',
    error: '/sounds/error.mp3',
    alert: '/sounds/alert.mp3',
    click: '/sounds/click.mp3',
    type: '/sounds/type.mp3',
};

interface SoundContextType {
    isMuted: boolean;
    toggleMute: () => void;
    playSuccess: () => void;
    playError: () => void;
    playAlert: () => void;
    playClick: () => void;
    playType: () => void;
}

const SoundContext = createContext<SoundContextType | null>(null);

export function SoundProvider({ children }: { children: React.ReactNode }) {
    const [isMuted, setIsMuted] = useState(false);

    // Load sounds with use-sound hook
    const [playSuccessSound] = useSound(SOUNDS.success, { volume: 0.5 });
    const [playErrorSound] = useSound(SOUNDS.error, { volume: 0.4 });
    const [playAlertSound] = useSound(SOUNDS.alert, { volume: 0.6 });
    const [playClickSound] = useSound(SOUNDS.click, { volume: 0.3 });
    const [playTypeSound] = useSound(SOUNDS.type, { volume: 0.15 });

    const toggleMute = useCallback(() => {
        setIsMuted(prev => !prev);
    }, []);

    const playSuccess = useCallback(() => {
        if (!isMuted) playSuccessSound();
    }, [isMuted, playSuccessSound]);

    const playError = useCallback(() => {
        if (!isMuted) playErrorSound();
    }, [isMuted, playErrorSound]);

    const playAlert = useCallback(() => {
        if (!isMuted) playAlertSound();
    }, [isMuted, playAlertSound]);

    const playClick = useCallback(() => {
        if (!isMuted) playClickSound();
    }, [isMuted, playClickSound]);

    const playType = useCallback(() => {
        if (!isMuted) playTypeSound();
    }, [isMuted, playTypeSound]);

    return (
        <SoundContext.Provider value={{
            isMuted,
            toggleMute,
            playSuccess,
            playError,
            playAlert,
            playClick,
            playType,
        }}>
            {children}
        </SoundContext.Provider>
    );
}

export function useSounds() {
    const context = useContext(SoundContext);
    if (!context) {
        // Return no-op functions if outside provider
        return {
            isMuted: false,
            toggleMute: () => { },
            playSuccess: () => { },
            playError: () => { },
            playAlert: () => { },
            playClick: () => { },
            playType: () => { },
        };
    }
    return context;
}

// Mute Toggle Button Component
export function MuteButton() {
    const { isMuted, toggleMute } = useSounds();

    return (
        <button
            onClick={toggleMute}
            className={`p-2 rounded-lg transition-all ${isMuted
                ? 'bg-gray-800 text-gray-500'
                : 'bg-emerald-500/20 text-emerald-400'
                }`}
            title={isMuted ? 'Unmute sounds' : 'Mute sounds'}
        >
            {isMuted ? (
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                    <line x1="23" y1="9" x2="17" y2="15" />
                    <line x1="17" y1="9" x2="23" y2="15" />
                </svg>
            ) : (
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                    <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
                    <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
                </svg>
            )}
        </button>
    );
}
