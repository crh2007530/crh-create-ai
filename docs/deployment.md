# Docker Trial Deployment

This guide is for letting other people try crh create AI from a public URL.

## One-command local trial

```powershell
Copy-Item .env.deploy.example .env
docker compose -f docker-compose.prod.yml up --build -d
```

Open:

```txt
http://localhost:3000
```

## Public server trial

1. Install Docker and Docker Compose on the server.
2. Copy this project folder to the server.
3. Copy `.env.deploy.example` to `.env`.
4. Put API keys into `.env` if you want real model calls. The deterministic math/visual flow still works without keys.
5. Start:

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

6. Open firewall/security group port:

```txt
3000/tcp
```

7. Visit:

```txt
http://YOUR_SERVER_IP:3000
```

## Public access design

Only the web service is exposed publicly.

```txt
Browser
-> http://YOUR_SERVER_IP:3000
-> Next.js /api/backend/* rewrite
-> Docker internal http://api:8000
-> FastAPI
```

This avoids asking testers to access a separate API port.

## Useful commands

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml restart
docker compose -f docker-compose.prod.yml down
```

## Optional reverse proxy

If you later bind a domain, point Nginx/Caddy to:

```txt
127.0.0.1:3000
```

The API proxy remains internal through `/api/backend`.
