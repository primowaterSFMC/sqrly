#!/bin/bash

# Sqrly Database Seeding Script Runner
# This script sets up the environment and runs the database seeding

set -e  # Exit on any error

echo "🌱 Sqrly Database Seeding Script"
echo "================================"

# Check if we're in the right directory
if [ ! -f "sqrily/app/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected to find: sqrily/app/main.py"
    exit 1
fi

# Check if Python virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "   It's recommended to run this in a virtual environment"
    echo "   Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Exiting. Please activate your virtual environment and try again."
        exit 1
    fi
fi

# Check if required dependencies are installed
echo "🔍 Checking dependencies..."
python -c "import sqlalchemy, fastapi" 2>/dev/null || {
    echo "❌ Error: Required dependencies not found"
    echo "   Please install dependencies with: pip install -r requirements.txt"
    exit 1
}

# Check if database configuration is set
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: No .env file found"
    echo "   Using default database configuration"
    echo "   For production, please create a .env file with proper database settings"
fi

# Make the seed script executable
chmod +x scripts/seed_database.py

# Run the seeding script
echo "🚀 Running database seeding script..."
echo ""

python scripts/seed_database.py

echo ""
echo "✅ Database seeding completed!"
echo ""
echo "🎯 Next steps:"
echo "   1. Start the backend server: python -m sqrily.app.main"
echo "   2. Start the frontend: cd ui && npm start"
echo "   3. Login with: jwhiteprimo@gmail.com / SecuredPassword123"
echo ""
echo "Happy coding! 🚀"
