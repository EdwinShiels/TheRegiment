# The Regiment - System Architecture

## Overview
The Regiment is a discipline-first coaching system built with Python FastAPI backends and a React frontend. This document outlines the system architecture and file organization.

## Directory Structure

```
the-regiment/
├── api/                           # Backend services
│   ├── core/                      # Shared core functionality
│   │   ├── __init__.py
│   │   ├── config.py             # Environment and app config
│   │   ├── database.py           # Database connection and models
│   │   └── schemas/              # Pydantic schemas
│   │       ├── __init__.py
│   │       ├── client.py         # ClientProfileSchema
│   │       ├── meal.py           # MealLogSchema, MealTemplateSchema
│   │       ├── training.py       # TrainingLogSchema, TrainingTemplateSchema
│   │       ├── cardio.py         # CardioLogSchema
│   │       ├── checkin.py        # CheckinLogSchema
│   │       └── job_card.py       # JobCardSchema
│   │
│   ├── engines/                  # Core business logic engines
│   │   ├── __init__.py
│   │   ├── onboarding/          # Onboarding engine
│   │   ├── meal_delivery/       # Meal delivery engine
│   │   ├── training/            # Training dispatcher
│   │   ├── cardio/              # Cardio regiment engine
│   │   ├── checkin/             # Check-in analyzer
│   │   ├── infraction/          # Infraction monitor
│   │   └── dspy/                # DSPy flag engine
│   │
│   ├── api/                     # FastAPI routes
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── clients.py
│   │   │   ├── meals.py
│   │   │   ├── training.py
│   │   │   ├── cardio.py
│   │   │   └── checkins.py
│   │   └── deps.py              # Shared dependencies
│   │
│   ├── discord/                 # Discord bot integration
│   │   ├── __init__.py
│   │   ├── bot.py
│   │   └── commands/
│   │
│   ├── scheduler/               # APScheduler jobs
│   │   ├── __init__.py
│   │   └── jobs.py
│   │
│   └── tests/                   # Backend tests
│       ├── __init__.py
│       ├── conftest.py
│       └── engines/
│
├── battle-station-ui/           # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API service calls
│   │   ├── utils/             # Helper functions
│   │   └── types/             # TypeScript types
│   ├── public/                # Static assets
│   └── tests/                 # Frontend tests
│
├── docker/                     # Docker configuration
│   ├── api/                   # Backend Dockerfile
│   └── ui/                    # Frontend Dockerfile
│
├── scripts/                    # Utility scripts
│   ├── setup.sh
│   └── deploy.sh
│
├── .env.example               # Example environment variables
├── docker-compose.yml         # Docker compose configuration
├── Makefile                   # Build and development commands
├── pyproject.toml            # Python dependencies
└── README.md                 # Project documentation
```

## Key Components

### Backend Services (api/)
- **Core**: Shared functionality, database models, and schemas
- **Engines**: Business logic modules for each major feature
- **API**: FastAPI routes and endpoints
- **Discord**: Bot integration for client interactions
- **Scheduler**: Background job management

### Frontend (battle-station-ui/)
- React + Tailwind CSS application
- Component-based architecture
- TypeScript for type safety
- API service integration

### Infrastructure
- Docker containers for each service
- Poetry for Python dependency management
- PostgreSQL database
- Discord bot integration
- APScheduler for background jobs

## Development Guidelines

1. All data structures must conform to the schemas defined in `api/core/schemas/`
2. All timestamps must be in UTC
3. All numeric fields must maintain 8 decimal places
4. All engines must validate inputs against schemas
5. All changes must include tests
6. All code must pass linting and type checking 