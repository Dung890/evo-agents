#!/usr/bin/env python3
"""
Start script for the UTD Career Guidance AI System
"""

import os
import sys

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import boto3
        import selenium
        import pandas
        print("✅ All dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    aws_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not aws_key or not aws_secret:
        print("⚠️  AWS credentials not found in environment variables")
        print("   The system will work with limited functionality")
        print("   For full functionality, set:")
        print("   export AWS_ACCESS_KEY_ID=your_access_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("   export AWS_DEFAULT_REGION=us-east-2")
        return False
    
    print("✅ AWS credentials found")
    return True

def main():
    """Start the server"""
    print("🚀 UTD Career Guidance AI System")
    print("=" * 50)
    print("📍 Server: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("src"):
        print("❌ Error: Please run this script from the aws-agetic-ai directory")
        print("   cd aws-agetic-ai")
        print("   python start_server.py")
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    check_aws_credentials()
    
    print("🔄 Starting server with auto-reload...")
    print()
    
    # Start uvicorn
    os.system("uvicorn src.api.app:app --reload --host 127.0.0.1 --port 8000")

if __name__ == "__main__":
    main()

