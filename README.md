# crh create AI V2

工科版 Photomath：面向电路分析和线性代数的 AI 可视化解题平台。

V2 当前是可运行 MVP 工程，不再是单页 Demo：

- Next.js 15 + TypeScript + Tailwind frontend
- FastAPI backend
- AI Gateway with OpenAI / Gemini / DeepSeek provider routing
- DeepSeek vision bridge design
- Per-step SVG visualization
- Circuit and matrix sample solvers

## Public Website For Testers

Use this when you want anyone to open the site on phone or desktop.

Recommended:

```txt
Frontend: Vercel
Backend: Render
Tester URL: https://YOUR_SITE.vercel.app
```

Deployment guide: `docs/public-hosting.md`.

## GitHub Codespaces Trial URL

Use this if Docker is not convenient for testers.

1. Push this project to GitHub.
2. Open the repository on GitHub.
3. Click `Code` -> `Codespaces` -> `Create codespace on main`.
4. Wait for setup.
5. Open forwarded port `3000`.

GitHub will provide a URL like:

```txt
https://YOUR-CODESPACE-NAME-3000.app.github.dev
```

More details: `docs/github-codespaces.md`.

## Docker Trial Deploy

Use this when you want someone else to try the site.

```powershell
Copy-Item .env.deploy.example .env
docker compose -f docker-compose.prod.yml up --build -d
```

Open:

```txt
http://localhost:3000
```

For public access on a server, open `3000/tcp` and visit:

```txt
http://YOUR_SERVER_IP:3000
```

More details: `docs/deployment.md`.

## Run API

```powershell
cd apps/api
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Run Web

```powershell
cd apps/web
npm install
npm run dev
```

Open:

```txt
http://localhost:3000
```

## Environment

Copy `.env.example` to `.env`.

The MVP works without API keys by returning deterministic visual steps. After setting keys, provider adapters can be extended to call real model APIs.

```txt
OPENAI_API_KEY=
GEMINI_API_KEY=
DEEPSEEK_API_KEY=
```

## Product Rule

The answer is not the center.

Each step must include:

- step title
- formula
- short teacher explanation
- synchronized SVG visualization

For image input with DeepSeek selected:

```txt
image -> OpenAI/Gemini vision bridge -> structured text/netlist -> DeepSeek reasoning
```

This prevents sending raw images to a model that does not support vision.
