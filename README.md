# AI Software Development Team Platform

## Overview

**AI Software Development Team Platform** is a full-stack multi-agent AI system that simulates an autonomous software engineering organization. Given a high-level user prompt, the system coordinates a sequential 12-agent workflow to analyze requirements, design architecture, produce PostgreSQL database schemas, construct OpenAPI REST contracts, generate React frontend & FastAPI backend source code, conduct automated code reviews, audit security vulnerabilities, generate pytest suites, and produce containerized deployment configurations.

All generated project artifacts are safely saved on physical disk under `generated_projects/<project_id>/<task_id>/` and tracked securely in PostgreSQL.

---

## 12-Agent Workflow Execution Order

```
User Requirement
      │
      ▼
1. Project Manager       (Workflow & Project Roadmap)
      │
      ▼
2. Business Analyst      (Requirements Specification & User Stories)
      │
      ▼
3. Software Architect    (System Architecture & Directory Design)
      │
      ▼
4. Database Engineer     (PostgreSQL DDL Schemas & ER Diagrams)
      │
      ▼
5. API Developer         (REST Endpoints & OpenAPI 3.0 Specifications)
      │
      ▼
6. UI/UX Designer        (Interface Design & Layout Guidelines)
      │
      ▼
7. Backend Developer     (FastAPI Implementation & Services)
      │
      ▼
8. Frontend Developer    (React / TypeScript Components & Pages)
      │
      ▼
9. Code Reviewer         (Code Quality & Architecture Audit)
      │
      ▼
10. Security Engineer    (OWASP Security Audit & Vulnerability Assessment)
      │
      ▼
11. Test Engineer        (Automated Pytest Suite & QA Plan)
      │
      ▼
12. DevOps Engineer      (Dockerfile, Docker Compose & CI/CD Pipelines)
      │
      ▼
Generated Project Artifacts & Files
```

---

## Generated Project Directory Structure

Artifacts are isolated per workflow task execution:
```
generated_projects/
    <project_id>/
        <task_id>/
            frontend/       (React / TypeScript source files)
            backend/        (FastAPI routes, models, services)
            database/       (SQL DDL schemas & migrations)
            tests/          (Automated test files)
            docs/           (OpenAPI specs & architecture docs)
            deployment/     (Dockerfile, docker-compose.yml)
            README.md       (Generated project overview)
```

---

## API Documentation & OpenAPI Spec

### Authentication
- `POST /api/auth/register` - Register user account
- `POST /api/auth/login` - Obtain JWT access token
- `GET /api/auth/profile` - Get current authenticated profile

### Projects
- `POST /api/projects` - Create software project
- `GET /api/projects` - List user projects
- `GET /api/projects/{project_id}` - Get project details
- `DELETE /api/projects/{project_id}` - Delete project

### Workflow Orchestrator
- `GET /api/orchestrator/order` - Get 12-agent execution order
- `POST /api/orchestrator/start` - Launch background development workflow
- `GET /api/orchestrator/status/{task_id}` - Poll live status, current step, %, and logs
- `GET /api/orchestrator/results/{task_id}` - Get complete structured results summary
- `POST /api/orchestrator/cancel/{task_id}` - Request workflow cancellation

### Artifacts (JWT Protected)
- `GET /api/projects/{project_id}/artifacts` - List project artifacts
- `GET /api/orchestrator/results/{task_id}/artifacts` - List task artifacts
- `GET /api/projects/{project_id}/artifacts/{artifact_id}` - View artifact details
- `GET /api/projects/{project_id}/artifacts/{artifact_id}/download` - Download file

---

## Installation & Setup Instructions

### 1. Environment Setup
Copy `.env.example` to `.env` inside the `backend` folder:
```bash
cp backend/.env.example backend/.env
```

### 2. Database Migration (Alembic)
Ensure PostgreSQL is running and database `ai_software_team` is created:
```bash
cd backend
$env:PYTHONPATH="."
venv\Scripts\alembic.exe upgrade head
```

### 3. Ollama & Llama 3.1 Setup
Install Ollama and pull the Llama 3.1 model:
```bash
ollama run llama3.1
```

### 4. Running the Backend Server
```bash
cd backend
$env:PYTHONPATH="."
venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
FastAPI Swagger documentation will be available at: `http://127.0.0.1:8000/docs`

### 5. Running the Frontend Application
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

### 6. Running Automated Pytest Suite
```bash
cd backend
$env:PYTHONPATH="."
venv\Scripts\python.exe -m pytest test/ -v
```