import { ClerkProvider } from '@clerk/nextjs';
import { NextIntlClientProvider } from 'next-intl';
import { getLocale, getMessages } from 'next-intl/server';
import './globals.css';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
    title: 'Axiom Antigravity | AI Trading Platform',
    description: 'The First AI-Powered Trading Ecosystem',
};

export default async function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const locale = await getLocale();
    const messages = await getMessages();

    return (
        <ClerkProvider>
            <html lang={locale} dir={locale === 'ar' ? 'rtl' : 'ltr'}>
                <body className={inter.className}>
                    <NextIntlClientProvider messages={messages}>
                        <main className="min-h-screen bg-black text-white selection:bg-neon-green selection:text-black">
                            {children}
                        </main>
                    </NextIntlClientProvider>
                </body>
            </html>
        </ClerkProvider>
    );
}
