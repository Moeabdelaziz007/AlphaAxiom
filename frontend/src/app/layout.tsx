import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
    title: 'Trading System 0.1 | Hedge Fund Terminal',
    description: 'نظام التداول الموحد - Multi-Asset Trading Platform',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="ar" dir="ltr">
            <head>
                <link
                    href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap"
                    rel="stylesheet"
                />
            </head>
            <body className="min-h-screen bg-midnight antialiased">
                {children}
            </body>
        </html>
    )
}
