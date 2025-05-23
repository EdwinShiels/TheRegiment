# TheRegiment - MonsterCoach 2025

AI-powered coaching platform built with military-grade discipline and precision.

## Phase 0 - Infrastructure Setup ✅

- Project structure initialized
- Dependencies locked and installed
- Development environment configured
- Docker containers ready

## Quick Start

```bash
# Install dependencies
poetry install

# Start development environment
docker-compose up -d

# Run the application
poetry run uvicorn src.api.main:app --reload
```

## Architecture

- **Backend**: FastAPI with SQLAlchemy
- **AI Engine**: DSPy framework
- **Database**: PostgreSQL
- **Bot**: Discord.py
- **Deployment**: Docker containers

## Development

See `docs/` for detailed documentation and build specifications. 