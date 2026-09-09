# Aurora Student Suite — Student Management System

Full-stack student management application with authentication, dashboard, and complete student CRUD.

## Project structure

```
student-management-complete/
├── frontend/          # Static HTML/CSS/JS (landing + admin)
├── backend/           # FastAPI REST API
├── database/          # MySQL schema reference
└── notes/
```

## Features

### Authentication
- Register (full name, email, password, confirm password, role)
- Login / Logout
- JWT bearer tokens
- Password hashing (bcrypt)
- Duplicate email prevention
- Roles: admin, staff, user

### Student management
- Full CRUD (create, list, view, update, delete)
- Search by student ID, name, email, course, department
- Profile image upload
- Confirmation modal for delete
- Professional details page

### Dashboard
- Stats and recent students after login

## Run backend

```bash
cd backend
pip install -r requirements.txt
# Uses SQLite by default (student_management.db is created automatically)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the helper script:

```bash
cd backend
bash run.sh
```

**Important:** There is no default admin account.  
Create your first account via the Register page and choose the **Administrator** role.

API docs: http://127.0.0.1:8000/docs

For MySQL, edit `backend/.env` and set:

```
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/fastapi_student_system
```

Then run `database/schema.sql` if you want (tables are also auto-created by FastAPI).

## Run frontend

Open `frontend/index.html` or serve the folder:

```bash
cd frontend
python -m http.server 5500
```

Then visit http://127.0.0.1:5500 → Register → Login.

If the API runs elsewhere, edit `API_BASE` in `frontend/assets/js/api.js`.

## API summary

- `POST /api/auth/register`
- `POST /api/auth/login` (form) / `/api/auth/login/json`
- `POST /api/auth/logout`
- `GET  /api/auth/me`
- `GET|POST /api/students`
- `GET|PUT|DELETE /api/students/{id}`
- `POST /api/students/{id}/upload-image`
