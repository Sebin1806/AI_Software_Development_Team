# AI Software Development Team

## Overview

**AI Software Development Team** is a full-featured multi-agent AI system that simulates an autonomous software engineering organization. Given a high-level user prompt, the system coordinates a sequential workflow across 12 specialized AI agents to plan, design, write code, review, secure, test, and package complete software applications.

---

## 12-Agent Workflow

```
User Prompt
      │
      ▼
1. Project Manager       (Project Workflow & Milestone Planning)
      │
      ▼
2. Business Analyst      (Requirement Analysis & User Stories)
      │
      ▼
3. Software Architect    (System Architecture & Directory Design)
      │
      ▼
4. Database Engineer     (PostgreSQL DDL Schemas & ER Diagrams)
      │
      ▼
5. UI/UX Designer        (Interface Design & Layout Guidelines)
      │
      ▼
6. Frontend Developer    (React / TypeScript Components & Pages)
      │
      ▼
7. Backend Developer     (FastAPI Services & Business Logic)
      │
      ▼
8. API Developer         (REST Endpoints & OpenAPI Specifications)
      │
      ▼
9. Code Reviewer         (Code Quality & Refactoring Audit)
      │
      ▼
10. Security Engineer    (OWASP Security Audit & Vulnerability Assessment)
      │
      ▼
11. Test Engineer        (Automated Test Suites & QA Plan)
      │
      ▼
12. DevOps Engineer      (Dockerfile, Docker Compose & CI/CD Pipelines)
      │
      ▼
Generated Project & Artifacts
```

---

## Tech Stack & Architecture

- **Backend**: FastAPI, Python 3.11, Pydantic v2
- **Database**: PostgreSQL (SQLAlchemy ORM + Alembic Migrations)
- **Authentication**: JWT Token Authentication & bcrypt Password Hashing
- **LLM Service**: Ollama (Llama 3.1) with retry handling and configurable timeout
- **Testing**: pytest & FastAPI TestClient

---

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user account
- `POST /api/auth/login` - Authenticate user & obtain JWT token
- `GET /api/auth/profile` - Get authenticated user profile

### Projects
- `POST /api/projects` - Create a new project
- `GET /api/projects` - List user projects
- `GET /api/projects/{project_id}` - Get project details
- `DELETE /api/projects/{project_id}` - Delete project

### Multi-Agent Orchestrator
- `GET /api/orchestrator/order` - Get execution order of the 12 agents
- `POST /api/orchestrator/start` - Dispatch background software development task
- `GET /api/orchestrator/status/{task_id}` - Check task progress and agent execution logs
- `GET /api/orchestrator/results/{task_id}` - Fetch generated code files, DDLs, and artifacts
- `POST /api/orchestrator/cancel/{task_id}` - Request workflow cancellation

---

## Setup & Local Development

### 1. Environment Configuration
Copy `.env.example` to `.env` in the `backend` folder and update environment variables:
```bash
cp backend/.env.example backend/.env
```

### 2. Database Migrations
Run Alembic migrations to create all tables (`users`, `projects`, `agents`, `task_executions`, `agent_execution_logs`, `agent_artifacts`):
```bash
cd backend
venv\Scripts\alembic.exe upgrade head
```

### 3. Running Ollama & Llama 3.1
Ensure Ollama server is running locally and pull the Llama 3.1 model:
```bash
ollama run llama3.1
```

### 4. Running the Backend Server
```bash
cd backend
venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### 5. Running Automated Tests
```bash
cd backend
$env:PYTHONPATH="."
venv\Scripts\python.exe -m pytest test/
```