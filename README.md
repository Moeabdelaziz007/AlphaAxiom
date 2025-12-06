# 🚀 Quantum Trading Terminal v0.1

<div align="center">

![Trading Terminal](https://img.shields.io/badge/Status-Demo%20Ready-00ff9d?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-000000?style=for-the-badge&logo=next.js)
![Docker](https://img.shields.io/badge/Deploy-Docker-2496ED?style=for-the-badge&logo=docker)

**نظام تداول متعدد الأصول مع واجهة Hedge Fund Terminal**

</div>

---

## ✨ المميزات

| الميزة | الوصف |
|--------|-------|
| 📈 **تداول متعدد الأصول** | أسهم، ذهب، عملات رقمية |
| ⚡ **تحديثات لحظية** | WebSocket للأسعار والصفقات |
| 🤖 **Sentinel AI** | سجلات ذكاء اصطناعي للتحليل |
| 💎 **تصميم Glassmorphism** | واجهة فاخرة بتأثيرات النيون |
| 🐳 **Docker Ready** | تشغيل بأمر واحد |

---

## 🚀 التشغيل السريع

### المتطلبات

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)

### الخطوات

```bash
# 1. استنسخ المشروع
git clone <repository-url>
cd Trading.System-0.1

# 2. أنشئ ملف البيئة
cp backend/.env.example backend/.env

# 3. شغّل النظام
docker compose up --build
```

### الوصول

- **Frontend**: <http://localhost:3000>
- **Backend API**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>

---

## ⚙️ إعداد Alpaca Paper Trading

1. أنشئ حساب مجاني على [Alpaca](https://alpaca.markets/)
2. انتقل إلى **Paper Trading** → **API Keys**
3. انسخ المفاتيح إلى `backend/.env`:

```env
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

> 💡 **ملاحظة**: حساب Paper Trading يأتي برصيد تجريبي $100,000

---

## 📁 بنية المشروع

```
Trading.System-0.1/
├── 🐳 docker-compose.yml      # تنسيق Docker
├── 📂 backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env                   # مفاتيح API (لا ترفعها لـ Git!)
│   └── app/
│       └── main.py            # FastAPI Server
├── 📂 frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.ts     # ألوان النيون
│   └── src/
│       ├── app/
│       │   ├── page.tsx       # Dashboard الرئيسي
│       │   └── globals.css    # Glassmorphism CSS
│       ├── components/
│       │   └── Dashboard/
│       │       ├── LivePrice.tsx
│       │       ├── MainChart.tsx
│       │       ├── MomentumGauge.tsx
│       │       ├── SentinelAI.tsx
│       │       └── ConnectionHeartbeat.tsx
│       ├── hooks/
│       │   └── useMarketData.ts
│       └── lib/
│           ├── api.ts
│           └── types.ts
└── 📄 README.md
```

---

## 🎨 نظام التصميم

### ألوان النيون

| اللون | الكود | الاستخدام |
|-------|-------|-----------|
| 🔵 Neon Cyan | `#00f2ea` | أوامر، حدود |
| 🟢 Neon Green | `#00ff9d` | ربح، صعود |
| 🔴 Neon Red | `#ff0055` | خسارة، هبوط |
| 🟡 Neon Gold | `#ffd700` | ذهب، تحذيرات |

### CSS Classes

```css
.glass-panel      /* خلفية زجاجية */
.neon-border      /* حدود نيون سماوي */
.glow-cyan        /* توهج نصي سماوي */
.price-up         /* حركة صعود السعر */
.price-down       /* حركة هبوط السعر */
.heartbeat        /* نبض الاتصال */
```

---

## 🔌 API Endpoints

| Method | Endpoint | الوصف |
|--------|----------|-------|
| GET | `/api/status` | حالة النظام |
| GET | `/api/market/{symbol}` | بيانات السوق |
| GET | `/api/account` | معلومات الحساب |
| POST | `/api/trade` | تنفيذ صفقة |
| GET | `/api/positions` | الصفقات المفتوحة |
| DELETE | `/api/positions` | إغلاق جميع الصفقات |
| WS | `/ws` | WebSocket للتحديثات |

---

## 🧪 الاختبار

```bash
# اختبار Backend
cd backend
pytest

# اختبار Frontend (Playwright)
cd frontend
npx playwright test
```

---

## 📞 الدعم

للمساعدة أو الاستفسارات:

- 📧 Email: <support@trading-system.com>
- 💬 Telegram: @TradingSupport

---

## ⚠️ تنبيه قانوني

هذا النظام للأغراض التعليمية والتجريبية فقط. التداول ينطوي على مخاطر مالية عالية. لا نتحمل أي مسؤولية عن الخسائر الناتجة عن استخدام هذا النظام.

---

<div align="center">

**صُنع بـ ❤️ باستخدام Gemini AI + FastAPI + Next.js**

</div>
