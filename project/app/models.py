from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base

# Association table for many-to-many between Student and Course
student_course = Table(
    "student_course",
    Base.metadata,
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("student_id", "course_id", name="uq_student_course"),
)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)

    courses = relationship(
        "Course",
        secondary=student_course,
        back_populates="students",
        cascade="save-update",
    )


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)

    students = relationship(
        "Student",
        secondary=student_course,
        back_populates="courses",
        cascade="save-update",
    )
