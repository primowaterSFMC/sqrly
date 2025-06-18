# Sqrily ADHD Planner - FastAPI Backend

An ADHD-friendly AI planner backend built with FastAPI, featuring Sqrily methodology integration and comprehensive executive function support.

## 🌟 Features

- **ADHD-Specific Support**: Executive function assistance, overwhelm management, task breakdown
- **AI-Powered Planning**: OpenAI GPT-4 integration for intelligent task management
- **Sqrily Method**: Quadrant-based goal and task organization
- **Comprehensive Auth**: JWT + OAuth (Google, Apple) authentication
- **Real-time Features**: WebSocket support for timers and notifications
- **Executive Function Support**: Micro-tasks, stuck helper, momentum building
- **External Integrations**: Google Calendar, Spotify, and more

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (or SQLite for development)
- OpenAI API key
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sqrily
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Configure OpenAI API Key**
   ```bash
   export OPENAI_API_KEY=your-openai-api-key-here
   # Or add it to your .env file
   ```

6. **Run development server**
   ```bash
   python run_dev.py
   ```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/api/docs`.

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - Register with ADHD profile
- `POST /auth/login` - Email/password login
- `GET /auth/google/login` - Google OAuth initiation
- `GET /auth/google/callback` - Google OAuth callback
- `POST /auth/apple/callback` - Apple Sign In callback
- `POST /auth/refresh` - Refresh JWT tokens

### User Management
- `GET /users/me` - Get current user
- `PATCH /users/me/adhd-profile` - Update ADHD preferences
- `POST /users/onboarding` - Complete onboarding

### Goals & Tasks (Sqrily)
- `POST /goals` - Create goal with AI breakdown
- `POST /tasks` - Create task with AI analysis
- `POST /tasks/bulk-process` - Bulk task processing for overwhelm
- `POST /tasks/{id}/breakdown` - AI task breakdown
- `POST /tasks/{id}/micro-tasks` - Generate micro-tasks

### AI Features
- `POST /ai/collaborate` - Interactive AI collaboration
- `POST /ai/natural-input` - Natural language processing
- `POST /ai/overwhelm-check` - Overwhelm detection

### Calendar & Time Management
- `POST /calendar/time-block` - AI-assisted time blocking
- `GET /calendar/focus-time` - Find optimal focus time

### Analytics
- `GET /analytics/productivity` - ADHD-aware analytics
- `GET /analytics/habits` - Habit pattern analysis
- `GET /analytics/weekly-review` - Sqrily weekly review

### Integrations
- `POST /integrations/google-calendar` - Connect Google Calendar
- `POST /integrations/spotify` - Connect Spotify
- `GET /integrations` - List all integrations

### WebSocket Connections
- `WS /ws/timer/{user_id}` - Real-time timer with hyperfocus detection
- `WS /ws/collaboration/{user_id}` - Live AI collaboration
- `WS /ws/notifications/{user_id}` - ADHD-friendly notifications

## 🏗️ Project Structure

```
franklin_adhd_planner/
├── app/
│   ├── api/                    # API endpoints
│   │   ├── auth/              # Authentication
│   │   ├── users/             # User management
│   │   ├── goals/             # Goals & Sqrily
│   │   ├── tasks/             # Task management
│   │   ├── subtasks/          # Executive function support
│   │   ├── ai/                # AI collaboration
│   │   ├── calendar/          # Time management
│   │   ├── analytics/         # ADHD analytics
│   │   ├── integrations/      # External integrations
│   │   └── websockets/        # Real-time features
│   ├── models/                # Database models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   ├── utils/                 # Helper functions
│   ├── config.py              # Configuration
│   ├── database.py            # Database setup
│   ├── dependencies.py        # FastAPI dependencies
│   └── main.py                # FastAPI application
├── tests/                     # Test suite
├── prompts/                   # OpenAI prompt templates
├── requirements.txt           # Python dependencies
├── run_dev.py                 # Development server
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example`):

- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `REDIS_URL` - Redis connection for caching

### ADHD-Specific Settings

- `DEFAULT_FOCUS_DURATION` - Default focus timer (25 minutes)
- `DEFAULT_BREAK_DURATION` - Default break length (5 minutes)  
- `HYPERFOCUS_WARNING_THRESHOLD` - When to warn about hyperfocus (90 minutes)
- `MAX_OVERWHELM_THRESHOLD` - Maximum overwhelm threshold (10)

## 🧠 ADHD Features

### Executive Function Support
- **Task Breakdown**: AI automatically breaks complex tasks into manageable subtasks
- **Micro-Tasks**: 2-5 minute actions for severe executive dysfunction
- **Stuck Helper**: AI assistant for when users can't start tasks
- **Momentum Building**: Tasks designed to build confidence and momentum

### Overwhelm Management
- **Cognitive Load Assessment**: AI analyzes task complexity and user capacity
- **Bulk Task Processing**: AI prioritizes and organizes overwhelming task lists
- **Gentle Notifications**: ADHD-friendly reminders and alerts
- **Break Management**: Automatic break suggestions and energy tracking

### Sqrily Integration
- **Quadrant Assignment**: Automatic classification into Important/Urgent matrix
- **Values Alignment**: Goals connected to personal values and mission
- **Weekly Reviews**: Automated weekly reflection and planning
- **Role Balance**: Tracking time across different life roles

## 🤖 AI Integration

### OpenAI Features
- **GPT-4 Collaboration**: Interactive planning sessions with AI
- **Natural Language Processing**: Convert speech/text to structured tasks
- **ADHD-Optimized Prompts**: Specialized prompts for ADHD needs
- **Cost Optimization**: Token counting and usage monitoring

### AI Capabilities
- Task breakdown and micro-task generation
- Overwhelm detection and intervention
- Goal planning with Sqrily principles
- Habit pattern analysis and predictions
- Personalized productivity insights

## 🔌 Integrations

### Google Calendar
- Bidirectional sync with ADHD optimizations
- Automatic buffer time addition
- Focus time protection
- Gentle reminder scheduling

### Spotify
- Focus music recommendations
- Session-length playlists
- Automatic music for focus sessions
- ADHD-optimized playlist curation

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

## 📱 Deployment

### Docker Deployment

```bash
# Build container
docker build -t sqrily-adhd-planner .

# Run with environment variables
docker run -p 8000:8000 --env-file .env sqrily-adhd-planner
```

### Production Considerations

1. **Security**: Change all default secrets, use HTTPS
2. **Database**: Use PostgreSQL with proper connection pooling
3. **Caching**: Configure Redis for session storage and caching
4. **Monitoring**: Set up logging and error tracking
5. **Scaling**: Use load balancer and multiple instances
6. **AI Costs**: Monitor OpenAI API usage and set budgets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [API Docs](http://localhost:8000/api/docs)
- **Issues**: Submit issues via GitHub
- **Discussions**: Join our community discussions

## 🎯 ADHD-Specific Design Principles

1. **Reduce Cognitive Load**: Simple, clear interfaces and responses
2. **Support Executive Function**: Break down complex tasks automatically
3. **Gentle Guidance**: Encouraging, non-judgmental AI responses
4. **Momentum Building**: Small wins that build confidence
5. **Overwhelm Prevention**: Proactive load management and support
6. **Flexible Structure**: Adapt to user's changing needs and energy levels

---

Built with ❤️ for the ADHD community