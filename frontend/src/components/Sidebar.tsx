"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { Zap, Newspaper, Settings, Moon } from 'lucide-react';

export default function Sidebar() {
    const t = useTranslations('Sidebar');
    const pathname = usePathname();
    const locale = pathname?.split('/')[1] || 'en';

    const navItems = [
        { icon: Zap, label: 'Signals', path: `/${locale}`, id: 'signals' },
        { icon: Newspaper, label: 'News', path: `/${locale}/news`, id: 'news' },
        { icon: Settings, label: 'Settings', path: `/${locale}/settings`, id: 'settings' },
    ];

    const isActive = (path: string) => {
        if (path === `/${locale}` && pathname === `/${locale}`) return true;
        if (path !== `/${locale}` && pathname?.startsWith(path)) return true;
        return false;
    };

    return (
        <aside className="w-64 h-screen bg-[#0a0a0f] border-e border-white/[0.06] flex flex-col">
            {/* Logo */}
            <div className="h-14 flex items-center px-5 border-b border-white/[0.06]">
                <Link href={`/${locale}`} className="flex items-center gap-3">
                    <Image
                        src="/icon.png"
                        alt="Axiom"
                        width={28}
                        height={28}
                        className="rounded-lg"
                    />
                    <span className="font-semibold text-[15px] tracking-tight text-white/90">
                        Axiom Signals
                    </span>
                </Link>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-3 py-4">
                <div className="space-y-1">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const active = isActive(item.path);

                        return (
                            <Link
                                key={item.id}
                                href={item.path}
                                className={`
                                    flex items-center gap-3 px-3 py-2 rounded-lg text-[14px] font-medium
                                    transition-all duration-150
                                    ${active
                                        ? 'bg-white/[0.08] text-white'
                                        : 'text-white/50 hover:text-white/80 hover:bg-white/[0.04]'
                                    }
                                `}
                            >
                                <Icon size={18} className={active ? 'text-[#00F0FF]' : ''} />
                                <span>{item.label}</span>
                            </Link>
                        );
                    })}
                </div>
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-white/[0.06]">
                <div className="flex items-center justify-between px-2">
                    <div className="flex items-center gap-2">
                        <Moon size={16} className="text-white/40" />
                        <span className="text-[12px] text-white/40">Dark Mode</span>
                    </div>
                    <div className="w-8 h-4 bg-[#00F0FF]/20 rounded-full flex items-center justify-end px-0.5">
                        <div className="w-3 h-3 bg-[#00F0FF] rounded-full" />
                    </div>
                </div>
            </div>
        </aside>
    );
}
