# Database Seeding Scripts

This directory contains scripts to populate your Sqrly ADHD Planner database with comprehensive sample data for development and testing.

## 🎯 What Gets Created

### User Account
- **Email**: `jwhiteprimo@gmail.com`
- **Password**: `SecuredPassword123`
- **Name**: J White
- **ADHD Profile**: Fully configured with realistic preferences
  - Energy tracking enabled
  - Overwhelm notifications on
  - Break reminders configured
  - Medication schedule tracking
  - Sensory preferences set
  - Executive function support enabled

### Sample Data Structure

#### Goals (2 goals)
- **Improve Work-Life Balance** (Schedule quadrant)
- **Complete Professional Certification** (Focus quadrant)

#### Tasks (18 tasks total)
**Focus Quadrant (Important + Urgent)** - 4 tasks
- Complete project proposal presentation (with AI breakdown)
- Review and respond to client feedback
- Fix critical bug in production system (with AI breakdown)
- Prepare for performance review

**Schedule Quadrant (Important + Not Urgent)** - 5 tasks
- Plan quarterly team goals (with AI breakdown)
- Research new productivity tools
- Schedule annual health checkups
- Plan vacation time
- Learn new programming framework (in progress)

**Delegate Quadrant (Not Important + Urgent)** - 4 tasks
- Organize desk workspace (completed)
- Update team calendar with meetings
- Order office supplies
- Submit monthly expense report (completed)

**Eliminate Quadrant (Not Important + Not Urgent)** - 2 tasks
- Clean out old email folders
- Reorganize digital photos

**Additional Tasks** - 3 tasks
- Call insurance company (completed)
- Update LinkedIn profile (overdue)

#### Subtasks (15+ subtasks)
- Detailed breakdown for complex tasks
- Realistic executive function difficulty ratings
- AI-generated with confidence scores
- Proper sequencing and dependencies
- ADHD-specific support features

### ADHD-Specific Features
- **Energy Levels**: Realistic distribution from 1-5
- **Executive Function Ratings**: Initiation, execution, completion difficulties
- **Context Tags**: Environment and tool requirements
- **AI Suggestions**: Breakdown recommendations and timing advice
- **Due Dates**: Mix of overdue, today, and future dates
- **Progress Tracking**: Various completion states
- **Overwhelm Prevention**: Manageable task sizes and clear instructions

## 🚀 How to Run

### Option 1: Shell Script (macOS/Linux)
```bash
./scripts/run_seed.sh
```

### Option 2: Python Script (Cross-platform)
```bash
python scripts/run_seed.py
```

### Option 3: Direct Execution
```bash
python scripts/seed_database.py
```

## 📋 Prerequisites

1. **Project Setup**: Run from the project root directory
2. **Dependencies**: Install with `pip install -r requirements.txt`
3. **Database**: PostgreSQL or SQLite configured
4. **Environment**: Virtual environment recommended

## 🔧 Configuration

### Environment Variables
The script uses your existing `.env` configuration. If no `.env` file exists, it uses defaults:
- SQLite database in development
- Default JWT settings
- Local development configuration

### Database Connection
The script automatically:
- Creates database tables if they don't exist
- Uses your configured database connection
- Handles transactions safely with rollback on errors

## 📊 Sample Data Details

### Task Distribution
- **Focus**: 4 tasks (22%)
- **Schedule**: 5 tasks (28%)
- **Delegate**: 4 tasks (22%)
- **Eliminate**: 2 tasks (11%)
- **Other**: 3 tasks (17%)

### Completion Status
- **Completed**: 3 tasks (17%)
- **In Progress**: 2 tasks (11%)
- **Pending**: 13 tasks (72%)

### Due Date Distribution
- **Overdue**: 1 task
- **Due Today**: 2 tasks
- **Future**: 8 tasks
- **No Due Date**: 7 tasks

### Energy Level Distribution
- **Low Energy (1-2)**: 4 tasks
- **Medium Energy (3-4)**: 8 tasks
- **High Energy (5)**: 6 tasks

## 🧪 Testing Features

This sample data allows you to test:

### Core Functionality
- ✅ User authentication and profile
- ✅ Task CRUD operations
- ✅ Goal-task relationships
- ✅ Subtask management
- ✅ Progress tracking

### ADHD-Specific Features
- ✅ Energy level matching
- ✅ Quadrant visualization
- ✅ Executive function support
- ✅ AI task breakdown
- ✅ Overwhelm prevention
- ✅ Context-aware task suggestions

### UI Components
- ✅ Task cards with all metadata
- ✅ Progress indicators
- ✅ Energy tracker
- ✅ Quadrant view
- ✅ Filter and search functionality
- ✅ Due date indicators
- ✅ Completion animations

## 🔄 Re-running the Script

The script is designed to be idempotent:
- Checks for existing user before creating
- Won't duplicate data if run multiple times
- Safe to run during development

To completely reset the database:
1. Delete the database file (SQLite) or drop tables (PostgreSQL)
2. Run the seeding script again

## 🐛 Troubleshooting

### Common Issues

**"Required dependencies not found"**
```bash
pip install -r requirements.txt
```

**"Please run from project root"**
```bash
cd /path/to/sqrly
./scripts/run_seed.sh
```

**"Database connection error"**
- Check your `.env` file configuration
- Ensure PostgreSQL is running (if using PostgreSQL)
- Verify database permissions

**"Import errors"**
- Ensure you're in the correct virtual environment
- Check that the project structure is intact
- Verify Python path configuration

## 📝 Customization

To modify the sample data:

1. **Edit `scripts/seed_database.py`**
2. **Modify the data structures** in the creation functions
3. **Add new tasks, goals, or user preferences**
4. **Run the script** to apply changes

The script is well-documented and modular, making it easy to customize for your specific testing needs.

## 🎯 Next Steps

After running the seeding script:

1. **Start the backend**: `python -m sqrily.app.main`
2. **Start the frontend**: `cd ui && npm start`
3. **Login**: Use `jwhiteprimo@gmail.com` / `SecuredPassword123`
4. **Test features**: Explore all the ADHD-specific functionality
5. **Develop UI**: Use the rich sample data to build and test components

The sample data provides a realistic foundation for developing and testing all aspects of the Sqrly ADHD Planner application!
