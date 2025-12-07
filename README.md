# 🌌 Antigravity Terminal v3.0 (Twin-Turbo Edition)
### The Autonomous Market Intelligence System | نظام الاستخبارات السوقية المستقل

![Status](https://img.shields.io/badge/System-Operational-success)
![Language](https://img.shields.io/badge/Languages-English_%7C_%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-blue)
![Architecture](https://img.shields.io/badge/Architecture-Serverless_Edge-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Table of Contents | جدول المحتويات

1. [Overview | نبذة عامة](#-overview--نبذة-عامة)
2. [System Architecture | المعمارية التقنية](#-system-architecture--المعمارية-التقنية)
3. [The Twin-Turbo Engine | محرك التيربو المزدوج](#-the-twin-turbo-engine--محرك-التيربو-المزدوج)
4. [Implementation Plan | خطة التنفيذ](#-implementation-plan--خطة-التنفيذ)
5. [Data & Operations | البيانات والتشغيل](#-data--operations--البيانات-والتشغيل)
6. [Author | المؤلف](#-author--المؤلف)
7. [License | الترخيص](#-license--الترخيص)

---

## 🌍 Overview | نبذة عامة

### English
Antigravity Terminal v3.0 is not a traditional trading bot. It is an Artificial Market Lifeform designed to live on the Cloudflare Edge network. Unlike standard systems that rely on single indicators or expensive servers, this system operates with zero latency (<10ms) and zero operational cost.

The v3.0 upgrade introduces the "Twin-Turbo Engine": a dual-core mathematical system combining Statistical Precision (AEXI) with Chaos Theory (Dream Machine). The system is governed by a Mixture of Experts (MoE) AI brain that validates every signal against real-time global news before execution, ensuring institutional-grade performance.

### العربية
يمثل Antigravity Terminal v3.0 نقلة نوعية في عالم التداول الخوارزمي. هو ليس مجرد "بوت تداول" تقليدي، بل هو "كيان سوقي اصطناعي" مصمم ليعيش ويعمل على شبكة Cloudflare Edge، بسرعة استجابة فورية وتكلفة تشغيلية صفرية.

يقدم الإصدار 3.0 "محرك التيربو المزدوج": نظام رياضي ثنائي النواة يجمع بين الدقة الإحصائية (AEXI) و نظرية الفوضى (Dream Machine). يخضع النظام لإدارة "عقل الخبراء المختلط" (MoE) الذي يتحقق من كل إشارة مقابل الأخبار العالمية اللحظية قبل التنفيذ، مما يضمن أداءً مؤسسياً.

---

## 🏗️ System Architecture | المعمارية التقنية

The system utilizes a Serverless, Edge-Native architecture. يعتمد النظام على بنية "بدون خادم" (Serverless) موزعة على الحافة.

``mermaid
graph TD
    Cron[⏰ Cron Trigger (1 Min)] -->|Wake Up| Dispatcher[Cloudflare Worker]
    Dispatcher -->|Spawn| DO_BTC[🛡️ Sentinel: BTC]
    Dispatcher -->|Spawn| DO_SPY[🛡️ Sentinel: SPY]
    
    subgraph "Twin-Turbo Engine (Inside Sentinel)"
        DO_BTC -->|Data Fetch| Cache[(KV Store)]
        Cache -- Stale --> API[Alpaca/CoinGecko]
        Cache -- Fresh --> Math[Calc Engines]
        
        Math -->|Engine A| AEXI[AEXI (Precision)]
        Math -->|Engine B| Dream[Dream Machine (Chaos)]
        
        AEXI & Dream -->|Signal?| AI_Gate[🧠 Groq Router]
    end
    
    AI_Gate -- Approved --> Telegram[📱 Alert Bot]
    AI_Gate -- Approved --> DB[(🗄️ D1 Database)]
```

---

## 🏎️ The Twin-Turbo Engines | المحركات المزدوجة

The system identifies a "Money Glitch" only when both engines trigger simultaneously. يحدد النظام "الخلل المالي" فقط عندما يطلق كلا المحركين إشارة في آن واحد.

### 1. Engine A: AEXI (Precision) | المحرك أ: AEXI (الدقة)
**Logic**: Detects mathematical price exhaustion (Mean Reversion). **المنطق**: يكتشف الإرهاق السعري رياضياً (العودة للمتوسط).

* **EXH (Exhaustion)**: Z-Score deviation from the 100-period mean.
* **VAF (Acceleration)**: Momentum velocity relative to Volatility (ATR).
* **SVP (Volume)**: Relative volume spikes indicating institutional action.

### 2. Engine B: Dream Machine (Chaos) | المحرك ب: آلة الأحلام (الفوضى)
**Logic**: Detects structural anomalies via Physics & Chaos Theory. **المنطق**: يكتشف الشذوذ الهيكلي عبر الفيزياء ونظرية الفوضى.

* **Entropy**: Measures market disorder (Shannon Entropy).
* **Fractal Dimension**: Measures the roughness/complexity of price action.
* **Hurst Exponent**: Measures the "memory" of the trend (Mean reverting vs. Trending).

🔴 **The Signal Condition**: `AEXI > 80 AND Dream_Score > 75`.

---

## 🛠️ Expert Implementation Plan | خطة التنفيذ للمحترفين

### Phase 1: Infrastructure Genesis | البنية التحتية
* **Cloudflare Workers**: Initialize the execution engine.
* **D1 Database**: Create SQL schemas for trade_logs, rules, and system_state.
* **KV Storage**: Setup caching namespaces to reduce API load by 90%.
* **Durable Objects**: Configure MarketSentinel classes in wrangler.toml.

### Phase 2: The Twin Brain | المنطق البرمجي
* **Math Module**: Implement calculate_z_score, calculate_entropy, calculate_hurst in Pure Python (Pyodide).
* **Engine Integration**: Embed AEXI and Dream Machine logic within the Worker.
* **MoE Brain**: Integrate Groq API (Router) and Gemini API (Analyst) for signal validation.

### Phase 3: The Command Center | واجهة القيادة
* **Frontend**: Deploy Next.js 14 with Tailwind CSS on Vercel.
* **War Room**: Build the 4-grid synchronized chart interface.
* **Localization**: Implement next-intl for full Arabic RTL support.

### Phase 4: Activation | الإطلاق
* **Cron Trigger**: Set the heartbeat to `* * * * *` (Every Minute).
* **Telegram Hook**: Connect the bot for real-time mobile alerts.
* **Panic Protocol**: Activate the "Liquidate All" emergency endpoint.

---

## 📚 Data & Operations | البيانات والتشغيل

### Free Data Sources (Zero-Cost Strategy)
To maintain zero operational cost, the system aggregates multiple free sources:

* **Primary (Stocks)**: Alpaca Paper API (IEX Data).
* **Primary (Crypto)**: CoinGecko / Binance Public API.
* **News Intelligence**: Yahoo Finance RSS / Google News RSS.
* **Global/China**: AkShare / MCP Servers.

### Operations Maintenance
* **Smart Caching**: All market data is cached in KV for 60 seconds.
* **Database Pruning**: Auto-deletion of logs older than 30 days to respect D1 limits.
* **Error Handling**: "Safe Mode" activation upon API failure with auto-retry.

---

## 👨‍💻 Author & Contact | المؤلف ومعلومات الاتصال

**Mohamed Hossameldin Abdelaziz**  
Solo Full-Stack Developer & AI Systems Engineer  
Specializing in Artificial Intelligence System Architecture

This project was architected and developed by Mohamed Abdelaziz, leveraging cutting-edge Edge AI technologies to democratize institutional trading tools.

📧 **Email**: amrikyy@gmail.com | mabdela1@students.kennesaw.edu  
📱 **WhatsApp**: +17706160211  
📞 **Phone**: +201094228044

---

## ⚖️ License | الترخيص

**MIT License**

Copyright (c) 2025 Mohamed Hossameldin Abdelaziz

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

> For educational purposes only. Trade responsibly.  
> للأغراض التعليمية فقط. تداول بمسؤولية.