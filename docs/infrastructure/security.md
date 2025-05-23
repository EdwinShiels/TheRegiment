✅ Security Contract

Auth:
- No public user auth needed
- Coach access only via local access (Battle Station)
- Discord commands are role-gated (Coach only)

Rate Limiting:
- Backend FastAPI endpoints limited to 100 req/min per IP
- Bot commands not rate-limited (handled by Discord API)

HTTPS:
- Enforced at deployment layer (Railway or Fly.io)
- All production endpoints must be HTTPS

CORS:
- Allow only requests from `https://your-battle-station.com` (if deployed)
