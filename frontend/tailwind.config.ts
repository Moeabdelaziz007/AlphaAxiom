import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                // Deep Background Colors
                'terminal-black': '#050505',
                'terminal-dark': '#0a0a0a',
                'terminal-gray': '#121212',

                // Neon Colors (Hedge Fund Colors)
                'neon-cyan': '#00f2ea',   // للأوامر والأنظمة
                'neon-green': '#00ff9d',  // للربح (Profit)
                'neon-red': '#ff0055',    // للخسارة (Loss)
                'neon-gold': '#ffd700',   // للذهب والتحذيرات

                // Keep existing colors for compatibility
                'midnight': '#0a0a0f',
                'panel': '#121218',
                'border-dark': '#1e1e2e',
                'cyan-glow': '#00f2ea',
                'gold-glow': '#ffd700',
                'profit': '#00ff9d',
                'loss': '#ff0055',
            },
            fontFamily: {
                mono: ['JetBrains Mono', 'monospace'],
            },
            animation: {
                'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
                'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
                'ticker': 'ticker 20s linear infinite',
            },
            keyframes: {
                glow: {
                    '0%': { boxShadow: '0 0 5px rgba(0, 242, 234, 0.2)' },
                    '100%': { boxShadow: '0 0 20px rgba(0, 242, 234, 0.6), 0 0 10px rgba(0, 242, 234, 0.4)' },
                },
                'pulse-glow': {
                    '0%, 100%': { opacity: '1' },
                    '50%': { opacity: '0.5' },
                },
                ticker: {
                    '0%': { transform: 'translateX(0)' },
                    '100%': { transform: 'translateX(-50%)' },
                },
            },
        },
    },
    plugins: [],
};
export default config;
