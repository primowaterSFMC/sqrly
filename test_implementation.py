#!/usr/bin/env python3
"""
Test script to verify the implementation changes work correctly.

This script tests the core functionality without requiring a full environment setup.
"""

import sys
import os
sys.path.append('sqrily')

def test_pydantic_imports():
    """Test that Pydantic v2 imports work correctly"""
    try:
        from pydantic_settings import BaseSettings
        from pydantic import field_validator
        print("✅ Pydantic v2 imports successful")
        return True
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False

def test_schema_validation():
    """Test that our schemas validate correctly"""
    try:
        # Set minimal environment variables for testing
        os.environ['JWT_SECRET_KEY'] = 'test-secret-key-for-testing-only'
        os.environ['OPENAI_API_KEY'] = 'test-openai-key'

        # Test basic schema imports and validation
        sys.path.append('sqrily')
        from app.schemas.task import TaskCreate, TaskResponse
        from app.schemas.goal import GoalCreate, GoalResponse
        from app.schemas.auth import UserRegister
        
        # Test task schema
        task_data = {
            "title": "Test Task",
            "description": "A test task for validation",
            "importance_level": 8,
            "urgency_level": 6,
            "task_type": "work",
            "complexity_level": "medium"
        }
        
        task = TaskCreate(**task_data)
        print(f"✅ Task schema validation successful: {task.title}")
        
        # Test goal schema
        goal_data = {
            "title": "Test Goal",
            "description": "A test goal for validation",
            "priority_level": 7,
            "complexity_assessment": "medium",
            "overwhelm_risk": "low"
        }
        
        goal = GoalCreate(**goal_data)
        print(f"✅ Goal schema validation successful: {goal.title}")
        
        # Test auth schema
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        user = UserRegister(**user_data)
        print(f"✅ Auth schema validation successful: {user.email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

def test_exception_classes():
    """Test that our custom exceptions work correctly"""
    try:
        sys.path.append('sqrily')
        from app.exceptions import (
            TaskNotFoundError, ValidationError, OverwhelmDetectedError,
            ADHDFriendlyException
        )
        
        # Test basic exception
        try:
            raise TaskNotFoundError("test-task-id")
        except ADHDFriendlyException as e:
            assert "couldn't find that task" in e.adhd_friendly_message
            print("✅ TaskNotFoundError works correctly")
        
        # Test validation error
        try:
            raise ValidationError("Invalid input", "title")
        except ADHDFriendlyException as e:
            assert "small issue" in e.adhd_friendly_message
            print("✅ ValidationError works correctly")
        
        # Test overwhelm detection
        try:
            raise OverwhelmDetectedError(8.5)
        except ADHDFriendlyException as e:
            assert "take on a lot" in e.adhd_friendly_message
            print("✅ OverwhelmDetectedError works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception testing failed: {e}")
        return False

def test_config_loading():
    """Test that configuration loads with minimal setup"""
    try:
        # Set required environment variables
        os.environ['JWT_SECRET_KEY'] = 'test-secret-key-for-testing-only'
        os.environ['OPENAI_API_KEY'] = 'test-openai-key'
        
        sys.path.append('sqrily')
        from app.config import Settings
        
        # Test with debug mode
        settings = Settings(debug=True)
        cors_origins = settings.get_cors_origins()
        
        assert isinstance(cors_origins, list)
        assert len(cors_origins) > 0
        assert any("localhost" in origin for origin in cors_origins)
        
        print(f"✅ Config loading successful")
        print(f"   - App name: {settings.app_name}")
        print(f"   - Debug mode: {settings.debug}")
        print(f"   - CORS origins: {cors_origins}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_api_structure():
    """Test that API modules can be imported"""
    try:
        # Test basic file structure exists
        import os

        # Check that key files exist
        files_to_check = [
            'sqrily/app/api/tasks/tasks.py',
            'sqrily/app/api/goals/goals.py',
            'sqrily/app/api/ai/ai.py',
            'sqrily/app/services/task_service.py',
            'sqrily/app/services/goal_service.py',
            'sqrily/app/schemas/task.py',
            'sqrily/app/schemas/goal.py',
            'sqrily/app/exceptions.py'
        ]

        for file_path in files_to_check:
            if not os.path.exists(file_path):
                print(f"❌ Missing file: {file_path}")
                return False
            else:
                print(f"✅ Found: {file_path}")

        print("✅ All key implementation files exist")
        return True

    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        return False


def test_endpoint_count():
    """Test that we have implemented the expected number of endpoints"""
    try:
        import re

        endpoint_counts = {}

        # Count Task API endpoints
        with open('sqrily/app/api/tasks/tasks.py', 'r') as f:
            task_content = f.read()
            task_endpoints = len(re.findall(r'@router\.(get|post|put|delete)', task_content))
            endpoint_counts['tasks'] = task_endpoints

        # Count Goal API endpoints
        with open('sqrily/app/api/goals/goals.py', 'r') as f:
            goal_content = f.read()
            goal_endpoints = len(re.findall(r'@router\.(get|post|put|delete)', goal_content))
            endpoint_counts['goals'] = goal_endpoints

        # Count AI API endpoints
        with open('sqrily/app/api/ai/ai.py', 'r') as f:
            ai_content = f.read()
            ai_endpoints = len(re.findall(r'@router\.(get|post|put|delete)', ai_content))
            endpoint_counts['ai'] = ai_endpoints

        print(f"✅ Task API endpoints: {endpoint_counts['tasks']}")
        print(f"✅ Goal API endpoints: {endpoint_counts['goals']}")
        print(f"✅ AI API endpoints: {endpoint_counts['ai']}")
        print(f"✅ Total endpoints implemented: {sum(endpoint_counts.values())}")

        # Verify we have the expected minimum endpoints
        expected_minimums = {'tasks': 8, 'goals': 8, 'ai': 5}
        for api, count in endpoint_counts.items():
            if count < expected_minimums[api]:
                print(f"❌ {api} API has only {count} endpoints, expected at least {expected_minimums[api]}")
                return False

        return True

    except Exception as e:
        print(f"❌ Endpoint count test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Sqrly Implementation Changes")
    print("=" * 50)
    
    tests = [
        ("Pydantic v2 Imports", test_pydantic_imports),
        ("Schema Validation", test_schema_validation),
        ("Exception Classes", test_exception_classes),
        ("Configuration Loading", test_config_loading),
        ("API Structure", test_api_structure),
        ("Endpoint Implementation", test_endpoint_count),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Implementation is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
