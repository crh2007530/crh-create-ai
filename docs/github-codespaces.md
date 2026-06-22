# GitHub Codespaces Trial URL

Use this path when Docker is too much for early testers.

## What the tester does

1. Open the GitHub repository.
2. Click `Code`.
3. Click `Codespaces`.
4. Click `Create codespace on main`.
5. Wait for setup to finish.
6. Open the forwarded port `3000`.

GitHub will give a URL like:

```txt
https://YOUR-CODESPACE-NAME-3000.app.github.dev
```

That is the development website URL you can send to testers.

## What starts automatically

Codespaces runs:

```txt
FastAPI -> 0.0.0.0:8000
Next.js -> 0.0.0.0:3000
```

The browser only needs the `3000` URL. Next.js proxies API calls through:

```txt
/api/backend/* -> http://127.0.0.1:8000/*
```

## Logs

Inside Codespaces:

```bash
cat .devcontainer/logs/api.log
cat .devcontainer/logs/web.log
```

## API keys

The deterministic visual math flow works without model keys. For real model calls, create `.env` from `.env.example` and add keys:

```bash
cp .env.example .env
```

Then fill:

```txt
OPENAI_API_KEY=
GEMINI_API_KEY=
DEEPSEEK_API_KEY=
```

Restart the codespace after changing environment values.
