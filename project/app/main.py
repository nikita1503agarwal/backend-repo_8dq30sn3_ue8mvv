from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .database import Base, engine
from . import schemas, crud, models
from .dependencies import db_session
from .security import get_api_key

app = FastAPI(
    title="Students & Courses CRUD API",
    description=(
        "A production-ready FastAPI service for managing students, courses, and enrollments. "
        "Includes pagination, filters, ordering, API key security, and robust validation."
    ),
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create DB tables on startup
@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


# ---------- Students Endpoints ----------
@app.post("/students/", response_model=schemas.StudentOut, dependencies=[Depends(get_api_key)], status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(db_session)):
    try:
        created = crud.create_student(db, student)
    except IntegrityError:
        # Duplicate email
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    # load courses relation for response
    created = crud.get_student(db, created.id)
    assert created is not None
    return created


@app.post("/students/bulk", response_model=List[schemas.StudentOut], dependencies=[Depends(get_api_key)], status_code=status.HTTP_201_CREATED)
def bulk_create_students(payload: schemas.StudentBulkCreate, db: Session = Depends(db_session)):
    created, errors = crud.bulk_create_students(db, payload.students)
    if errors and not created:
        # If nothing created and there are errors, surface them
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=errors)
    # Return created items with nested courses
    with_courses = [crud.get_student(db, s.id) for s in created]
    return [s for s in with_courses if s]


@app.get("/students/", response_model=List[schemas.StudentOut], dependencies=[Depends(get_api_key)])
def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, gt=0, le=100),
    name: Optional[str] = None,
    order_by: Optional[str] = Query(None, pattern="^(name|age)$"),
    db: Session = Depends(db_session),
):
    return crud.get_students(db, skip=skip, limit=limit, name=name, order_by=order_by)


@app.get("/students/{student_id}", response_model=schemas.StudentOut, dependencies=[Depends(get_api_key)])
def get_student(student_id: int, db: Session = Depends(db_session)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


@app.put("/students/{student_id}", response_model=schemas.StudentOut, dependencies=[Depends(get_api_key)])
def update_student(student_id: int, data: schemas.StudentUpdate, db: Session = Depends(db_session)):
    try:
        updated = crud.update_student(db, student_id, data)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    # Ensure nested courses included
    updated = crud.get_student(db, student_id)
    assert updated is not None
    return updated


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_api_key)])
def delete_student(student_id: int, db: Session = Depends(db_session)):
    ok = crud.delete_student(db, student_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return None


@app.post("/students/{student_id}/enroll/{course_id}", response_model=schemas.StudentOut, dependencies=[Depends(get_api_key)])
def enroll(student_id: int, course_id: int, db: Session = Depends(db_session)):
    student = crud.enroll_student_in_course(db, student_id, course_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student or course not found")
    # reload with nested courses
    student = crud.get_student(db, student_id)
    assert student is not None
    return student


@app.post("/students/{student_id}/unenroll/{course_id}", response_model=schemas.StudentOut, dependencies=[Depends(get_api_key)])
def unenroll(student_id: int, course_id: int, db: Session = Depends(db_session)):
    student = crud.unenroll_student_from_course(db, student_id, course_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student or course not found")
    student = crud.get_student(db, student_id)
    assert student is not None
    return student


# ---------- Courses Endpoints ----------
@app.post("/courses/", response_model=schemas.CourseOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_api_key)])
def create_course(course: schemas.CourseCreate, db: Session = Depends(db_session)):
    created = crud.create_course(db, course)
    return created


@app.get("/courses/", response_model=List[schemas.CourseOut], dependencies=[Depends(get_api_key)])
def list_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, gt=0, le=100),
    title: Optional[str] = None,
    order_by: Optional[str] = Query(None, pattern="^(title)$"),
    db: Session = Depends(db_session),
):
    return crud.get_courses(db, skip=skip, limit=limit, title=title, order_by=order_by)


@app.get("/courses/{course_id}", response_model=schemas.CourseOut, dependencies=[Depends(get_api_key)])
def get_course(course_id: int, db: Session = Depends(db_session)):
    course = crud.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@app.put("/courses/{course_id}", response_model=schemas.CourseOut, dependencies=[Depends(get_api_key)])
def update_course(course_id: int, data: schemas.CourseUpdate, db: Session = Depends(db_session)):
    updated = crud.update_course(db, course_id, data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return updated


@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_api_key)])
def delete_course(course_id: int, db: Session = Depends(db_session)):
    ok = crud.delete_course(db, course_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return None


@app.get("/courses/{course_id}/students", response_model=List[schemas.StudentOut], dependencies=[Depends(get_api_key)])
def students_in_course(
    course_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, gt=0, le=100),
    order_by: Optional[str] = Query(None, pattern="^(name|age)$"),
    db: Session = Depends(db_session),
):
    # Ensure course exists
    if not crud.get_course(db, course_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    students = crud.get_students_in_course(db, course_id, skip=skip, limit=limit, order_by=order_by)
    # Attach nested courses for each student
    with_courses = [crud.get_student(db, s.id) for s in students]
    return [s for s in with_courses if s]
