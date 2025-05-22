# The Regiment

A discipline-first coaching system built with Python FastAPI backends and a React frontend.

## System Architecture

The system consists of multiple microservices:

- **Onboarding Engine** (Port 8001): Client onboarding and profile management
- **Meal Delivery Engine** (Port 8002): Meal plan generation and tracking
- **Training Dispatcher** (Port 8003): Training program management
- **Cardio Regiment Engine** (Port 8004): Cardio program management
- **Check-in Analyzer** (Port 8005): Client check-in processing
- **Infraction Monitor** (Port 8006): Compliance monitoring
- **DSPy Flag Engine** (Port 8007): AI-powered flag generation
- **Automation Scheduler** (Port 8008): Background job management
- **Battle Station UI** (Port 80): React frontend

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Poetry (Python package manager)
- PostgreSQL 15+

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/the-regiment.git
   cd the-regiment
   ```

2. Install dependencies:
   ```bash
   make install
   ```

3. Copy environment file:
   ```bash
   cp .env.example.md .env
   ```
   Edit `.env` with your configuration.

4. Start development environment:
   ```bash
   make dev
   ```

## Development

### Running Tests
```bash
make test
```

### Linting
```bash
make lint
```

### Building
```bash
# Build all components
make build

# Build specific components
make build-ui
make build-api
make build-images
```

### Docker Images
```bash
# Build all images
make build-images

# Push images to registry
make push-images
```

## Environment Variables

Key environment variables (see `.env.example.md` for full list):

- `DATABASE_URL`: PostgreSQL connection string
- `DISCORD_BOT_TOKEN`: Discord bot token
- `DISCORD_CLIENT_ID`: Discord OAuth client ID
- `DISCORD_CLIENT_SECRET`: Discord OAuth client secret
- `APP_HOST`: API host (default: 0.0.0.0)
- `APP_PORT`: API port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 