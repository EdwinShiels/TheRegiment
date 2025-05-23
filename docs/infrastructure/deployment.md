✅ Deployment Contract

We will test and run the system locally first using Docker Compose.  
Final production deployment target will be chosen after local validation.

Initial Host: ❌ TBD  
Local Stack: ✅ Docker Compose for:
- FastAPI (backend logic + APScheduler + all engine runners)
- Discord bot (as a standalone process)
- NeonDB (external, not containerized)
- Frontend (React UI – Battle Station)

Final deployment will use either Render,Railway or Fly.io — both acceptable per tech stack.

Secrets loaded from `.env` files locally. Production secrets stored securely in host (e.g. Railway Secrets panel).
