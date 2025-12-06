
# 🌌 ANTIGRAVITY TERMINAL (v0.1)

### The Zero-Resistance, AI-Powered Autonomous Trading System

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-yellow.svg)
![Next.js](https://img.shields.io/badge/Frontend-Next.js_14-black)
![Cloudflare](https://img.shields.io/badge/Infrastructure-Cloudflare_Edge-orange)
![AI](https://img.shields.io/badge/Brain-DeepSeek_%2B_Gemini-magenta)

> **"Remove emotion from the equation. Trade with pure mathematics."**

---

## 🦅 Vision & Overview

**Antigravity Terminal** is an institutional-grade, multi-asset trading platform designed for the retail trader. It leverages a **Dual-Core AI Architecture** to analyze market momentum (The Antigravity Effect) and execute trades with surgical precision.

Unlike traditional bots that run on costly servers, Antigravity utilizes a **Serverless Edge Architecture** (Cloudflare Workers), allowing it to run **24/7 at $0.00 cost**.

---

## 🧠 The Dual-Core Brain Architecture

The system mimics a hedge fund's operating structure by splitting intelligence into two cores:

| Component | AI Model | Role | Function |
| :--- | :--- | :--- | :--- |
| **The Strategist** | **DeepSeek-V3** | Macro Analysis | Runs periodically on the Edge. Analyzes complex patterns, volume anomalies, and sets the daily bias (Bullish/Bearish). |
| **The Operator** | **Gemini 1.5 Flash** | Execution & Chat | Runs in real-time. Handles user interaction, executes orders instantly, and reacts to live price feeds. |

---

## ⚡ Key Capabilities

### 🖥️ 1. The Hedge Fund Dashboard (Frontend)

* **Tech:** Next.js 14, Tailwind CSS, Lightweight Charts.
* **Visuals:** "Midnight Black" glassmorphism UI with neon indicators.
* **Features:**
  * Live Tickers (Crypto, Stocks, Gold).
  * **Antigravity Gauge:** Visual representation of market momentum.
  * **Sentinel Chat:** Talk to your bot using natural language.

### ☁️ 2. Zero-Cost Edge Infrastructure (Backend)

* **Tech:** Cloudflare Workers (Python) + KV Store.
* **Mechanism:**
  * **Heartbeat Protocol:** A Cron Trigger wakes the bot every 60 seconds.
  * **Global State:** Strategy and open positions are stored in Cloudflare KV (Low latency database).
  * **No VPS Required:** No AWS EC2, no DigitalOcean. Pure serverless.

### 🛡️ 3. Risk Management Engine

* **Hard Stop:** Automatic Stop Loss placement on every trade.
* **Take Profit:** Trailing stop logic to maximize runs.
* **Panic Protocol:** One-click "Flatten All" button to liquidate positions instantly.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User[User Dashboard] -->|Chat & Commands| Cloudflare[Cloudflare Worker (Edge)]
    Cron[Cron Trigger (1 min)] -->|Wake Up Signal| Cloudflare
    
    subgraph "The Dual Brain"
        Cloudflare -->|Deep Analysis| DeepSeek[DeepSeek V3 API]
        Cloudflare -->|Fast Response| Gemini[Gemini Flash API]
    end
    
    subgraph "Execution"
        Cloudflare -->|Market Data| CoinGecko[Data Feeds]
        Cloudflare -->|Execute Orders| Alpaca[Alpaca/Jesse Exchange]
        Cloudflare -->|Store State| KV[(Cloudflare KV)]
    end
```

## 🚀 Quick Start Guide

### Prerequisites

* Node.js & npm
* Python 3.10+
* Cloudflare Account (Free Tier)
* API Keys (DeepSeek, Gemini, Alpaca)

### 1. Local Development (Docker Mode)

Run the full stack locally for testing and UI development.

```bash
# Clone the repo
git clone https://github.com/Moeabdelaziz007/Trading-Bot-System-v0.01.git
cd Trading-Bot-System-v0.01

# Setup Environment
cp .env.example backend/.env
# (Add your API keys in backend/.env)

# Launch System
docker-compose up --build
```

Access the dashboard at <http://localhost:3000>

### 2. Deploying the Brain to Cloudflare (24/7 Mode)

```bash
# Install Wrangler
npm install -g wrangler
wrangler login

# Deploy the Worker
cd trading-cloud-brain
npx wrangler deploy
```

## 📂 Project Structure

```plaintext
/
├── frontend/             # Next.js Dashboard (The Cockpit)
│   ├── src/components/   # UI Widgets (Charts, Chat, Stats)
│   └── src/hooks/        # Live Data Hooks
├── backend/              # Python FastAPI (Local Brain)
├── trading-cloud-brain/  # Cloudflare Worker (24/7 Edge Brain)
└── docker-compose.yml    # Orchestration
```

## ⚠️ Disclaimer

This software is for educational purposes only. Do not risk money you cannot afford to lose. The "Antigravity" algorithm does not guarantee profits. Use paper trading first.

---
Built with 💻 & ☕ by [Moe Abdelaziz]
