# PDF360 — Production Deployment Guide (Render + Neon PostgreSQL)

This guide covers deploying PDF360 to **Render.com** using the provided Infrastructure as Code blueprint (`render.yaml`), connecting to a **Neon Free PostgreSQL** database, and configuring optional S3/Cloudflare R2 storage.

---

## Architecture Overview

```
                      ┌──────────────────────┐
                      │   Next.js Frontend   │
                      │ (Render Web Service) │
                      └──────────┬───────────┘
                                 │ HTTPS / API
                                 ▼
                      ┌──────────────────────┐
                      │   FastAPI Backend    │
                      │ (Render Web Service) │
                      └────┬────────────┬────┘
                           │            │
            Celery Tasks   │            │ DB Queries (SSL)
                           ▼            ▼
┌──────────────────────────────┐     ┌──────────────────────────────┐
│        Celery Worker         │     │       Neon PostgreSQL        │
│    (Render Worker Service)   │     │    (Serverless Database)     │
└──────────────┬───────────────┘     └──────────────────────────────┘
               │
               ▼ Redis Broker
┌──────────────────────────────┐
│         Render Redis         │
│   (In-memory Queue Service)  │
└──────────────────────────────┘
```

---

## 1. Prerequisites

1. **GitHub Account**: Your repository pushed to GitHub (`https://github.com/Al-Ahotanee/PDF360.git`).
2. **Neon Account** ([neon.tech](https://neon.tech)): Free serverless PostgreSQL database.
3. **Render Account** ([render.com](https://render.com)): Free cloud hosting platform.

---

## 2. Set Up Free Neon PostgreSQL

1. Log in to [Neon](https://console.neon.tech).
2. Click **Create Project** -> Name it `pdf360`.
3. In your Neon Dashboard, find your **Connection Details**:
   - Select **Pooled connection** (recommended for serverless FastAPI/Celery).
   - Copy the PostgreSQL connection string. It will look like:
     ```
     postgresql://alex:AbCdEf123456@ep-cool-fog-123456-pooler.us-east-2.aws.neon.tech/pdf360?sslmode=require
     ```
4. Keep this connection string ready for Step 3.

---

## 3. One-Click Blueprint Deployment on Render

1. Log in to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** in the top navigation and select **Blueprint**.
3. Connect your GitHub account and select your repository: **`Al-Ahotanee/PDF360`**.
4. Render will parse `render.yaml` and display the **100% Free** stack components:
   - `pdf360-api` (Free Web Service — FastAPI + Embedded Celery Worker + Redis)
   - `pdf360-frontend` (Free Web Service — Next.js)
   *(Because both services use Render's Free tier, Render will NOT require credit card details).*
5. In the Blueprint form:
   - Under **`pdf360-api`**, paste your Neon **`DATABASE_URL`** copied from Step 2.
   - Under **`pdf360-frontend`**, you can provide your **`NEXT_PUBLIC_API_BASE_URL`** (e.g. `https://pdf360-api.onrender.com/api/v1` or configure it after deploy).
6. Click **Apply**.
7. Render will build and deploy both services completely free of charge!

---

## 4. What Happens on Startup

1. **Automatic Database Migrations**:
   The `backend/Dockerfile` automatically runs:
   ```bash
   alembic upgrade head
   python -m app.db.seed
   ```
   This creates all required PostgreSQL tables (`users`, `roles`, `files`, `file_shares`, `jobs`, `comments`, etc.) and seeds default roles (`registered_user`, `admin`, etc.) with their permissions.

2. **FastAPI Web Service**:
   Binds dynamically to the port provided by Render (`$PORT`) on `0.0.0.0` and answers `/api/health`.

3. **Next.js Frontend**:
   Binds dynamically to its assigned port and connects to the public URL of `pdf360-api`.

---

## 5. Persistent Cloud Storage (Cloudflare R2 / AWS S3)

By default, PDF360 uses local storage (`STORAGE_PROVIDER=local`) inside the container at `/app/storage`.

For production deployments where file uploads need to persist across container restarts without paid Render Disks, configure S3-compatible cloud storage (e.g. Cloudflare R2 free tier with 10GB free storage and zero egress fees):

In your Render dashboard for both `pdf360-api` and `pdf360-worker`, set these environment variables:

| Variable | Description | Example (Cloudflare R2) |
|---|---|---|
| `STORAGE_PROVIDER` | Set to `s3` | `s3` |
| `S3_BUCKET_NAME` | Bucket name | `pdf360-uploads` |
| `S3_ACCESS_KEY` | Access key ID | `7a8b...` |
| `S3_SECRET_KEY` | Secret access key | `9f0e...` |
| `S3_ENDPOINT_URL` | S3 API endpoint | `https://<account_id>.r2.cloudflarestorage.com` |
| `S3_REGION` | Region (optional for R2) | `auto` |

---

## 6. Verifying the Deployment

1. **API Health**:
   Visit `https://<your-pdf360-api>.onrender.com/api/health`. It should return:
   ```json
   {"status":"ok","app":"PDF360","env":"production"}
   ```
2. **Interactive Swagger Docs**:
   Visit `https://<your-pdf360-api>.onrender.com/api/docs` to test all 90+ endpoints directly.
3. **Frontend Application**:
   Visit `https://<your-pdf360-frontend>.onrender.com` to register an account, upload files, and collaborate!
