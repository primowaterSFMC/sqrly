# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sqrly is an ADHD-friendly AI planner backend built with FastAPI. It implements the Sqrily methodology with four-quadrant (FC) task prioritization, executive function support, and AI-powered task analysis using OpenAI GPT-4.

## Commands

### Development Server
```bash
# Run development server (from project root)
python sqrily/run_dev.py

# Alternative: Using uvicorn directly (from sqrily directory)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Using Docker
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Dependencies
```bash
# Install dependencies
pip install -r sqrily/requirements.txt
```

## Architecture

### Directory Structure
- `sqrily/app/` - Main application code
  - `api/` - FastAPI routers organized by feature
  - `models/` - SQLAlchemy ORM models
  - `schemas/` - Pydantic v2 schemas for validation
  - `services/` - Business logic layer
  - `tasks/` - Celery background tasks
  - `utils/` - Shared utilities

### Key Architectural Patterns

1. **Layered Architecture**: Clean separation between API routes, business logic (services), and data access (models)

2. **ADHD-Centric Design**: All models include ADHD-specific fields like `executive_difficulty`, `initiation_difficulty`, and `completion_difficulty`. Error messages are supportive and non-judgmental.

3. **Authentication**: JWT-based with access/refresh tokens, OAuth2 support for Google/Apple sign-in. Auth dependencies are in `app/dependencies.py`.

4. **AI Integration**: OpenAI GPT-4 integration in `app/services/ai_service.py` for task analysis and breakdown. Prompts are stored in `sqrily/prompts/`.

5. **Background Tasks**: Celery configuration in `app/celery_app.py` for async processing, notifications, and scheduled tasks.

6. **Configuration**: Environment-based using Pydantic Settings in `app/config.py`. ADHD-specific settings include focus duration and overwhelm thresholds.

### Important Implementation Notes

- The project is at 85% completion (per QUICK_START_GUIDE.md)
- Pydantic v2 migration is complete
- Several API endpoints are stubs awaiting implementation
- Test directory exists but tests are not yet implemented
- CORS wildcard in production needs fixing before deployment

### ADHD-Specific Features

- **Task Breakdown**: AI-powered decomposition of complex tasks into manageable subtasks
- **Executive Function Support**: Difficulty ratings for initiation, execution, and completion
- **Overwhelm Management**: Detection and prevention of user overwhelm
- **Energy Matching**: Task scheduling based on user energy levels
- **Sqrily Quadrants**: FC (four-quadrant) system for prioritization

### External Integrations

- Google Calendar API for calendar sync
- Spotify API for focus music integration
- OAuth providers (Google, Apple) for authentication

### Development Tips

- Always maintain ADHD-friendly error messages
- Use the existing exception classes in `app/exceptions.py`
- Follow the established pattern of router → service → model
- Check `IMPLEMENTATION_PLAN.md` for remaining work items
- API documentation available at `http://localhost:8000/api/docs` when running