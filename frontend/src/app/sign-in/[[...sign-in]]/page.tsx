import { SignIn } from "@clerk/nextjs";

export default function Page() {
    return (
        <div className="flex items-center justify-center min-h-screen bg-black/90 backdrop-blur-xl">
            <div className="p-8 border border-white/10 rounded-2xl bg-black/50 shadow-2xl shadow-neon-green/20">
                <h1 className="text-3xl font-bold text-center mb-8 text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">
                    Axiom Access
                </h1>
                <SignIn appearance={{
                    elements: {
                        formButtonPrimary: 'bg-neon-green hover:bg-neon-green/80 text-black font-bold',
                        card: 'bg-transparent shadow-none',
                        headerTitle: 'hidden',
                        headerSubtitle: 'text-gray-400',
                        socialButtonsBlockButton: 'border-white/20 hover:bg-white/5 text-white',
                        formFieldLabel: 'text-gray-400',
                        formFieldInput: 'bg-white/5 border-white/10 text-white focus:border-neon-green',
                        footerActionLink: 'text-neon-green hover:text-neon-green/80'
                    }
                }} />
            </div>
        </div>
    );
}
