from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.database import engine, Base
from app import models
from app.routers import auth, students
import mysql.connector

# Establish a connection to the MySQL database
mydb = mysql.connector.connect(
    host="localhost",      # Database server address
    user="root",           # MySQL username
    password="root"        # MySQL password
)


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aurora Student Management API",
    description="Complete Student Management System with Authentication",
    version="1.0.0"
)

# CORS - allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static uploads
uploads_path = Path("uploads")
uploads_path.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(auth.router)
app.include_router(students.router)


@app.get("/")
def root():
    return {
        "message": "Aurora Student Management API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}