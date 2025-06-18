# 🐳 Sqrly ADHD Planner - Docker Deployment Guide

This guide provides comprehensive instructions for deploying the Sqrly ADHD Planner application using Docker and Docker Compose.

## 📋 Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **OpenAI API Key**: Required for AI functionality

### Verify Installation
```bash
docker --version
docker-compose --version
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
# Navigate to your project directory
cd /path/to/sqrly

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment
Edit the `.env` file with your settings:

```bash
# REQUIRED: Set your OpenAI API key
OPENAI_API_KEY=your-openai-api-key-here

# REQUIRED: Set secure passwords
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-here
POSTGRES_PASSWORD=your-secure-postgres-password-here

# Optional: Set Redis password for production
REDIS_PASSWORD=your-redis-password-here
```

### 3. Build and Start (Production)
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f sqrly

# Check service status
docker-compose ps
```

### 4. Access the Application
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

## 🛠️ Development Mode

For development with hot reload and debugging:

```bash
# Start in development mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View development logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f sqrly

# Access development tools container
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec dev-tools bash
```

### Development Features
- **Hot Reload**: Code changes automatically restart the server
- **Debug Mode**: Enhanced logging and error details
- **Exposed Ports**: Direct access to PostgreSQL (5432) and Redis (6379)
- **Development Database**: Separate database for development data

## 🏗️ Architecture Overview

The Docker setup includes the following services:

### Core Services
- **sqrly**: Main FastAPI application (Port 8000)
- **postgres**: PostgreSQL database (Port 5432 in dev)
- **redis**: Redis cache and message broker (Port 6379 in dev)

### Background Services
- **celery-worker**: Handles background tasks
- **celery-beat**: Manages scheduled tasks

### Service Dependencies
```
sqrly → postgres (database)
sqrly → redis (cache/sessions)
celery-worker → postgres + redis
celery-beat → postgres + redis
```

## 📊 Container Management

### Basic Commands
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a specific service
docker-compose restart sqrly

# View logs
docker-compose logs -f [service-name]

# Execute commands in container
docker-compose exec sqrly bash
```

### Database Management
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d sqrly_adhd_planner

# Create database backup
docker-compose exec postgres pg_dump -U postgres sqrly_adhd_planner > backup.sql

# Restore database backup
docker-compose exec -T postgres psql -U postgres -d sqrly_adhd_planner < backup.sql
```

### Redis Management
```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Monitor Redis
docker-compose exec redis redis-cli monitor
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | - | ✅ |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | - | ✅ |
| `POSTGRES_PASSWORD` | PostgreSQL password | - | ✅ |
| `DEBUG` | Enable debug mode | `false` | ❌ |
| `LOG_LEVEL` | Logging level | `INFO` | ❌ |
| `REDIS_PASSWORD` | Redis password | - | ❌ |

### ADHD-Specific Settings
```bash
MAX_OVERWHELM_THRESHOLD=10
DEFAULT_FOCUS_DURATION=25
DEFAULT_BREAK_DURATION=5
HYPERFOCUS_WARNING_THRESHOLD=90
```

## 🔒 Security Considerations

### Production Security
1. **Change Default Passwords**: Update all default passwords
2. **Use Strong JWT Secret**: Generate a secure JWT secret key
3. **Enable Redis Password**: Set a strong Redis password
4. **Network Security**: Use Docker networks for service isolation
5. **Non-Root User**: Application runs as non-root user in container

### Generate Secure Keys
```bash
# Generate JWT secret key
openssl rand -hex 32

# Generate Redis password
openssl rand -base64 32
```

## 📈 Monitoring and Health Checks

### Health Check Endpoints
- **Application**: `GET /health`
- **Database**: Automatic PostgreSQL health checks
- **Redis**: Automatic Redis ping checks

### View Health Status
```bash
# Check all service health
docker-compose ps

# View specific service health
docker inspect sqrly --format='{{.State.Health.Status}}'
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Verify database connectivity
docker-compose exec sqrly python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"
```

#### 3. Redis Connection Issues
```bash
# Check Redis logs
docker-compose logs redis

# Test Redis connectivity
docker-compose exec redis redis-cli ping
```

#### 4. OpenAI API Issues
```bash
# Verify API key is set
docker-compose exec sqrly env | grep OPENAI

# Test API connectivity
docker-compose exec sqrly python -c "import openai; print('API key configured')"
```

### Logs and Debugging
```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs sqrly

# Debug container issues
docker-compose exec sqrly bash
```

## 🔄 Updates and Maintenance

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Migrations
```bash
# Run database migrations
docker-compose exec sqrly alembic upgrade head
```

### Cleanup
```bash
# Remove stopped containers
docker-compose down --remove-orphans

# Clean up unused images
docker image prune -f

# Clean up unused volumes (⚠️ This will delete data)
docker volume prune -f
```

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify environment configuration
3. Ensure all required services are healthy
4. Check network connectivity between containers

For additional help, refer to the main project documentation or create an issue in the project repository.
