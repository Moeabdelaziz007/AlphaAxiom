import type { Config } from "tailwindcss";

const config: Config = {
    darkMode: ["class"],
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                // 🌌 MIDNIGHT VOID Design System
                void: '#020204',
                obsidian: '#0A0A0F',
                glass: 'rgba(10, 10, 15, 0.6)',

                // Neon Accents
                neon: {
                    cyan: '#00F0FF',
                    magenta: '#FF003C',
                    green: '#05FFA1',
                    gold: '#FFD700',
                    purple: '#8B5CF6',
                },
            },
            fontFamily: {
                orbitron: ['var(--font-orbitron)'],
                mono: ['var(--font-jetbrains)'],
                arabic: ['var(--font-cairo)', 'IBM Plex Sans Arabic', 'sans-serif'],
            },
            boxShadow: {
                'neon-cyan': '0 0 10px rgba(0, 240, 255, 0.5), 0 0 20px rgba(0, 240, 255, 0.3)',
                'neon-red': '0 0 10px rgba(255, 0, 60, 0.5), 0 0 20px rgba(255, 0, 60, 0.3)',
                'neon-green': '0 0 10px rgba(5, 255, 161, 0.5), 0 0 20px rgba(5, 255, 161, 0.3)',
                'neon-gold': '0 0 10px rgba(255, 215, 0, 0.5), 0 0 20px rgba(255, 215, 0, 0.3)',
                'glass': '0 0 1px rgba(0, 240, 255, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.03)',
            },
            backgroundImage: {
                'void-cosmic': 'radial-gradient(ellipse at 50% 0%, rgba(0, 240, 255, 0.05) 0%, transparent 50%), radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.03) 0%, transparent 40%), linear-gradient(180deg, #020204 0%, #0a0a0f 100%)',
            },
            animation: {
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'pulse-glow': 'pulseGlow 2s infinite',
                'float': 'float 6s ease-in-out infinite',
                'ticker': 'ticker 30s linear infinite',
                'fade-in': 'fadeIn 0.2s ease-out forwards',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
                pulseGlow: {
                    '0%, 100%': { boxShadow: '0 0 5px rgba(0, 240, 255, 0.3)' },
                    '50%': { boxShadow: '0 0 20px rgba(0, 240, 255, 0.6)' },
                },
                ticker: {
                    '0%': { transform: 'translateX(100%)' },
                    '100%': { transform: 'translateX(-100%)' },
                },
                fadeIn: {
                    '0%': { opacity: '0', transform: 'scale(0.95)' },
                    '100%': { opacity: '1', transform: 'scale(1)' },
                },
            },
        },
    },
    plugins: [],
};

export default config;
