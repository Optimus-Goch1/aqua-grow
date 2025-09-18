# Aqua Grow - Smart Irrigation System Backend

A microservices-based backend system that powers the Aqua Grow mobile application for smart irrigation management using IoT sensors and automated controls.

## Overview

This backend system provides the server-side infrastructure for the Aqua Grow mobile application. It connects to IoT devices (ESP32) to collect sensor data, manages user authentication and farm configurations, and provides automated irrigation control based on configurable thresholds.

## Features

- **User Management**: Secure authentication with JWT tokens and user profile management
- **Farm Management**: CRUD operations for farm configurations with ESP32 device linking
- **Real-time Sensor Data**: Collection and processing of temperature and moisture sensor readings
- **Irrigation Control**: Manual and automatic irrigation system management
- **Threshold Management**: Configurable moisture and temperature thresholds for automated irrigation
- **Multi-farm Support**: Handle multiple farms per user with unique ESP32 device identifiers
- **MQTT Integration**: Real-time communication with IoT devices
- **RESTful APIs**: Well-documented APIs for mobile app integration

## Architecture

The backend follows a microservices architecture with four main services:

- **User Service**: Authentication, user management, and farm CRUD operations
- **Monitoring Service**: Sensor data collection, processing, and storage  
- **Irrigation Service**: Irrigation system control and automation logic
- **Notification Service**: Alert management and user notifications


## Tech Stack

- **Framework**: Flask with Flask-RESTX for API documentation
- **Authentication**: Flask-JWT-Extended for secure token management
- **Database**: SQLAlchemy ORM with database migrations via Alembic
- **IoT Communication**: Paho-MQTT for real-time device communication
- **Data Storage**: InfluxDB for time-series sensor data
- **Containerization**: Docker with multi-stage builds
- **Deployment**: AWS ECS with ECR for container registry
- **CI/CD**: GitHub Actions for automated deployment
- **Package Management**: Poetry for dependency management

## Installation

### Prerequisites

- Python 3.10+
- Poetry
- Docker & Docker Compose
- AWS CLI (for deployment)
- MQTT Broker (for IoT communication)
- Database (PostgreSQL recommended for production)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aqua-grow-backend
   ```

2. **Set up each service**
   ```bash
   # User Service
   cd user_service
   poetry install
   poetry shell

   # Repeat for each service
   cd ../irrigation_service && poetry install
   cd ../monitoring_service && poetry install  
   cd ../notification_service && poetry install
   ```

3. **Environment Configuration**
   
   Create `.env` files in each service directory:
   ```env
   # Common configuration
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///app.db
   
   # JWT Configuration
   JWT_SECRET_KEY=your-jwt-secret
   JWT_ACCESS_TOKEN_EXPIRES=3600
   
   # MQTT Configuration (for monitoring service)
   MQTT_BROKER_HOST=localhost
   MQTT_BROKER_PORT=1883
   MQTT_USERNAME=mqtt_user
   MQTT_PASSWORD=mqtt_password
   
   # InfluxDB Configuration (for monitoring service)
   INFLUXDB_URL=http://localhost:8086
   INFLUXDB_TOKEN=your-influxdb-token
   INFLUXDB_ORG=your-org
   INFLUXDB_BUCKET=sensor-data
   ```

4. **Database Setup**
   ```bash
   cd user_service
   poetry run flask db init
   poetry run flask db migrate -m "Initial migration"
   poetry run flask db upgrade
   ```

5. **Run Services**
   ```bash
   # Terminal 1 - User Service (Port 5001)
   cd user_service
   poetry run python src/app.py

   # Terminal 2 - Irrigation Service (Port 5002)
   cd irrigation_service
   poetry run python src/app.py

   # Terminal 3 - Monitoring Service (Port 5003)  
   cd monitoring_service
   poetry run python src/app.py

   # Terminal 4 - Notification Service (Port 5004)
   cd notification_service
   poetry run python app.py
   ```

## API Documentation

Each service provides Swagger/OpenAPI documentation available at:
- User Service: `http://localhost:5001/`
- Irrigation Service: `http://localhost:5002/`
- Monitoring Service: `http://localhost:5003/`
- Notification Service: `http://localhost:5004/`

### Key API Endpoints

#### User Service (`/user/user/`)
#### Monitoring Service (`/sensor/sensor/`)
#### Irrigation Service (`/irrigation/irrigation/`)


## IoT Device Integration

The system integrates with ESP32 devices through MQTT protocol:

### MQTT Topics
- `sensors/{esp32_id}/data` - Sensor data from devices
- `irrigation/{esp32_id}/command` - Irrigation commands to devices
- `system/{esp32_id}/status` - Device status updates

### Sensor Data Format
```json
{
  "esp32_id": "ESP32_001",
  "temperature": 25.5,
  "moisture": 45.2,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Deployment

### Docker Deployment

1. **Build services**
   ```bash
   docker build -t user-service ./user_service
   docker build -t irrigation-service ./irrigation_service
   docker build -t monitoring-service ./monitoring_service
   docker build -t notification-service ./notification_service
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### AWS ECS Deployment

The project includes GitHub Actions workflow for automated deployment to AWS ECS:

1. **Required AWS Services**
   - ECS Cluster
   - ECR Repositories for each service
   - R