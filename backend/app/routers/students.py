from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import uuid
import aiofiles
from pathlib import Path

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/students", tags=["Students"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.get("", response_model=schemas.StudentListResponse)
def list_students(
    q: Optional[str] = Query(None, description="Search by student_id, name, email, course, department"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.Student)

    if q:
        search = f"%{q.strip()}%"
        query = query.filter(
            or_(
                models.Student.student_id.ilike(search),
                models.Student.first_name.ilike(search),
                models.Student.last_name.ilike(search),
                models.Student.email.ilike(search),
                models.Student.course.ilike(search),
                models.Student.department.ilike(search),
                (models.Student.first_name + " " + models.Student.last_name).ilike(search)
            )
        )

    total = query.count()
    students = query.order_by(models.Student.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "students": students}


@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("", response_model=schemas.StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(
    student_in: schemas.StudentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles("admin", "staff"))
):
    # Check unique student_id
    if db.query(models.Student).filter(models.Student.student_id == student_in.student_id).first():
        raise HTTPException(status_code=400, detail="Student ID already exists")

    # Check unique email
    if db.query(models.Student).filter(models.Student.email == student_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered for a student")

    db_student = models.Student(**student_in.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.put("/{student_id}", response_model=schemas.StudentOut)
def update_student(
    student_id: int,
    student_in: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles("admin", "staff"))
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    data = student_in.model_dump(exclude_unset=True)

    if "student_id" in data and data["student_id"] != student.student_id:
        if db.query(models.Student).filter(models.Student.student_id == data["student_id"]).first():
            raise HTTPException(status_code=400, detail="Student ID already exists")

    if "email" in data and data["email"] != student.email:
        if db.query(models.Student).filter(models.Student.email == data["email"]).first():
            raise HTTPException(status_code=400, detail="Email already registered for a student")

    for key, value in data.items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}", response_model=schemas.Message)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles("admin", "staff"))
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Remove profile image file if exists
    if student.profile_image:
        img_path = Path(student.profile_image.lstrip("/"))
        if img_path.exists():
            try:
                img_path.unlink()
            except Exception:
                pass

    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}


@router.post("/{student_id}/upload-image", response_model=schemas.StudentOut)
async def upload_profile_image(
    student_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles("admin", "staff"))
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Validate content type
    allowed = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, GIF, WEBP images are allowed")

    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = UPLOAD_DIR / filename

    async with aiofiles.open(filepath, "wb") as out:
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:  # 5 MB limit
            raise HTTPException(status_code=400, detail="File too large (max 5MB)")
        await out.write(content)

    # Delete old image
    if student.profile_image:
        old = Path(student.profile_image.lstrip("/"))
        if old.exists():
            try:
                old.unlink()
            except Exception:
                pass

    student.profile_image = f"/uploads/{filename}"
    db.commit()
    db.refresh(student)
    return student
