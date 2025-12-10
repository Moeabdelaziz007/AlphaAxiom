import { getRequestConfig } from 'next-intl/server';
import { notFound } from 'next/navigation';

// Supported locales
const locales = ['en', 'ar'] as const;

export default getRequestConfig(async ({ requestLocale }) => {
    // Wait for the locale to be determined
    const locale = await requestLocale;
    
    // Validate that the incoming `locale` parameter is valid
    if (!locales.includes(locale as any)) notFound();

    return {
        messages: (await import(`../../messages/${locale}.json`)).default
    };
});
