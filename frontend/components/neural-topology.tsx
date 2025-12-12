"use client"

import { useEffect, useRef } from "react"

export function NeuralTopology() {
    const canvasRef = useRef<HTMLCanvasElement>(null)

    useEffect(() => {
        const canvas = canvasRef.current
        if (!canvas) return

        const ctx = canvas.getContext("2d")
        if (!ctx) return

        let width = (canvas.width = window.innerWidth)
        let height = (canvas.height = window.innerHeight)

        // Quantum/Neural Nodes
        const nodes: Node[] = []
        const nodeCount = Math.min(Math.floor((width * height) / 15000), 100)
        const connectionDistance = 150
        const pulseSpeed = 0.02

        class Node {
            x: number
            y: number
            vx: number
            vy: number
            size: number
            pulse: number

            constructor() {
                this.x = Math.random() * width
                this.y = Math.random() * height
                this.vx = (Math.random() - 0.5) * 0.5 // Slow, floating movement
                this.vy = (Math.random() - 0.5) * 0.5
                this.size = Math.random() * 2 + 1
                this.pulse = Math.random() * Math.PI
            }

            update() {
                this.x += this.vx
                this.y += this.vy

                // Bounce off edges
                if (this.x < 0 || this.x > width) this.vx *= -1
                if (this.y < 0 || this.y > height) this.vy *= -1

                // Pulse animation
                this.pulse += pulseSpeed
            }

            draw() {
                if (!ctx) return
                const currentSize = this.size + Math.sin(this.pulse) * 0.5

                ctx.beginPath()
                ctx.arc(this.x, this.y, currentSize, 0, Math.PI * 2)
                ctx.fillStyle = `rgba(57, 255, 20, ${0.3 + Math.sin(this.pulse) * 0.2})` // #39FF14 with pulsing opacity
                ctx.fill()
            }
        }

        // Initialize nodes
        for (let i = 0; i < nodeCount; i++) {
            nodes.push(new Node())
        }

        const animate = () => {
            if (!ctx) return

            ctx.clearRect(0, 0, width, height)

            // Update and draw nodes
            nodes.forEach((node, i) => {
                node.update()
                node.draw()

                // Draw connections
                for (let j = i + 1; j < nodes.length; j++) {
                    const other = nodes[j]
                    const dx = node.x - other.x
                    const dy = node.y - other.y
                    const distance = Math.sqrt(dx * dx + dy * dy)

                    if (distance < connectionDistance) {
                        const opacity = 1 - distance / connectionDistance
                        ctx.beginPath()
                        ctx.moveTo(node.x, node.y)
                        ctx.lineTo(other.x, other.y)
                        ctx.strokeStyle = `rgba(57, 255, 20, ${opacity * 0.15})` // Faint green lines
                        ctx.lineWidth = 1
                        ctx.stroke()
                    }
                }
            })

            requestAnimationFrame(animate)
        }

        animate()

        const handleResize = () => {
            width = canvas.width = window.innerWidth
            height = canvas.height = window.innerHeight
        }

        window.addEventListener("resize", handleResize)
        return () => window.removeEventListener("resize", handleResize)
    }, [])

    return (
        <canvas
            ref={canvasRef}
            className="fixed inset-0 z-0 pointer-events-none opacity-40 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-zinc-900/0 via-zinc-900/0 to-zinc-950/80"
            style={{ background: 'transparent' }}
        />
    )
}
