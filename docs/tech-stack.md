# ✅ MonsterCoach 2025 Tech Stack

This stack is designed for:
- Local-first development
- Zero-cost MVP deployment
- Schema-bound, modular logic
- Discord integration + scheduling
- AI-augmented coaching via DSPy
- Zero drift between backend, bot, and UI

---

## 🧠 Runtime Environment
- **Python**: `3.12`  
  Stable, modern async support. Compatible with FastAPI, APScheduler, DSPy, and Discord bots.

- **Environment Management**: `poetry`  
  Handles all dependencies, lockfiles, and packaging via `pyproject.toml`.

- **Containerization**: Docker (Python 3.12 slim)  
  Used for local orchestration with `docker-compose`.

---

## ⚙️ Core Backend
- **Framework**: FastAPI `^0.111.0`  
  Async, modular, built for schema validation and API scalability.

- **Scheduler**: APScheduler `^4.0.0`  
  Timezone-aware, precision-based engine tick controller for scheduled jobs.

- **Schema Engine**: Pydantic v2 `^2.6.4`  
  Lightning-fast schema validation. Bound to `schema_definitions.md`.

- **Compliance AI Engine**: DSPy `^0.4.1`  
  Used in `dspy_flag_engine` for weekly logic scans and recon flags.

---

## 📡 Discord Integration
- **Library**: discord.py `^2.3.2`  
  Full support for modals, buttons, slash commands, and DM routing.

- **Middleware**: Custom retry logic  
  Auto-retries failed Discord messages (3x), logs as `status: missed`.

---

## 🧱 Database & Persistence
- **Database**: NeonDB (PostgreSQL 15+)  
  Serverless, JSON-friendly. Used for logging job cards, meals, client profiles.

- **Driver**: asyncpg `^0.29.0`  
  Fully async, lightweight, ideal for Pydantic-native data access.

- **ORM**: ❌ None  
  Direct DB access using `asyncpg` and Pydantic models.

---

## 🧪 Dev & Testing
- **Testing**: `pytest`, `pytest-asyncio`, `httpx`  
  Used for engine runner tests, API routes, Discord mocks.

- **Logging**: `logfire.dev` (or `structlog`)  
  Structured, JSON logs with status annotations.

- **Validation**: `jsonschema`  
  Optional — used to ensure DSPy outputs match schema contracts.

---

## 📦 Package Management
- **Tool**: Poetry  
  Controls dependencies, environments, and scripts via `pyproject.toml`.

---

## 🖥️ Frontend (Battle Station UI)
- **Framework**: React 18+
- **Build Tool**: Vite or Next.js
- **State Layer**: SWR or tRPC
- **API Layer**: Connects to FastAPI backend
- **Deployment Target**: Vercel (free tier, GitHub deploy)

---

## 🛡️ Security & Auth (Minimal, Coach-Only)
- Discord-based OAuth2 (Battle Station login)
- IP-level API rate limiting (100 req/min)
- HTTPS enforced by host (Fly.io, Vercel)
- No JWT or user auth — Coach-only use

---

## 🚀 Deployment Strategy
- **Local Development**: Docker + Docker Compose
- **Free MVP Hosts**:
  - Backend: Fly.io or Render (choose based on scaling needs)
  - Frontend: Vercel
  - Database: NeonDB
- **Secrets**: `.env` for local, Secrets panel for host
- **CI/CD**: GitHub Actions (optional post-MVP)

---

## ✅ Doctrine Rules
- All schemas must match `schema_definitions.md`
- All triggers follow `LST_Master.md` and per-engine LSTs
- No logic merged across engines
- All missed events must be logged with `status: missed`
- All timestamps in ISO 8601 with explicit UTC offset

---

This stack is zero-cost friendly, scalable, and aligned with best practices as of early 2025 — ideal for AI-enhanced modular fitness coaching systems.
