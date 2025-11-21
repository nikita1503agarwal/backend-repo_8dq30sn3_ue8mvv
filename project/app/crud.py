from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from . import models, schemas


# ---------- Students CRUD ----------

def create_student(db: Session, data: schemas.StudentCreate) -> models.Student:
    student = models.Student(name=data.name, email=data.email, age=data.age)
    db.add(student)
    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        # Likely unique email conflict
        raise
    return student


def bulk_create_students(db: Session, students: List[schemas.StudentCreate]) -> Tuple[List[models.Student], List[str]]:
    # Detect duplicates within payload by email
    emails = [s.email for s in students]
    dup_within = {e for e in emails if emails.count(e) > 1}

    # Detect duplicates against DB
    existing = set(
        db.scalars(select(models.Student.email).where(models.Student.email.in_(emails))).all()
    )

    errors: List[str] = []
    to_create: List[models.Student] = []

    if dup_within:
        errors.append(f"Duplicate emails in payload: {', '.join(sorted(dup_within))}")

    conflict_emails = existing
    if conflict_emails:
        errors.append(f"Emails already exist: {', '.join(sorted(conflict_emails))}")

    # Create only non-conflicting
    creatable = [s for s in students if s.email not in conflict_emails and s.email not in dup_within]
    for s in creatable:
        to_create.append(models.Student(name=s.name, email=s.email, age=s.age))

    if to_create:
        db.add_all(to_create)
        db.commit()
        for s in to_create:
            db.refresh(s)

    return to_create, errors


def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    order_by: Optional[str] = None,
) -> List[models.Student]:
    stmt = select(models.Student).options(joinedload(models.Student.courses))
    if name:
        stmt = stmt.where(func.lower(models.Student.name).like(f"%{name.lower()}%"))
    if order_by in {"name", "age"}:
        column = getattr(models.Student, order_by)
        stmt = stmt.order_by(column.asc())
    stmt = stmt.offset(skip).limit(limit)
    return db.scalars(stmt).unique().all()


def get_student(db: Session, student_id: int) -> Optional[models.Student]:
    stmt = select(models.Student).options(joinedload(models.Student.courses)).where(models.Student.id == student_id)
    return db.scalars(stmt).unique().first()


def update_student(db: Session, student_id: int, data: schemas.StudentUpdate) -> Optional[models.Student]:
    student = db.get(models.Student, student_id)
    if not student:
        return None
    if data.name is not None:
        student.name = data.name
    if data.email is not None:
        student.email = data.email
    if data.age is not None:
        student.age = data.age
    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        raise
    return student


def delete_student(db: Session, student_id: int) -> bool:
    student = db.get(models.Student, student_id)
    if not student:
        return False
    db.delete(student)
    db.commit()
    return True


# ---------- Courses CRUD ----------

def create_course(db: Session, data: schemas.CourseCreate) -> models.Course:
    course = models.Course(title=data.title, description=data.description, credits=data.credits)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def get_courses(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    title: Optional[str] = None,
    order_by: Optional[str] = None,
) -> List[models.Course]:
    stmt = select(models.Course)
    if title:
        stmt = stmt.where(func.lower(models.Course.title).like(f"%{title.lower()}%"))
    if order_by == "title":
        stmt = stmt.order_by(models.Course.title.asc())
    stmt = stmt.offset(skip).limit(limit)
    return db.scalars(stmt).all()


def get_course(db: Session, course_id: int) -> Optional[models.Course]:
    return db.get(models.Course, course_id)


def update_course(db: Session, course_id: int, data: schemas.CourseUpdate) -> Optional[models.Course]:
    course = db.get(models.Course, course_id)
    if not course:
        return None
    if data.title is not None:
        course.title = data.title
    if data.description is not None:
        course.description = data.description
    if data.credits is not None:
        course.credits = data.credits
    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course_id: int) -> bool:
    course = db.get(models.Course, course_id)
    if not course:
        return False
    db.delete(course)
    db.commit()
    return True


# ---------- Enrollment ----------

def enroll_student_in_course(db: Session, student_id: int, course_id: int) -> Optional[models.Student]:
    student = db.get(models.Student, student_id)
    course = db.get(models.Course, course_id)
    if not student or not course:
        return None
    if course in student.courses:
        # Duplicate enrollment prevented
        return student
    student.courses.append(course)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(student)
    return student


def unenroll_student_from_course(db: Session, student_id: int, course_id: int) -> Optional[models.Student]:
    student = db.get(models.Student, student_id)
    course = db.get(models.Course, course_id)
    if not student or not course:
        return None
    if course in student.courses:
        student.courses.remove(course)
        db.commit()
        db.refresh(student)
    return student


def get_students_in_course(db: Session, course_id: int, skip: int = 0, limit: int = 10, order_by: Optional[str] = None) -> List[models.Student]:
    stmt = (
        select(models.Student)
        .join(models.student_course, models.student_course.c.student_id == models.Student.id)
        .where(models.student_course.c.course_id == course_id)
    )
    if order_by in {"name", "age"}:
        stmt = stmt.order_by(getattr(models.Student, order_by).asc())
    stmt = stmt.offset(skip).limit(limit)
    return db.scalars(stmt).all()
