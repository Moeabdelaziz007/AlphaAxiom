"use client";
import { motion } from 'framer-motion';

interface GaugeProps {
    label: string;
    value: number;
    maxValue?: number;
    color: string;
    description?: string;
    index?: number;
}

// Animation variants for staggered entrance
const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.15,
            delayChildren: 0.1
        }
    }
};

const itemVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.95 },
    visible: {
        opacity: 1,
        y: 0,
        scale: 1,
        transition: {
            type: "spring",
            stiffness: 300,
            damping: 24
        }
    }
};

function Gauge({ label, value, maxValue = 100, color, description, index = 0 }: GaugeProps) {
    const percentage = Math.min((value / maxValue) * 100, 100);
    const isTriggered = value >= 80;

    return (
        <motion.div
            variants={itemVariants}
            whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
            className={`bg-white/[0.02] border rounded-xl p-5 transition-colors ${isTriggered
                    ? 'border-[#00F0FF]/30 shadow-lg shadow-[#00F0FF]/10'
                    : 'border-white/[0.06] hover:border-white/10'
                }`}
        >
            <div className="flex items-center justify-between mb-3">
                <span className="text-[13px] font-medium text-white/60">{label}</span>
                <motion.span
                    className="text-[11px] text-white/30"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                >
                    {description}
                </motion.span>
            </div>

            <div className="flex items-end gap-3 mb-3">
                <motion.span
                    className="text-3xl font-semibold text-white tracking-tight tabular-nums"
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ type: "spring", delay: 0.2 }}
                >
                    {value.toFixed(1)}
                </motion.span>
                <span className="text-white/30 text-[14px] mb-1">/ {maxValue}</span>
            </div>

            {/* Animated Progress Bar */}
            <div className="h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                <motion.div
                    className="h-full rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{
                        duration: 1,
                        delay: 0.3,
                        ease: [0.4, 0, 0.2, 1] // Smooth ease-out
                    }}
                    style={{ background: color }}
                />
            </div>

            {/* Threshold Markers */}
            <div className="flex justify-between mt-2 text-[10px] text-white/20">
                <span>0</span>
                <motion.span
                    className={isTriggered ? 'text-[#00F0FF]' : 'text-white/40'}
                    animate={isTriggered ? {
                        textShadow: ['0 0 0px #00F0FF', '0 0 10px #00F0FF', '0 0 0px #00F0FF']
                    } : {}}
                    transition={{ duration: 1.5, repeat: Infinity }}
                >
                    Trigger: 80
                </motion.span>
                <span>{maxValue}</span>
            </div>
        </motion.div>
    );
}

export default function TwinTurboGauges() {
    // Demo values - in production these would come from API
    const aexi = 75.4;
    const dream = 68.2;

    return (
        <motion.div
            className="space-y-4"
            initial="hidden"
            animate="visible"
            variants={containerVariants}
        >
            <motion.h2
                className="text-[13px] font-medium text-white/40 uppercase tracking-wider"
                variants={itemVariants}
            >
                Twin-Turbo Engines
            </motion.h2>

            <motion.div
                className="grid grid-cols-1 md:grid-cols-2 gap-4"
                variants={containerVariants}
            >
                <Gauge
                    label="AEXI Protocol"
                    value={aexi}
                    color="linear-gradient(90deg, #00F0FF 0%, #0080FF 100%)"
                    description="Exhaustion Index"
                    index={0}
                />
                <Gauge
                    label="Dream Machine"
                    value={dream}
                    color="linear-gradient(90deg, #8B5CF6 0%, #D946EF 100%)"
                    description="Chaos Theory"
                    index={1}
                />
            </motion.div>
        </motion.div>
    );
}

