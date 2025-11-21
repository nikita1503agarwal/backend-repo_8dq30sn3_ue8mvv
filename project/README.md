# FastAPI Students & Courses CRUD (SQLite + SQLAlchemy)

A clean, production-ready FastAPI application that manages Students, Courses, and Enrollments (many-to-many). It includes pagination, search, ordering, robust validation, API key security, CORS, and comprehensive error handling.

## Features

- Full CRUD for Students and Courses
- Many-to-many Enrollment between Students and Courses
- Pagination (skip, limit)
- Search filters (students by name, courses by title)
- Ordering (students by name or age, courses by title)
- Input validation with Pydantic (email, min lengths, positive credits)
- API Key security via `X-API-KEY` header
- Duplicate email protection (409 Conflict)
- Return nested relations (students include courses; courses include students where applicable)
- Bulk student creation
- List all students in a specific course
- Automatic DB table creation on startup
- CORS enabled for all origins
- Swagger docs with custom title, description, and version

## Tech Stack

- FastAPI
- SQLAlchemy ORM
- SQLite (file-based DB)
- Pydantic

## Project Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── dependencies.py
│   ├── security.py
└── requirements.txt
└── README.md
```

## Installation

1. Create and activate a virtual environment (recommended)

```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

2. Install dependencies

```
pip install -r requirements.txt
```

Note: This repo also contains a root-level requirements.txt used by some environments. Use the `project/requirements.txt` if running standalone from the `project` folder.

## Running the App

From the repository root, run:

```
uvicorn app.main:app --reload
```

If running from inside the `project` folder, run:

```
uvicorn app.main:app --reload --app-dir .
```

The API will be available at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Default API key for local testing: `secret123`.
Include it in requests with the header: `X-API-KEY: secret123`.

## Environment Variables (Optional)

- `API_KEY` — override the default `secret123` API key.
- `DATABASE_URL` — override SQLite path. Defaults to `sqlite:///./students_courses.db`.

## API Overview

### Students
- POST `/students/`
- POST `/students/bulk`
- GET `/students/` — supports `?skip=0&limit=10&name=Mi&order_by=name|age`
- GET `/students/{id}`
- PUT `/students/{id}`
- DELETE `/students/{id}`
- POST `/students/{id}/enroll/{course_id}`
- POST `/students/{id}/unenroll/{course_id}`

### Courses
- POST `/courses/`
- GET `/courses/` — supports `?skip=0&limit=10&title=Intro&order_by=title`
- GET `/courses/{id}`
- PUT `/courses/{id}`
- DELETE `/courses/{id}`
- GET `/courses/{id}/students` — all students in a course

## Example Requests (curl)

Create a student:
```
curl -X POST http://127.0.0.1:8000/students/ \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: secret123" \
  -d '{"name":"Mira Stone","email":"mira@example.com","age":22}'
```

List students with pagination, search, and ordering:
```
curl -H "X-API-KEY: secret123" \
  "http://127.0.0.1:8000/students/?skip=0&limit=10&name=Mi&order_by=name"
```

Create a course:
```
curl -X POST http://127.0.0.1:8000/courses/ \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: secret123" \
  -d '{"title":"Intro to Databases","description":"Basics of SQL","credits":3}'
```

Enroll a student in a course:
```
curl -X POST http://127.0.0.1:8000/students/1/enroll/1 \
  -H "X-API-KEY: secret123"
```

List students in a course:
```
curl -H "X-API-KEY: secret123" http://127.0.0.1:8000/courses/1/students
```

Sample JSON response (student with courses):
```
{
  "id": 1,
  "name": "Mira Stone",
  "email": "mira@example.com",
  "age": 22,
  "courses": [
    {"id": 1, "title": "Intro to Databases", "description": "Basics of SQL", "credits": 3}
  ]
}
```

## Future Improvements

- Authentication with users/roles
- Rate limiting
- Soft deletes and audit logs
- CSV import/export
- Async SQLAlchemy model

## License

MIT License
