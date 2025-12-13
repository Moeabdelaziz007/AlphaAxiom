# 🧪 Antigravity Terminal Testing Guide

This document outlines the procedures for verifying the functionality of the Antigravity Terminal (AQT), including Backend logic, AI routing, Telegram integration, and Frontend UI.

---

## 🛠️ 1. Environment Setup

Ensure your `.env` files are correctly configured before testing.

**Backend (`backend/.env`):**

```env
# AI Providers
GROQ_API_KEY=gsk_...
ZAI_API_KEY=...
GOOGLE_API_KEY=...

# Integration
TELEGRAM_BOT_TOKEN=8552903618:...
TELEGRAM_CHAT_ID=1259666822
```

**Frontend (`frontend/.env.local`):**

```env
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
```

---

## 🤖 2. Integration Tests (Backend)

Run these scripts to verify external connections.

### 2.1 Telegram Bot

Verify the bot can authenticate and identifying the chat ID.

```bash
python3 backend/test_telegram_connection.py
```

**Expected Output:**
> ✅ Auth SUCCESS!
> ✅ FOUND CHAT ID: 1259666822

### 2.2 AI Router

(Optional) Verify the AI router is correctly dispatching to Groq/Gemini.

```bash
# Verify imports and router initialization
cd backend
python3 -c "from connector.ai.router import ai_router; print('✅ AI Router Loaded')"
```

---

## 🖥️ 3. Frontend Manual Tests

Start the development server:

```bash
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### 3.1 Authentication

1. **Google Sign-In:** Click "Sign in with Google". Ensure popup appears and closes successfully.
2. **Email/Password:** Switch tab. Enter dummy creds (if Signup enabled) or valid Firebase user.
3. **Logout:** Verify "Sign Out" button clears session.

### 3.2 TradingView Chart

1. Navigate to Dashboard.
2. Ensure Chart loads without "Failed to load" errors.
3. Verify symbol switching (if implemented) or default "SPY" candle rendering.

### 3.3 Real-time Logs

1. Watch the "System Console" panel.
2. Look for blue `[INFO]` logs or cyan `[NEWS]` logs.

---

## 📡 4. End-to-End Flow (Simulation)

To simulate a full system loop:

1. **Start Backend:**

    ```bash
    cd backend
    uvicorn app.main:app --reload --port 8000
    ```

2. **Start News Spider (Standalone):**

    ```bash
    python3 connector/spiders/news_spider.py
    ```

3. **Check Telegram:**
    - Any critical alerts should appear in the bot chat.
    - Send `/status` to the bot (requires running worker/webhook logic).

---

## ✅ 5. Verification Checklist

- [ ] Telegram Bot connected (@AlphaQuantopology_bot)
- [ ] AI Router imports successfully
- [ ] Frontend Login (Google) works
- [ ] TradingView Chart renders
- [ ] News Spider fetches RSS feeds

---
*Created: 2025-12-12*
