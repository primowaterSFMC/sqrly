#!/usr/bin/env python3
"""
Cross-platform database seeding script runner
Works on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if the environment is properly set up"""
    print("🔍 Checking environment...")
    
    # Check if we're in the right directory
    if not Path("sqrily/app/main.py").exists():
        print("❌ Error: Please run this script from the project root directory")
        print(f"   Current directory: {os.getcwd()}")
        print("   Expected to find: sqrily/app/main.py")
        return False
    
    # Check if required dependencies are installed
    try:
        import sqlalchemy
        import fastapi
        print("✅ Required dependencies found")
    except ImportError as e:
        print("❌ Error: Required dependencies not found")
        print(f"   Missing: {e.name}")
        print("   Please install dependencies with: pip install -r requirements.txt")
        return False
    
    # Check for .env file
    if not Path(".env").exists():
        print("⚠️  Warning: No .env file found")
        print("   Using default database configuration")
        print("   For production, please create a .env file with proper database settings")
    
    return True

def run_seeding():
    """Run the database seeding script"""
    print("🚀 Running database seeding script...")
    print("")
    
    try:
        # Import and run the seeding script
        sys.path.insert(0, str(Path.cwd()))
        from scripts.seed_database import main
        main()
        return True
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        return False

def main():
    """Main function"""
    print("🌱 Sqrly Database Seeding Script")
    print("================================")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check virtual environment (optional warning)
    if not os.environ.get('VIRTUAL_ENV'):
        print("⚠️  Warning: No virtual environment detected")
        print("   It's recommended to run this in a virtual environment")
        response = input("   Continue anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Exiting. Please activate your virtual environment and try again.")
            sys.exit(1)
    
    # Run seeding
    if run_seeding():
        print("")
        print("✅ Database seeding completed!")
        print("")
        print("🎯 Next steps:")
        print("   1. Start the backend server: python -m sqrily.app.main")
        print("   2. Start the frontend: cd ui && npm start")
        print("   3. Login with: jwhiteprimo@gmail.com / SecuredPassword123")
        print("")
        print("Happy coding! 🚀")
    else:
        print("❌ Database seeding failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
