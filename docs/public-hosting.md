# Public Website Deployment

Goal: anyone can open one public website URL on phone or desktop.

Recommended early-trial setup:

```txt
Vercel public website
-> /api/backend/*
-> Render public FastAPI backend
```

The tester only opens the Vercel URL.

## 1. Push Project To GitHub

Create a GitHub repository and push the whole `crh-create-ai` folder.

## 2. Deploy Backend On Render

1. Open Render.
2. Create a new `Blueprint` or `Web Service`.
3. Connect the GitHub repository.
4. Use `render.yaml` if Render detects it.

Manual settings if needed:

```txt
Root Directory: apps/api
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

After deploy, Render gives an API URL like:

```txt
https://crh-create-ai-api.onrender.com
```

Test:

```txt
https://crh-create-ai-api.onrender.com/health
```

Expected:

```json
{"status":"ok"}
```

## 3. Deploy Frontend On Vercel

1. Open Vercel.
2. Import the same GitHub repository.
3. Use these settings:

```txt
Framework Preset: Next.js
Root Directory: apps/web
Build Command: npm run build
Output Directory: .next
Install Command: npm ci
```

4. Add environment variable:

```txt
API_INTERNAL_URL=https://YOUR_RENDER_API_URL
NEXT_PUBLIC_API_URL=/api/backend
```

Example:

```txt
API_INTERNAL_URL=https://crh-create-ai-api.onrender.com
NEXT_PUBLIC_API_URL=/api/backend
```

5. Deploy.

Vercel gives a website URL like:

```txt
https://crh-create-ai.vercel.app
```

This is the URL you send to testers.

## 4. Update Backend CORS

In Render environment variables, set:

```txt
API_CORS_ORIGIN=https://YOUR_VERCEL_SITE.vercel.app
```

Because the frontend uses a Vercel rewrite, most requests are same-origin from the browser, but keeping CORS accurate helps if you later call the API directly.

## 5. API Keys

The deterministic math and visual steps work without model keys.

For real model calls, add these in Render:

```txt
OPENAI_API_KEY=
GEMINI_API_KEY=
DEEPSEEK_API_KEY=
CUSTOM_API_KEY=
CUSTOM_BASE_URL=
CUSTOM_MODEL=
```

## 6. Tester Link

Send only the Vercel website URL:

```txt
https://crh-create-ai.vercel.app
```

Anyone can open it on mobile or desktop.
