# 📖 Axiom Antigravity - API Documentation

> Cloud Brain API v2.0 | Base URL: `https://trading-brain-v1.amrikyy.workers.dev`

---

## 🔐 Authentication

| Type | Header | Description |
|------|--------|-------------|
| **Public** | None | Endpoints in `public_paths` |
| **Protected** | `X-System-Key` | Sensitive operations |

```bash
# Protected endpoint example
curl -H "X-System-Key: YOUR_SECRET" \
  https://trading-brain-v1.amrikyy.workers.dev/api/trade?symbol=SPY&side=buy&qty=1
```

---

## 📡 REST Endpoints

### Status

```http
GET /api/status
```

**Response:**

```json
{
  "status": "online",
  "version": "2.0",
  "name": "Antigravity MoE Brain",
  "ai": "Groq Router + Gemini RAG",
  "database": "D1 Connected",
  "broker": "Alpaca Paper",
  "trades_today": 5,
  "max_trades": 20
}
```

---

### Chat (MoE Router)

```http
POST /api/chat
Content-Type: application/json
```

**Request:**

```json
{
  "message": "Analyze AAPL"
}
```

**Response Types:**

| Type | Trigger | Description |
|------|---------|-------------|
| `RESEARCH` | "Analyze X" | Gemini RAG analysis |
| `SHOW_CHART` | "Show chart" | Returns candle data |
| `TRADE` | "Buy/Sell X" | Executes trade |
| `CHAT` | General | Groq conversation |

---

### Market Snapshot

```http
GET /api/market?symbols=EURUSD,GBPUSD,XAUUSD
```

**Response:**

```json
{
  "EURUSD": {
    "price": 1.0875,
    "change_percent": 0.15,
    "high": 1.0892,
    "low": 1.0845
  }
}
```

---

### Candles (Chart Data)

```http
GET /api/candles?symbol=EURUSD&timeframe=1h
```

**Parameters:**

| Param | Default | Options |
|-------|---------|---------|
| `symbol` | Required | Any traded symbol |
| `timeframe` | `1h` | `1m`, `5m`, `15m`, `1h`, `1d` |

---

### Account

```http
GET /api/account
```

**Response:**

```json
{
  "balance": 10000.00,
  "equity": 10250.50,
  "margin_used": 500.00,
  "source": "Capital.com Demo"
}
```

---

### Positions

```http
GET /api/positions
```

**Response:**

```json
[
  {
    "symbol": "EURUSD",
    "side": "BUY",
    "size": 1000,
    "entry_price": 1.0850,
    "current_price": 1.0875,
    "pnl": 25.00
  }
]
```

---

### Execute Trade 🔐

```http
GET /api/trade?symbol=EURUSD&side=buy&qty=1
```

**Parameters:**

| Param | Required | Options |
|-------|----------|---------|
| `symbol` | ✓ | Any symbol |
| `side` | ✓ | `buy`, `sell` |
| `qty` | ✓ | Number |

**Routing Logic:**

- Forex pairs (6 chars, `/`, `USD`) → Capital.com
- Stocks/Crypto → Alpaca

---

### Panic Protocol 🔐 ☢️

```http
GET /api/panic
```

Immediately liquidates ALL open positions. Sends Telegram alert.

---

### Ably Token

```http
GET /api/ably/auth
```

Returns token for real-time subscriptions.

---

## 📱 Telegram Bot

### Webhook URL

```
POST /telegram/webhook
```

Set via:

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d '{"url": "https://trading-brain-v1.amrikyy.workers.dev/telegram/webhook"}'
```

### Commands

| Command | Description | AI Used |
|---------|-------------|---------|
| `/start` | Welcome message | - |
| `/status` | System status + panic mode | - |
| `/balance` | Portfolio value | - |
| `/positions` | Open trades | - |
| `/stoptrade` | 🛑 Kill switch ON | - |
| `/starttrade` | ▶️ Resume trading | - |
| `/ai [text]` | Quick AI (FREE) | Workers AI |
| `/analyze [type] [text]` | Deep analysis | DeepSeek |

### Analysis Types

```
/analyze sentiment البنك المركزي يرفع الفائدة
/analyze signal الذهب يرتفع بسبب التضخم
/analyze risk تحليل مخاطر EURUSD
/analyze summary أخبار السوق اليوم
```

---

## 🔑 Required Secrets

```bash
# Set via wrangler CLI
wrangler secret put TELEGRAM_BOT_TOKEN
wrangler secret put TELEGRAM_CHAT_ID
wrangler secret put GROQ_API_KEY
wrangler secret put DEEPSEEK_API_KEY
wrangler secret put CAPITAL_API_KEY
wrangler secret put CAPITAL_EMAIL
wrangler secret put CAPITAL_PASSWORD
wrangler secret put ABLY_API_KEY
```

---

## 📊 Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `401` | Unauthorized (missing X-System-Key) |
| `500` | Server error |

---

*Generated: 2025-12-08*
