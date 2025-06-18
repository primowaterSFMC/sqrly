#!/usr/bin/env python3
"""
Development server runner for Sqrily ADHD Planner

This script starts the FastAPI development server with hot reloading.
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Run the development server"""
    
    # Set environment variables for development
    os.environ.setdefault("DATABASE_URL", "sqlite:///./sqrily_adhd_planner.db")
    os.environ.setdefault("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
    os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key-here")
    
    print("🚀 Starting Sqrily ADHD Planner Development Server")
    print("📖 API Documentation will be available at: http://localhost:8000/api/docs")
    print("🔄 Auto-reload enabled for development")
    print("💡 Make sure to set your OPENAI_API_KEY environment variable")
    print("-" * 60)
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(project_root / "app")],
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()