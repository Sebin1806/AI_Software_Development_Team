# AI Software Development Team Platform

## Overview

**AI Software Development Team Platform** is a full-stack multi-agent AI system that simulates an autonomous software engineering organization. Given a high-level user prompt, the system coordinates a sequential 12-agent workflow to analyze requirements, design architecture, produce PostgreSQL database schemas, construct OpenAPI REST contracts, generate React frontend & FastAPI backend source code, conduct automated code reviews, audit security vulnerabilities, generate pytest suites, and produce containerized deployment configurations.

All generated project artifacts are safely saved on physical disk under `generated_projects/<project_id>/<task_id>/` and tracked securely in PostgreSQL.

---

## ⚡ Quick Start Guide (Windows)

### Step 1: Run Automated Setup (One Time)
Double-click `setup.bat` or run in Command Prompt / PowerShell:
```cmd
setup.bat
```
This script automatically:
- Checks Python 3.11+ installation
- Creates Python virtual environment (`backend\venv`)
- Installs backend Python dependencies
- Installs frontend npm packages (`frontend\node_modules`)
- Configures database & runs Alembic migrations
- Checks Ollama AI service status

### Step 2: Start the Application
Double-click `start.bat` or run in Command Prompt / PowerShell:
```cmd
start.bat
```
This will launch both the FastAPI Backend and React Frontend in separate windows.

### Step 3: Open the Web Application
Open your browser and navigate to:
- **Frontend Web App**: `http://localhost:5173`
- **Backend Swagger API Docs**: `http://localhost:8000/docs`

### Step 4: Stop Application Servers
Run `stop.bat` to stop all running application servers cleanly:
```cmd
stop.bat
```

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

## Manual Setup & CLI Instructions

### 1. Environment Setup
Copy `.env.example` to `backend/.env`:
```bash
cp .env.example backend/.env
```

### 2. Database Migrations (Alembic)
Ensure PostgreSQL is running and database `ai_software_team` exists:
```bash
cd backend
$env:PYTHONPATH="."
venv\Scripts\python.exe -m alembic upgrade head
```

### 3. Ollama & Llama 3.1 Setup
Install Ollama and pull the Llama 3.1 model:
```bash
ollama run llama3.1
```

### 4. Running Automated Pytest Suite
```bash
cd backend
$env:PYTHONPATH="."
venv\Scripts\pytest.exe test/ -v
```