import { UserButton, SignInButton, SignedIn, SignedOut } from '@clerk/nextjs';
import Link from 'next/link';
import LanguageSwitcher from './LanguageSwitcher';
import ModeToggle from './ModeToggle';

export default function Navbar() {
    return (
        <nav className="fixed top-0 w-full z-50 border-b border-white/10 bg-black/50 backdrop-blur-xl">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link href="/" className="flex-shrink-0 flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-neon-green/20 border border-neon-green/50 flex items-center justify-center">
                            <span className="text-neon-green font-bold">A</span>
                        </div>
                        <span className="text-xl font-bold tracking-tight text-white">
                            AXIOM <span className="text-neon-green">ANTIGRAVITY</span>
                        </span>
                    </Link>

                    {/* Right Controls */}
                    <div className="flex items-center gap-4">
                        <LanguageSwitcher />
                        <ModeToggle />

                        <div className="h-6 w-px bg-white/20 mx-2" />

                        <SignedIn>
                            <UserButton
                                afterSignOutUrl="/"
                                appearance={{
                                    elements: {
                                        avatarBox: "w-8 h-8 border border-neon-green/50 hover:border-neon-green transition-colors"
                                    }
                                }}
                            />
                        </SignedIn>

                        <SignedOut>
                            <SignInButton mode="modal">
                                <button className="px-4 py-2 text-sm font-bold text-black bg-neon-green rounded hover:bg-neon-green/80 transition-all shadow-[0_0_10px_rgba(57,255,20,0.3)]">
                                    ACCESS SYSTEM
                                </button>
                            </SignInButton>
                        </SignedOut>
                    </div>
                </div>
            </div>
        </nav>
    );
}
