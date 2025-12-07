import type { Metadata, Viewport } from "next";
import { JetBrains_Mono } from "next/font/google";
import "./globals.css";

const mono = JetBrains_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "Antigravity Terminal",
    description: "AI-Powered Trading Terminal - Bloomberg Killer",
    manifest: "/manifest.json",
    appleWebApp: {
        capable: true,
        statusBarStyle: "black-translucent",
        title: "Antigravity",
    },
    icons: {
        icon: "/logo.png",
        apple: "/logo.png",
    },
};

export const viewport: Viewport = {
    themeColor: "#06b6d4",
    width: "device-width",
    initialScale: 1,
    maximumScale: 1,
    userScalable: false,
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <head>
                <link rel="apple-touch-icon" href="/logo.png" />
                <meta name="apple-mobile-web-app-capable" content="yes" />
                <meta name="mobile-web-app-capable" content="yes" />
            </head>
            <body className={mono.className}>
                {children}
            </body>
        </html>
    );
}
