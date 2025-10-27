# 🚀 CI/CD Guide - OPIc Practice Portal

This guide covers Continuous Integration and Continuous Deployment (CI/CD) setup for the OPIc Practice Portal Flask application.

## 📋 Table of Contents

1. [Overview](#overview)
2. [GitHub Actions Setup](#github-actions-setup)
3. [Docker Configuration](#docker-configuration)
4. [Deployment Strategies](#deployment-strategies)
5. [Environment Management](#environment-management)
6. [Monitoring & Logging](#monitoring--logging)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)

## 🎯 Overview

Our CI/CD pipeline includes:
- **Automated Testing** - Unit, integration, and API tests
- **Code Quality Checks** - Linting, formatting, and security scans
- **Docker Builds** - Multi-stage builds for optimization
- **Deployment** - Automated deployment to staging and production
- **Monitoring** - Health checks and performance monitoring

## 🔧 GitHub Actions Setup

### 1. Continuous Integration (CI)

Create `.github/workflows/ci.yml`:

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.14, 3.15]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8 black
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Format check with black
      run: black --check .
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.14'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install safety bandit
    
    - name: Security check with safety
      run: safety check
    
    - name: Security check with bandit
      run: bandit -r app/ -f json -o bandit-report.json
    
    - name: Upload security report
      uses: actions/upload-artifact@v3
      with:
        name: security-report
        path: bandit-report.json

  docker-build:
    runs-on: ubuntu-latest
    needs: [test, security]
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: |
          opic-portal:latest
          opic-portal:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

### 2. Continuous Deployment (CD)

Create `.github/workflows/deploy.yml`:

```yaml
name: CD Pipeline

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Staging
      run: |
        echo "Deploying to staging environment..."
        # Add your staging deployment commands here
        # Example: kubectl apply -f k8s/staging/
    
    - name: Run Health Checks
      run: |
        echo "Running health checks..."
        # Add health check commands here
        # Example: curl -f https://staging.opic-portal.com/health

  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment: production
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Production
      run: |
        echo "Deploying to production environment..."
        # Add your production deployment commands here
        # Example: kubectl apply -f k8s/production/
    
    - name: Run Production Health Checks
      run: |
        echo "Running production health checks..."
        # Add production health check commands here
        # Example: curl -f https://opic-portal.com/health
    
    - name: Notify Deployment Success
      uses: 8398a7/action-slack@v3
      with:
        status: success
        text: 'Production deployment successful! 🚀'
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 🐳 Docker Configuration

### 1. Dockerfile

Create `Dockerfile`:

```dockerfile
# Multi-stage build for production
FROM python:3.14-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p uploads/responses uploads/questions && \
    chown -R appuser:appuser uploads

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

### 2. Docker Compose

Create `docker-compose.yml` for development:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=postgresql://postgres:password@db:5432/opic_portal
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - .:/app
      - ./uploads:/app/uploads
    depends_on:
      - db
      - redis
    command: python app.py

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=opic_portal
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/opic_portal
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - .:/app
      - ./uploads:/app/uploads
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

### 3. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  web:
    image: opic-portal:latest
    ports:
      - "80:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./uploads:/app/uploads
    depends_on:
      - db
      - redis
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

## 🚀 Deployment Strategies

### 1. Kubernetes Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opic-portal
  labels:
    app: opic-portal
spec:
  replicas: 3
  selector:
    matchLabels:
      app: opic-portal
  template:
    metadata:
      labels:
        app: opic-portal
    spec:
      containers:
      - name: opic-portal
        image: opic-portal:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: opic-portal-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: opic-portal-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: opic-portal-service
spec:
  selector:
    app: opic-portal
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

### 2. AWS ECS Deployment

Create `aws/ecs-task-definition.json`:

```json
{
  "family": "opic-portal",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "opic-portal",
      "image": "account.dkr.ecr.region.amazonaws.com/opic-portal:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:opic-portal/database-url"
        },
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:opic-portal/secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/opic-portal",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

## 🔐 Environment Management

### 1. Environment Variables

Create environment-specific configuration files:

**Development (.env.dev)**:
```env
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///opic_portal.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key
```

**Staging (.env.staging)**:
```env
FLASK_ENV=staging
FLASK_DEBUG=False
DATABASE_URL=postgresql://user:pass@staging-db:5432/opic_portal
REDIS_URL=redis://staging-redis:6379/0
SECRET_KEY=${STAGING_SECRET_KEY}
```

**Production (.env.prod)**:
```env
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=${PROD_DATABASE_URL}
REDIS_URL=${PROD_REDIS_URL}
SECRET_KEY=${PROD_SECRET_KEY}
```

### 2. Secrets Management

Use AWS Secrets Manager or HashiCorp Vault:

```python
# secrets_manager.py
import boto3
import json

def get_secret(secret_name, region_name="us-west-2"):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None
```

## 📊 Monitoring & Logging

### 1. Application Monitoring

Add monitoring endpoints to your Flask app:

```python
# monitoring.py
from flask import jsonify
import psutil
import time

@app.route('/health')
def health_check():
    """Health check endpoint for load balancers"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '1.0.0'
    })

@app.route('/metrics')
def metrics():
    """Application metrics endpoint"""
    return jsonify({
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'active_users': User.query.count(),
        'total_responses': Response.query.count()
    })
```

### 2. Logging Configuration

```python
# logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/opic_portal.log', maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('OPIc Portal startup')
```

### 3. Error Tracking

Integrate with Sentry for error tracking:

```python
# error_tracking.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

def init_sentry(app):
    sentry_sdk.init(
        dsn=app.config.get('SENTRY_DSN'),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        environment=app.config.get('FLASK_ENV', 'development')
    )
```

## 🔒 Security Considerations

### 1. Container Security

- Use non-root users in containers
- Scan images for vulnerabilities
- Keep base images updated
- Use multi-stage builds to reduce attack surface

### 2. Network Security

- Use HTTPS in production
- Implement proper CORS policies
- Use network policies in Kubernetes
- Enable firewall rules

### 3. Secrets Security

- Never commit secrets to version control
- Use environment variables or secret managers
- Rotate secrets regularly
- Use least privilege access

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database connectivity
   python -c "from app import db; print(db.engine.url)"
   ```

2. **Redis Connection Issues**
   ```bash
   # Test Redis connection
   redis-cli ping
   ```

3. **Docker Build Failures**
   ```bash
   # Build with verbose output
   docker build --no-cache --progress=plain .
   ```

4. **Deployment Rollback**
   ```bash
   # Rollback to previous version
   kubectl rollout undo deployment/opic-portal
   ```

### Debug Commands

```bash
# Check application logs
docker logs opic-portal-container

# Check Kubernetes pods
kubectl get pods
kubectl logs -f deployment/opic-portal

# Check database migrations
flask db current
flask db history

# Test API endpoints
curl -X GET http://localhost:5000/health
curl -X GET http://localhost:5000/metrics
```

## 📚 Additional Resources

- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.0.x/deploying/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)

---

**Happy Deploying! 🚀**

