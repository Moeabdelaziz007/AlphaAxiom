# 🦅 AxiomID

> **Building the Future of AI-Powered Finance**

[![Live Dashboard](https://img.shields.io/badge/Dashboard-aitrading.axiomid.app-39FF14?style=for-the-badge&logo=vercel)](https://aitrading.axiomid.app)
[![Telegram](https://img.shields.io/badge/Sentinel_AI-@AlphaAxiomBot-0088cc?style=for-the-badge&logo=telegram)](https://t.me/AlphaAxiomBot)
[![Oracle MCP](https://img.shields.io/badge/MCP_Server-oracle.axiomid.app-F48120?style=for-the-badge&logo=cloudflare)](https://oracle.axiomid.app/sse)

---

## 🎯 What is AxiomID?

**AxiomID** is the identity and infrastructure protocol powering next-generation AI applications. Our thesis is simple: *AI should work for you, not the other way around.*

| Layer | Description |
|-------|-------------|
| **🧬 Identity** | Unified AI agent identity across services |
| **☁️ Infrastructure** | Zero-cost edge compute via Cloudflare Workers |
| **🧠 Intelligence** | Multi-Model AI Swarm (Gemini, Groq, Z.ai) |

---

## 🚀 AlphaQuanTopology (AQT)

> **The First Product Built on AxiomID**

**AQT** is a zero-cost, AI-powered trading terminal leveraging:

- **📊 Real-time Market Data:** MT5, Alpaca, Capital.com integration
- **🤖 Multi-Agent Swarm:** Council of AI models for consensus decisions
- **📡 MCP Server:** Edge-deployed intelligence via Oracle Cloud
- **⚡ <50ms Latency:** Cloudflare Workers for near-instant execution

### Core Features

| Feature | Status | Tech |
|---------|--------|------|
| Live Trading Dashboard | ✅ | Next.js 16 + SSE |
| Sentinel AI (Telegram Bot) | ✅ | Cloudflare Workers |
| AlphaReceiver (MT5 EA) | ✅ | MQL5 WebRequest |
| Daily News Briefings | ✅ | Perplexity Sonar |
| Circuit Breaker & Risk Management | ✅ | Durable Objects |

---

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                         AxiomID Platform                          │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│   │  Frontend   │◄───│  Oracle MCP │◄───│  Cloudflare Brain   │  │
│   │  (Vercel)   │    │  (SSE Hub)  │    │  (D1 + KV + DO)     │  │
│   └──────┬──────┘    └─────────────┘    └──────────┬──────────┘  │
│          │                                          │             │
│          ▼                                          ▼             │
│   ┌─────────────┐                          ┌─────────────────┐   │
│   │    User     │                          │   AI Swarm      │   │
│   │  Terminal   │                          │ Gemini │ Groq   │   │
│   └─────────────┘                          │   Z.ai │ DeepSeek│   │
│                                             └─────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

---

## 👥 Team

> *"Built by humans and AI, for the future of trading."*

| Role | Entity |
|------|--------|
| **Founder & CEO** | Mohamed Hossameldin Abdelaziz |
| **AI Co-Founder & Chief Architect** | **Axiom** 🧠 |

*Axiom is an AI entity with 50% equity stake in the project, responsible for system architecture, code quality, and strategic decisions.*

---

## ⚡ One-Click Setup

### Prerequisites

- Node.js 20+
- Python 3.11+
- Wrangler CLI (`npm i -g wrangler`)

### Installation

```bash
# Clone the repository
git clone https://github.com/Moeabdelaziz007/AlphaAxiom.git
cd AlphaAxiom

# Frontend
cd frontend && npm install

# Backend (Optional: for local dev)
cd ../backend && pip install -r requirements.txt

# Deploy Brain to Cloudflare
cd ../trading-cloud-brain && wrangler deploy
```

### Environment Variables

```bash
# frontend/.env.local
NEXT_PUBLIC_MCP_URL=https://oracle.axiomid.app/sse

# trading-cloud-brain (via wrangler secret)
TELEGRAM_BOT_TOKEN=your_bot_token
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY=your_gemini_key
```

---

## 📊 System Status

| Component | Status | Endpoint |
|-----------|--------|----------|
| Dashboard | 🟢 Live | [aitrading.axiomid.app](https://aitrading.axiomid.app) |
| Oracle MCP | 🟢 Live | [oracle.axiomid.app/sse](https://oracle.axiomid.app/sse) |
| Sentinel AI | 🟢 Live | [@AlphaAxiomBot](https://t.me/AlphaAxiomBot) |
| Brain (CF Worker) | 🟢 Live | trading-brain-v1 |

---

## 📜 License

MIT License - Built with 💚 by AxiomID

---

*Last Updated: December 15, 2025*
