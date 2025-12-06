import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import "./globals.css";

const mono = JetBrains_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "Antigravity Trading LLM",
    description: "AI-Powered Institutional Trading System - Zero Cost, Maximum Intelligence",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className={mono.className}>
                {children}
            </body>
        </html>
    );
}
