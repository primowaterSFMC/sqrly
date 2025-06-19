#!/usr/bin/env python3
"""
Test database connection
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

print("Environment variables:")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

try:
    from sqrily.app.config import settings
    print(f"Settings database_url: {settings.database_url}")
    
    from sqrily.app.database import engine
    print("Testing database connection...")
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("✅ Database connection successful!")
        print(f"Test query result: {result.fetchone()}")
        
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print(f"Error type: {type(e)}")
