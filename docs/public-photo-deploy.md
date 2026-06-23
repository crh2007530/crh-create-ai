# Public Photo Solve Deployment

目标：普通用户打开网站后，不需要填写 API Key，也可以拍照识别线代题。

## Required Architecture

不要使用纯 GitHub Pages 静态站承载拍题识别。图片识别需要后端代理：

```txt
User phone
-> Next.js frontend
-> FastAPI backend
-> OpenAI-compatible provider
-> Problem Parser / Math Engine / Teaching SVG
```

## Backend

Deploy `apps/api` to Render or another Python web service.

Required environment variables:

```txt
CUSTOM_API_KEY=<set in hosting dashboard, never commit>
CUSTOM_BASE_URL=https://ai-pixel.online
CUSTOM_MODEL=gpt-4o-mini
API_CORS_ORIGIN=*
```

Health check:

```txt
https://YOUR_API_HOST/health
```

## Frontend

Deploy `apps/web` to Vercel or another Next.js host.

Required environment variable:

```txt
NEXT_PUBLIC_API_URL=https://YOUR_API_HOST
```

Do not set:

```txt
NEXT_PUBLIC_LOCAL_SOLVER=true
```

That mode disables server-side photo recognition and is only for static preview.

## User Flow

```txt
Open website
-> Tap photo
-> Start solving
-> Backend extracts text
-> Linear algebra parser runs
-> Math engine calculates
-> Teaching SVG steps show
```

## Security

Do not put provider API keys in frontend code, GitHub Pages variables, or `NEXT_PUBLIC_*` variables.

Only store the key as a backend environment variable.
