# Claim Processing API

A production-ready API for processing healthcare claims with robust monitoring, logging, and alerting capabilities.

## Features

- **User Authentication**: JWT-based authentication with access and refresh tokens
- **Claim Management**: Full CRUD operations for healthcare claims
- **Database**: Async PostgreSQL integration using SQLAlchemy and asyncpg
- **Validation**: Request/response validation using Pydantic
- **Monitoring**: Comprehensive monitoring with Prometheus, Grafana, and Loki
- **Logging**: Structured JSON logging with Loki, Grafana, and Promtail
- **Containerization**: Multi-stage Docker build and docker-compose setup
- **CI/CD**: GitHub Actions pipeline for testing, building, and deployment

## Tech Stack

- **Backend**: Python 3.11, FastAPI
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy with asyncpg
- **Authentication**: JWT (JSON Web Tokens)
- **Monitoring**: Prometheus, Grafana, Loki
- **Logging**: Structured JSON logging with Loki, Grafana, and Promtail
- **Containerization**: Docker, docker-compose
- **CI/CD**: GitHub Actions

## Documentation

- [API Documentation](./README.md#api-documentation) - Details about the API endpoints
- [Deployment Strategies](./DEPLOYMENT_STRATEGIES.md) - Analysis of various deployment methods and log storage strategies
- [Monitoring Guide](./README.md#monitoring-and-alerting-setup) - Information on the monitoring and alerting setup

## Setup Instructions

### Prerequisites

- Docker and docker-compose
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd claim-processing-api
   ```

2. Environment Configuration:
   Copy the example environment file (if applicable):
   ```bash
   cp .env.example .env
   ```
   Modify the .env file with your specific configurations if needed.

3. Start the application and monitoring stack:
   ```bash
   docker-compose up -d
   ```

4. Verify the installation:
   - API is running: `curl http://localhost:8000/health`
   - Prometheus is running: `curl http://localhost:9090/-/healthy`
   - Loki is running: `curl http://localhost:3100/ready`
   - Grafana is running: `curl http://localhost:3000/api/health`

### Access Points

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (default credentials: admin/admin)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

## API Documentation

### Authentication

- `POST /api/v1/users`: Register a new user
  - Request Body: `{ "email": "user@example.com", "password": "securepassword", "full_name": "John Doe" }`
  - Response: `{ "id": 1, "email": "user@example.com", "full_name": "John Doe" }`

- `POST /api/v1/login`: Authenticate and receive JWT tokens
  - Request Body: `{ "username": "user@example.com", "password": "securepassword" }`
  - Response: `{ "access_token": "eyJ...", "token_type": "bearer", "refresh_token": "eyJ..." }`

- `POST /api/v1/refresh`: Refresh access token
  - Request Body: `{ "refresh_token": "eyJ..." }`
  - Response: `{ "access_token": "eyJ...", "token_type": "bearer" }`

### Claims Management

- `POST /api/v1/claims`: Submit a new claim
  - Request Body: 
    ```json
    {
      "patient_id": "123456789",
      "provider_id": "PRV12345",
      "service_date": "2023-04-15",
      "procedures": [
        {
          "code": "99213",
          "amount": 125.50
        }
      ],
      "total_amount": 125.50,
      "notes": "Optional notes about the claim"
    }
    ```
  - Response:
    ```json
    {
      "id": 1,
      "patient_id": "123456789",
      "provider_id": "PRV12345",
      "service_date": "2023-04-15",
      "procedures": [{"code": "99213", "amount": 125.50}],
      "total_amount": 125.50,
      "status": "submitted",
      "notes": "Optional notes about the claim",
      "created_at": "2023-04-16T10:30:00Z",
      "updated_at": "2023-04-16T10:30:00Z"
    }
    ```

- `GET /api/v1/claims/{id}`: Fetch a claim's details
  - Response: Same as above POST response

- `GET /api/v1/claims/status/{id}`: Fetch a claim's status
  - Response: `{ "id": 1, "status": "approved", "updated_at": "2023-04-17T14:25:00Z" }`

- `PUT /api/v1/claims/{id}`: Update a claim
  - Request Body: Same format as POST, but fields are optional
  - Response: Updated claim object

- `DELETE /api/v1/claims/{id}`: Delete a claim
  - Response: `{ "message": "Claim deleted successfully" }`

## CI/CD Pipeline Overview

Our GitHub Actions CI/CD pipeline automates the testing, building, and deployment processes:

### Pipeline Stages

1. **Linting**:
   - Uses flake8, black, and isort to ensure code quality
   - Checks code style, imports, and potential errors
   - Fails the build if code standards are not met

2. **Testing**:
   - Spins up PostgreSQL and Loki services for integration tests
   - Runs pytest with coverage reporting
   - Uploads coverage reports to Codecov

3. **Building**:
   - Triggered only on main branch pushes
   - Builds the Docker image using Docker Buildx
   - Pushes the image to DockerHub with appropriate tags

4. **Deployment**:
   - Deploys to staging environment after successful build
   - Uses environment-specific configurations and secrets
   - Can be extended to deploy to production after approval

### Setting Up CI/CD

1. Required repository secrets:
   - `DOCKERHUB_USERNAME`: Your DockerHub username
   - `DOCKERHUB_TOKEN`: Your DockerHub access token
   - Additional deployment secrets as needed

2. Branch protection rules:
   - Enable required status checks on the main branch
   - Require approval for pull requests

## Monitoring and Alerting Setup

Our monitoring stack consists of Prometheus, Loki, Grafana, and Alertmanager, providing comprehensive visibility into API performance and logs.

### Monitoring Components

1. **Prometheus**:
   - Collects metrics from API and infrastructure
   - Stores time-series data
   - Evaluates alert rules
   - Access at http://localhost:9090

2. **Loki**:
   - Aggregates logs from all services
   - Provides log querying capabilities
   - Integrates with Grafana for visualization
   - Access via Grafana or directly at http://localhost:3100

3. **Grafana**:
   - Visualizes metrics and logs
   - Provides dashboards for API performance, errors, and logs
   - Default credentials: admin/admin
   - Access at http://localhost:3000

4. **Alertmanager**:
   - Manages alert notifications
   - Handles grouping, routing, and silencing of alerts
   - Access at http://localhost:9093

### Available Dashboards

1. **API Overview**: General API performance metrics
   - Request rates, latencies, and error rates
   - Resource utilization
   - Endpoint performance

2. **API Logs Analysis**: Log-based insights
   - Error rates by status code
   - Log volumes over time
   - Error distribution
   - Request path analysis

### Alerting Configuration

Alerts are configured in `config/alert_rules.yml` and include:

1. **High Error Rate**: Triggers when the error rate exceeds 5%
2. **High 5xx Errors**: Triggers on server error spikes
3. **High 4xx Errors**: Triggers on client error spikes
4. **API Down**: Triggers when the API service is unavailable
5. **Database Connection Failures**: Monitors database connectivity
6. **High CPU/Memory Usage**: Monitors resource constraints

### Testing the Monitoring System

We provide scripts to test the monitoring and alerting system:

1. Generate test logs to verify log collection:
   ```bash
   python3 scripts/generate_error_logs.py -n 100 -t both
   ```

2. Generate logs that trigger alerts:
   ```bash
   python3 scripts/flood_loki_with_errors.py -n 500 -b 20 -i 0.1 -t 5xx
   ```

3. View the generated logs in Grafana:
   - Go to Explore
   - Select Loki as the data source
   - Query: `{job="api"}`

4. Check triggered alerts in Alertmanager:
   - Access http://localhost:9093
   - View active alerts

## Architecture

The system consists of several components:

1. **FastAPI Application**: The core API handling claim submissions and processing
2. **PostgreSQL Database**: Stores claim data and processing results
3. **Loki**: Stores structured logs
4. **Grafana**: Visualizes metrics and logs
5. **Promtail**: Ships logs from the application to Loki
6. **Prometheus**: Collects and stores metrics
7. **AlertManager**: Manages alerting and notifications

## Deployment Strategies

### Kubernetes Deployment

For production environments, Kubernetes is recommended:

1. **Stateless API**: Deploy the API as a stateless service with multiple replicas
2. **Database**: Use a managed PostgreSQL service or StatefulSet
3. **Monitoring**: Deploy the monitoring stack in a dedicated namespace
4. **Ingress**: Use an ingress controller for routing and TLS termination
5. **Autoscaling**: Configure Horizontal Pod Autoscaler based on CPU/memory metrics

### AWS ECS Deployment

Alternatively, AWS ECS provides a managed container service:

1. **Task Definition**: Define the API and monitoring services
2. **Service**: Create services with desired task count
3. **Load Balancer**: Use Application Load Balancer for routing
4. **Auto Scaling**: Configure service auto scaling based on CloudWatch metrics
5. **RDS**: Use Amazon RDS for PostgreSQL database

## Getting Started

1. Clone the repository
2. Install Docker and docker-compose
3. Run `docker-compose up -d`
4. Access the API at `http://localhost:8000`
5. Access Grafana at `http://localhost:3000`
6. Access Prometheus at `http://localhost:9090`
