"use client";
import React, { createContext, useContext, ReactNode } from "react";

// Simple SoundProvider that does nothing (placeholder for future sound features)
interface SoundContextType {
    playClick: () => void;
    playSuccess: () => void;
    playError: () => void;
}

const SoundContext = createContext<SoundContextType>({
    playClick: () => { },
    playSuccess: () => { },
    playError: () => { },
});

export function SoundProvider({ children }: { children: ReactNode }) {
    const playClick = () => {
        // Placeholder for click sound
    };

    const playSuccess = () => {
        // Placeholder for success sound
    };

    const playError = () => {
        // Placeholder for error sound
    };

    return (
        <SoundContext.Provider value={{ playClick, playSuccess, playError }}>
            {children}
        </SoundContext.Provider>
    );
}

export function useSound() {
    return useContext(SoundContext);
}
