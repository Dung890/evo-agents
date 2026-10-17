#!/usr/bin/env python3
"""
Setup script for UTD Career Guidance AI System
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is 3.11+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"✅ Node.js {result.stdout.strip()} detected")
        return True
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 18+")
        return False

def setup_backend():
    """Setup Python backend"""
    print("\n🐍 Setting up Python backend...")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Check for AWS credentials
    aws_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not aws_key or not aws_secret:
        print("⚠️  AWS credentials not found in environment variables")
        print("   Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        print("   You can also set AWS_DEFAULT_REGION (default: us-east-2)")
    
    return True

def setup_frontend():
    """Setup React frontend"""
    print("\n⚛️  Setting up React frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Install Node.js dependencies
    if not run_command("npm install", "Installing Node.js dependencies"):
        return False
    
    # Go back to root directory
    os.chdir("..")
    
    return True

def main():
    """Main setup function"""
    print("🚀 UTD Career Guidance AI System Setup")
    print("=" * 50)
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_node_version():
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Set your AWS credentials:")
    print("   export AWS_ACCESS_KEY_ID=your_access_key")
    print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
    print("   export AWS_DEFAULT_REGION=us-east-2")
    print("\n2. Start the backend server:")
    print("   python start_server.py")
    print("\n3. Start the frontend (in another terminal):")
    print("   cd frontend && npm run dev")
    print("\n4. Visit http://localhost:3000 to use the system!")

if __name__ == "__main__":
    main()
