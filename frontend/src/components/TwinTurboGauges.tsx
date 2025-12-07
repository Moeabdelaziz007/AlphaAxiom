"use client";

interface GaugeProps {
    label: string;
    value: number;
    maxValue?: number;
    color: string;
    description?: string;
}

function Gauge({ label, value, maxValue = 100, color, description }: GaugeProps) {
    const percentage = Math.min((value / maxValue) * 100, 100);

    return (
        <div className="bg-white/[0.02] border border-white/[0.06] rounded-xl p-5 hover:border-white/10 transition-colors">
            <div className="flex items-center justify-between mb-3">
                <span className="text-[13px] font-medium text-white/60">{label}</span>
                <span className="text-[11px] text-white/30">{description}</span>
            </div>

            <div className="flex items-end gap-3 mb-3">
                <span className="text-3xl font-semibold text-white tracking-tight">
                    {value.toFixed(1)}
                </span>
                <span className="text-white/30 text-[14px] mb-1">/ {maxValue}</span>
            </div>

            {/* Progress Bar */}
            <div className="h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                <div
                    className="h-full rounded-full transition-all duration-500 ease-out"
                    style={{
                        width: `${percentage}%`,
                        background: color
                    }}
                />
            </div>

            {/* Threshold Markers */}
            <div className="flex justify-between mt-2 text-[10px] text-white/20">
                <span>0</span>
                <span className="text-white/40">Trigger: 80</span>
                <span>{maxValue}</span>
            </div>
        </div>
    );
}

export default function TwinTurboGauges() {
    // Demo values - in production these would come from API
    const aexi = 75.4;
    const dream = 68.2;

    return (
        <div className="space-y-4">
            <h2 className="text-[13px] font-medium text-white/40 uppercase tracking-wider">
                Twin-Turbo Engines
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Gauge
                    label="AEXI Protocol"
                    value={aexi}
                    color="linear-gradient(90deg, #00F0FF 0%, #0080FF 100%)"
                    description="Exhaustion Index"
                />
                <Gauge
                    label="Dream Machine"
                    value={dream}
                    color="linear-gradient(90deg, #8B5CF6 0%, #D946EF 100%)"
                    description="Chaos Theory"
                />
            </div>
        </div>
    );
}
