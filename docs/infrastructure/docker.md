✅ Docker Setup (Local + Dev)

Use Docker to encapsulate the entire app for local development.

Services:
- `backend`: FastAPI app with all engines + APScheduler
- `discord_bot`: Discord.py command engine
- `frontend`: React (Battle Station UI)

Backend Dockerfile should:
- Use Python 3.12 slim
- Use `poetry` for dependency management
- Auto-run `uvicorn main:app` at container start

Frontend should be built with Vite or Next.js (not part of container yet).

NeonDB is not containerized — use live connection string.