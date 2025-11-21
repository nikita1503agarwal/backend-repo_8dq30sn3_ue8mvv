from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Course Schemas
class CourseBase(BaseModel):
    title: str = Field(..., min_length=2)
    description: Optional[str] = None
    credits: int = Field(..., gt=0)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2)
    description: Optional[str] = None
    credits: Optional[int] = Field(None, gt=0)


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    credits: int


# Student Schemas
class StudentBase(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    age: int


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    email: Optional[EmailStr] = None
    age: Optional[int] = None


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    age: int
    courses: List[CourseOut] = []


class StudentBulkCreate(BaseModel):
    students: List[StudentCreate]
