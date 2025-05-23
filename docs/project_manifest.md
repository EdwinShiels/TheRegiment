# 🧱 Project Manifest: The Regiment (2025)

This document defines the master contract for building and maintaining the MonsterCoach system known as **The Regiment**.

---

## 🧠 Project Identity

- **Project Code Name**: `theregiment`
- **Official GitHub Repo**: https://github.com/EdwinShiels/TheRegiment
- **Main Directory**: `src/`
- **Tech Stack File**: `docs/tech-stack.md` (single source of tech truth)
- **Schema Source**: `docs/schema_definitions.md`
- **Master LST Doctrine**: `docs/lst_master.md`
- **Top-Down HST Strategy**: `docs/hst_new.md`

---

## 🔐 Enforcement Rules

Cursor and all build tools must:
- **Use project name `theregiment`** consistently in all files, folders, Docker, toml, and CI configs
- **Reference only tech and tools declared in `tech-stack.md`**
- **Honor all LSTs as contracts** — no deviations or merges
- **Ignore typos or inconsistencies** found in LSTs unless corrected in this manifest
- **Use only schemas defined in `schema_definitions.md`**
- **Respect structure in `docs/repo_setup.md`** if present

---

## 🧱 Build Control

All builds must proceed in **phases**. These include:

- Phase 0: Repo structure + pyproject.toml
- Phase 1: Engine skeletons
- Phase 2: Engine runners and schemas
- Phase 3: Discord integration
- Phase 4: API + Backend Router
- Phase 5: Docker + Compose
- Phase 6: Local run test
- Phase 7+: UI integration, CI, deploy

Each phase must:
- Be self-contained
- Reference all global contracts above
- Pause for confirmation before moving forward

---

## 🔧 pyproject.toml Requirements

The project **must use Poetry**. `pyproject.toml` should include:

```toml
[tool.poetry]
name = "theregiment"
version = "0.1.0"
description = "AI-enhanced coaching system built on schema-bound engines, Discord UX, and DSPy."
authors = ["Edwin Shiels"]

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.111.0"
pydantic = "^2.6.4"
uvicorn = "^0.29.0"
APScheduler = "^4.0.0"
discord.py = "^2.3.2"
asyncpg = "^0.29.0"
dspy-ai = "^0.4.1"
python-dotenv = "^1.0.1"

[tool.poetry.dev-dependencies]
pytest = "^8.0.0"
httpx = "^0.27.0"
pytest-asyncio = "^0.23.0"
