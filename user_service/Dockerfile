FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential && apt-get clean

# Set workdir
WORKDIR /app

# Copy project metadata and install dependencies
COPY pyproject.toml ./

# Install pip's PEP 621 support using build tools
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir .

# Copy the rest of the code
COPY . .

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]