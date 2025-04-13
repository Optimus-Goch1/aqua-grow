# Base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.7.1

# Install system dependencies
RUN apt-get update && apt-get install -y curl build-essential && apt-get clean

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Set work directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

# Copy rest of the code
COPY . .

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]