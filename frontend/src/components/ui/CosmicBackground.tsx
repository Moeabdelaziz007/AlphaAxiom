"use client";
import { useCallback, useState, useEffect } from "react";
import Particles from "react-tsparticles";
import { loadSlim } from "tsparticles-slim";
import type { Engine } from "tsparticles-engine";

export default function CosmicBackground() {
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    const particlesInit = useCallback(async (engine: Engine) => {
        await loadSlim(engine);
    }, []);

    // Only render particles on client side after mount
    if (!isMounted) {
        return <div className="absolute inset-0 bg-void" />;
    }

    return (
        <Particles
            id="tsparticles"
            init={particlesInit}
            options={{
                background: {
                    color: { value: "#020204" },
                },
                fpsLimit: 60,
                particles: {
                    color: { value: "#00F0FF" },
                    links: {
                        color: "#00F0FF",
                        distance: 150,
                        enable: true,
                        opacity: 0.1,
                        width: 1,
                    },
                    move: {
                        enable: true,
                        speed: 0.5,
                        direction: "none",
                        outModes: { default: "bounce" },
                    },
                    number: {
                        density: { enable: true, area: 800 },
                        value: 60,
                    },
                    opacity: {
                        value: 0.3,
                        animation: {
                            enable: true,
                            speed: 1,
                            minimumValue: 0.1,
                        },
                    },
                    size: {
                        value: { min: 1, max: 2 },
                    },
                },
                detectRetina: true,
            }}
            className="absolute inset-0 -z-10"
        />
    );
}
