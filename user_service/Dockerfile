FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl build-essential && apt-get clean

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.7.1

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# Copy dependency files first for Docker caching
COPY pyproject.toml poetry.lock ./

# Install dependencies globally (no venv)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy source code
COPY src/ ./src/

COPY migrate.sh ./migrate.sh
RUN chmod +x ./migrate.sh

# Expose port for Flask
EXPOSE 5000

#Run DB Migrations and start the app
CMD ["./migrate.sh"]

