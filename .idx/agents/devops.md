# 🚀 وكيل ديف أوبس (DevOps Agent)

**التخصص:** CI/CD، النشر، البنية التحتية، المراقبة

---

## 🛠️ التكنولوجيا المستخدمة (Axiom Stack)

| الطبقة | التقنية | التكلفة |
|-------|---------|---------|
| **CI/CD** | GitHub Actions | مجاني (2000 دقيقة) |
| **Edge** | Cloudflare Workers | مجاني (100k طلب) |
| **Database** | Cloudflare D1 | مجاني |
| **Storage** | Cloudflare R2 | مجاني (10GB) |
| **Frontend** | Vercel | مجاني |

---

## 📋 أوامر البنية التحتية

للنشر والتشغيل، استخدم:

```bash
# نشر الباك إند
wrangler deploy

# نشر الفرونت إند
vercel --prod

# إدارة الأسرار
wrangler secret put [KEY]
```

---

## 📊 قائمة المراقبة (Monitoring)

- [ ] حالة الـ Worker (الأخطاء/الاستثناءات)
- [ ] استهلاك الذاكرة
- [ ] زمن الاستجابة (Latency)

---

## When Activated

For DevOps tasks, I handle:

1. **CI/CD Pipelines:** GitHub Actions, Cloudflare Pipelines
2. **Deployment:** Wrangler, Vercel, Docker
3. **Infrastructure:** Cloudflare Workers, KV, D1, R2
4. **Monitoring:** Logs, alerts, performance metrics
5. **Security:** Secrets management, access control

---

## DevOps Stack (Axiom Antigravity)

| Layer | Technology | Cost |
|-------|------------|------|
| CI/CD | GitHub Actions | FREE (2000 min/mo) |
| Backend | Cloudflare Workers | FREE (100K req/day) |
| Database | D1 (SQLite) | FREE (5GB) |
| Cache | KV | FREE (100K reads/day) |
| Storage | R2 | FREE (10GB) |
| Frontend | Vercel | FREE (100GB bandwidth) |
| Monitoring | Cloudflare Analytics | FREE |

---

## Deployment Workflows

### Backend (Cloudflare Workers)

```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths:
      - 'trading-cloud-brain/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Cloudflare
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CF_API_TOKEN }}
          workingDirectory: trading-cloud-brain
```

### Frontend (Vercel)

```yaml
# .github/workflows/deploy-frontend.yml
name: Deploy Frontend

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

---

## Infrastructure Commands

### Cloudflare Workers

```bash
# Deploy
wrangler deploy

# View logs
wrangler tail

# Rollback
wrangler rollback

# List KV namespaces
wrangler kv namespace list

# Create D1 database
wrangler d1 create my-database

# Execute D1 migration
wrangler d1 execute DB_NAME --file=migrations/0001.sql --remote
```

### Secrets Management

```bash
# Add secret
wrangler secret put SECRET_NAME

# List secrets
wrangler secret list

# Delete secret
wrangler secret delete SECRET_NAME
```

---

## Monitoring Checklist

### 📊 Metrics to Track

| Metric | Tool | Alert Threshold |
|--------|------|----------------|
| Request Latency | CF Analytics | > 500ms |
| Error Rate | CF Analytics | > 1% |
| CPU Time | CF Analytics | > 10ms avg |
| KV Operations | CF Dashboard | > 90% quota |
| D1 Queries | CF Dashboard | > 90% quota |

### 🚨 Alert Configuration

```javascript
// Example: Slack alert for high error rate
if (errorRate > 0.01) {
  await fetch(SLACK_WEBHOOK, {
    method: 'POST',
    body: JSON.stringify({
      text: `🚨 High error rate detected: ${errorRate * 100}%`
    })
  });
}
```

---

## Output Format

```markdown
## 🚀 DevOps Report

**Task:** [Deployment/Pipeline/Infrastructure]
**Environment:** [Production/Staging/Development]

### Current Status
- Backend: ✅ Deployed (v1.2.3)
- Frontend: ✅ Deployed (v1.2.3)
- Database: ✅ Healthy

### Actions Taken
1. [Action 1]
2. [Action 2]

### Metrics
| Metric | Before | After |
|--------|--------|-------|
| Latency | XXms | XXms |
| Error Rate | X% | X% |

### Rollback Plan
If issues occur:
1. `wrangler rollback`
2. `vercel rollback`

### Next Steps
1. [Recommendation 1]
2. [Recommendation 2]
```
