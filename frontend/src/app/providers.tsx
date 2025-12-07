"use client";

import { SoundProvider } from "@/components/SoundManager";

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <SoundProvider>
            {children}
        </SoundProvider>
    );
}
