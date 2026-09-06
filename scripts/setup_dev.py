#!/usr/bin/env python3
"""
NEXUS PM — Local Development Setup Script
Run this after cloning the repo and setting up .env

Usage:
    python scripts/setup_dev.py
"""

import subprocess
import sys
import os
import time


def run(cmd: str, cwd: str = None, check: bool = True):
    """Run a shell command and print output."""
    print(f"\n▶ {cmd}")
    result = subprocess.run(
        cmd, shell=True, cwd=cwd, check=check,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    if result.stdout:
        print(result.stdout)
    return result


def check_dependency(cmd: str, name: str):
    """Check if a dependency is installed."""
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode != 0:
        print(f"❌ {name} is not installed or not in PATH. Please install it first.")
        sys.exit(1)
    print(f"✅ {name} found")


def main():
    print("=" * 60)
    print("  NEXUS PM — Development Setup")
    print("=" * 60)

    # Check dependencies
    print("\n📋 Checking dependencies...")
    check_dependency("docker --version", "Docker")
    check_dependency("docker compose version", "Docker Compose")
    check_dependency("python --version", "Python")
    check_dependency("node --version", "Node.js")

    # Check .env exists
    if not os.path.exists(".env"):
        print("\n⚠️  .env file not found. Copying from .env.example...")
        run("copy .env.example .env" if sys.platform == "win32" else "cp .env.example .env")
        print("📝 Please edit .env and add your GEMINI_API_KEY, then re-run this script.")
        sys.exit(0)

    # Start infrastructure services
    print("\n🐳 Starting infrastructure (Postgres, Redis, MinIO)...")
    run("docker compose up -d postgres redis minio")
    print("⏳ Waiting for services to be healthy...")
    time.sleep(8)

    # Install backend dependencies (for local dev without Docker)
    print("\n🐍 Setting up Python virtual environment...")
    run("python -m venv venv", cwd="backend")
    venv_python = "backend\\venv\\Scripts\\python" if sys.platform == "win32" else "backend/venv/bin/python"
    run(f"{venv_python} -m pip install --upgrade pip")
    run(f"{venv_python} -m pip install -r requirements.txt", cwd="backend")

    # Run database migrations
    print("\n🗄️  Running database migrations...")
    env = {**os.environ, "DATABASE_URL": "postgresql://nexuspm:nexuspm_secret@localhost:5432/nexuspm"}
    run(f"{venv_python} -m alembic upgrade head", cwd="backend")

    # Seed demo data
    print("\n🌱 Seeding demo data...")
    run(f"{venv_python} scripts/seed_demo_data.py", cwd="backend")

    # Install AI service dependencies
    print("\n🤖 Setting up AI service...")
    run("python -m venv venv", cwd="ai-service")
    ai_python = "ai-service\\venv\\Scripts\\python" if sys.platform == "win32" else "ai-service/venv/bin/python"
    run(f"{ai_python} -m pip install -r requirements.txt", cwd="ai-service")

    # Install frontend dependencies
    print("\n⚛️  Setting up frontend...")
    run("npm install", cwd="frontend")

    print("\n" + "=" * 60)
    print("✅ Setup complete! Start the services:")
    print()
    print("  Terminal 1 (Backend):")
    print("    cd backend && venv\\Scripts\\activate")
    print("    uvicorn app.main:app --reload --port 8000")
    print()
    print("  Terminal 2 (AI Service):")
    print("    cd ai-service && venv\\Scripts\\activate")
    print("    uvicorn main:app --reload --port 8001")
    print()
    print("  Terminal 3 (Celery Worker):")
    print("    cd backend && venv\\Scripts\\activate")
    print("    celery -A app.tasks.celery_app worker --loglevel=info")
    print()
    print("  Terminal 4 (Frontend):")
    print("    cd frontend && npm run dev")
    print()
    print("  Open: http://localhost:3000")
    print("  API Docs: http://localhost:8000/docs")
    print()
    print("  Demo accounts:")
    print("    supervisor1@demo.com / demo123")
    print("    planner1@demo.com   / demo123")
    print("    pm1@demo.com        / demo123")
    print("=" * 60)


if __name__ == "__main__":
    main()
