"use client";
import { motion } from 'framer-motion';

/**
 * 💀 Skeleton Loading Components
 * Used to show loading states with animated placeholders
 */

interface SkeletonProps {
    className?: string;
    variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
    width?: string | number;
    height?: string | number;
}

export function Skeleton({
    className = '',
    variant = 'rectangular',
    width,
    height
}: SkeletonProps) {
    const baseClasses = "bg-gradient-to-r from-white/[0.02] via-white/[0.05] to-white/[0.02]";

    const variantClasses = {
        text: "h-4 rounded",
        circular: "rounded-full",
        rectangular: "rounded",
        rounded: "rounded-xl"
    };

    return (
        <motion.div
            className={`${baseClasses} ${variantClasses[variant]} ${className}`}
            style={{
                width,
                height,
                backgroundSize: '200% 100%'
            }}
            animate={{ backgroundPosition: ['200% 0', '-200% 0'] }}
            transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'linear'
            }}
        />
    );
}


// Pre-built skeleton patterns
export function SkeletonCard() {
    return (
        <div className="p-5 rounded-xl bg-white/[0.02] border border-white/[0.06] space-y-4">
            <div className="flex items-center justify-between">
                <Skeleton variant="text" width="40%" height={16} />
                <Skeleton variant="circular" width={24} height={24} />
            </div>
            <Skeleton variant="text" width="60%" height={32} />
            <Skeleton variant="rounded" width="100%" height={8} />
        </div>
    );
}

export function SkeletonChart() {
    return (
        <div className="p-5 rounded-xl bg-white/[0.02] border border-white/[0.06]">
            <Skeleton variant="text" width="30%" height={16} className="mb-4" />
            <div className="flex items-end gap-2 h-32">
                {[40, 65, 45, 80, 55, 70, 60].map((h, i) => (
                    <Skeleton
                        key={i}
                        variant="rounded"
                        width="14%"
                        height={`${h}%`}
                        className="flex-1"
                    />
                ))}
            </div>
        </div>
    );
}

export function SkeletonGauge() {
    return (
        <div className="p-5 rounded-xl bg-white/[0.02] border border-white/[0.06] space-y-3">
            <div className="flex justify-between">
                <Skeleton variant="text" width="40%" height={14} />
                <Skeleton variant="text" width="20%" height={12} />
            </div>
            <Skeleton variant="text" width="30%" height={32} />
            <Skeleton variant="rounded" width="100%" height={6} />
        </div>
    );
}

export function SkeletonPosition() {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-[#0A0A0A] border border-white/5 rounded-xl p-4 flex justify-between items-center"
        >
            <div className="flex items-center gap-4">
                <Skeleton variant="rectangular" width={4} height={48} />
                <div className="space-y-2">
                    <Skeleton variant="text" width={80} height={20} />
                    <Skeleton variant="text" width={120} height={12} />
                </div>
            </div>
            <div className="text-right space-y-2">
                <Skeleton variant="text" width={60} height={20} />
                <Skeleton variant="text" width={40} height={12} />
            </div>
        </motion.div>
    );
}

// Loading wrapper with skeleton children
interface LoadingWrapperProps {
    loading: boolean;
    skeleton: React.ReactNode;
    children: React.ReactNode;
}

export function LoadingWrapper({ loading, skeleton, children }: LoadingWrapperProps) {
    if (loading) return <>{skeleton}</>;
    return <>{children}</>;
}
