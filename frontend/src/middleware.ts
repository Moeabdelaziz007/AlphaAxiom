import createMiddleware from 'next-intl/middleware';
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

// next-intl middleware for i18n routing
const intlMiddleware = createMiddleware({
    locales: ['en', 'ar'],
    defaultLocale: 'en',
    localePrefix: 'as-needed'
});

// Define which routes are protected by Clerk
const isProtectedRoute = createRouteMatcher([
    '/dashboard(.*)',
    '/profile(.*)',
    '/settings(.*)',
    '/bots(.*)',
    '/test-ai(.*)'
]);

// Export the combined middleware
export default clerkMiddleware((auth, req) => {
    // Protect routes that require authentication
    if (isProtectedRoute(req)) auth().protect();
    
    // Apply internationalization to all routes
    return intlMiddleware(req);
});

export const config = {
    matcher: [
        // Skip Next.js internals and all static files, unless found in search params
        '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
        // Always run for API routes
        '/(api|trpc)(.*)',
    ],
};