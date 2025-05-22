Python 3.11+ – Core runtime 

Poetry – Dependency & packaging manager

FastAPI 0.100+ – ASGI framework for your HTTP endpoints 

discord.py 2.x – Discord bot integration for all delivery/modals 

APScheduler 3.x – Timezone-aware job scheduling (hourly ticks, daily drops) 

NeonDB (PostgreSQL v15+) – Primary JSON-capable datastore 

Pydantic v1.10+ & JSON Schema Draft-07 – Input/output validation 

uvicorn & Gunicorn – Production ASGI servers

Docker – Containerization for dev/prod parity

pytest – Unit/integration testing

black, isort, flake8, mypy – Code formatting, linting, static typing

python-dotenv – .env loading

GitHub Actions – CI/CD pipelines

Optional: Redis for caching/lookups, Sentry/OpenTelemetry for error-tracking & tracing

## Frontend (Battle Station UI)

- **Vite + React** — Blazing-fast dev server and build tool  
- **Tailwind CSS** — Utility-first CSS framework for rapid, consistent styling  
- **Chakra UI** — Accessible, themeable React component library (alternative to Tailwind)  

Environment Variables (.env.example.md)
md
Copy
Edit
# ─────────────────────────────────────────────────────────────────────────────
# MonsterCoach Environment Configuration
#
# Copy this to `.env` (no “.example” suffix), fill in your values, and keep
# the file out of version control.
# ─────────────────────────────────────────────────────────────────────────────

# Database
DATABASE_URL        = "postgresql://USER:PASSWORD@HOST:PORT/DATABASE"

# Discord Bot
DISCORD_BOT_TOKEN   = "your-discord-bot-token"
DISCORD_CLIENT_ID   = "your-discord-oauth-client-id"      # if using OAuth flows
DISCORD_CLIENT_SECRET = "your-discord-oauth-client-secret"

# FastAPI
APP_HOST            = "0.0.0.0"
APP_PORT            = "8000"
LOG_LEVEL           = "INFO"                              # DEBUG, INFO, WARNING, ERROR

# Secrets & Security
SECRET_KEY          = "random-string-for-signing-jwts"

# CORS / Hosts
ALLOWED_HOSTS       = "example.com,api.example.com"       # comma-separated

# Scheduler / Caching (optional)
REDIS_URL           = "redis://:password@redis-host:6379/0"

# Sentry (optional)
SENTRY_DSN          = "https://<key>@sentry.io/<project>"

# DSPy Flag Engine (if hosted separately)
DSPY_API_URL        = "https://dspy.example.com/api/flags"

# Defaults
TIMEZONE_DEFAULT    = "UTC"                              # fallback if none set
# ─────────────────────────────────────────────────────────────────────────────
Example pyproject.toml Snippet
toml
Copy
Edit
[tool.poetry]
name = "monstercoach"
version = "0.1.0"
description = "Discipline-first AI coaching system"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python               = "^3.11"
fastapi              = "^0.100"
uvicorn              = "^0.22"
discord.py           = "^2.0"
apscheduler          = "^3.11"
pydantic             = "^1.10"
python-dotenv        = "^1.0"
psycopg2-binary      = "^2.9"       # PostgreSQL driver

# Optional / integrations
redis                = "^4.5"
sentry-sdk           = "^1.12"

[tool.poetry.dev-dependencies]
pytest               = "^7.3"
black                = "^23.3"
isort                = "^5.12"
flake8               = "^6.0"
mypy                 = "^1.5"

[build-system]
requires             = ["poetry-core"]
build-backend        = "poetry.core.masonry.api"
With this you’ll have:

Reproducible environments via Poetry and .env.

High-performance async APIs driven by FastAPI & uvicorn.

Robust scheduling with APScheduler.

Strict schema enforcement with Pydantic/JSON-Schema.

Containerized deployments via Docker.