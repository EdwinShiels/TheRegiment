# Use Python 3.11 slim as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy engine code
COPY api/engines/checkin/ ./api/engines/checkin/
COPY api/core/ ./api/core/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ENGINE_TYPE=checkin

# Expose port
EXPOSE 8005

# Run the engine with Uvicorn
CMD ["uvicorn", "api.engines.checkin.main:app", "--host", "0.0.0.0", "--port", "8005"] 