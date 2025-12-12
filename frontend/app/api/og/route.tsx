import { ImageResponse } from 'next/og';

export const runtime = 'edge';

export async function GET() {
    return new ImageResponse(
        (
            <div
                style={{
                    height: '100%',
                    width: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: '#050505',
                    backgroundImage: 'radial-gradient(circle at 25px 25px, #333 2%, transparent 0%), radial-gradient(circle at 75px 75px, #333 2%, transparent 0%)',
                    backgroundSize: '100px 100px',
                    fontFamily: 'sans-serif',
                }}
            >
                {/* Glow Effect Behind Logo */}
                <div
                    style={{
                        position: 'absolute',
                        width: '600px',
                        height: '600px',
                        background: 'radial-gradient(circle, rgba(57,255,20,0.15) 0%, rgba(0,0,0,0) 70%)',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                    }}
                />

                {/* Brand Name */}
                <div
                    style={{
                        fontSize: 70,
                        fontWeight: 900,
                        color: 'white',
                        letterSpacing: '-2px',
                        marginBottom: 20,
                        textShadow: '0 0 40px rgba(57,255,20,0.5)',
                        display: 'flex',
                        alignItems: 'center',
                    }}
                >
                    AQT <span style={{ color: '#39FF14', marginLeft: 15 }}>//</span> TERMINAL
                </div>

                {/* Subtitle */}
                <div
                    style={{
                        fontSize: 30,
                        color: '#888',
                        letterSpacing: '4px',
                        textTransform: 'uppercase',
                    }}
                >
                    Quantum Intelligence System
                </div>

                {/* Status Badge */}
                <div
                    style={{
                        marginTop: 40,
                        padding: '10px 30px',
                        backgroundColor: 'rgba(57, 255, 20, 0.1)',
                        border: '1px solid #39FF14',
                        borderRadius: '50px',
                        color: '#39FF14',
                        fontSize: 20,
                        display: 'flex',
                        alignItems: 'center',
                    }}
                >
                    <div style={{ width: 10, height: 10, background: '#39FF14', borderRadius: '50%', marginRight: 10 }} />
                    SYSTEM ONLINE
                </div>
            </div>
        ),
        {
            width: 1200,
            height: 630,
        },
    );
}
