import { notFound } from 'next/navigation';
import { setRequestLocale } from 'next-intl/server';
import { getLocale } from 'next-intl/server';

export default async function GlobalNotFound() {
    // Get the locale and set it for static rendering
    const locale = await getLocale();
    setRequestLocale(locale);
    
    return notFound();
}