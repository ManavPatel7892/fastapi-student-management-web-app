#!/bin/bash
cd "$(dirname "$0")"
export DATABASE_URL="${DATABASE_URL:-sqlite:///./student_management.db}"
echo "Starting Aurora API on http://0.0.0.0:8000"
echo "DATABASE_URL=$DATABASE_URL"
echo "No default admin — register a new account and choose role 'Administrator'."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
