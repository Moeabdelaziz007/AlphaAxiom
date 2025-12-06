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
                // Midnight Protocol Theme
                midnight: {
                    void: '#050505',
                    surface: '#0A0A0A',
                    border: '#1F1F1F',
                },
                neon: {
                    cyan: '#06B6D4',
                    green: '#10B981',
                    red: '#F43F5E',
                },
            },
            fontFamily: {
                mono: ['JetBrains Mono', 'monospace'],
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            boxShadow: {
                'neon-cyan': '0 0 15px rgba(6, 182, 212, 0.3)',
                'neon-green': '0 0 15px rgba(16, 185, 129, 0.3)',
                'neon-red': '0 0 15px rgba(244, 63, 94, 0.3)',
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(circle at 50% 0%, #111827 0%, #050505 50%)',
            },
        },
    },
    plugins: [],
};

export default config;
