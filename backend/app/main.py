from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.core.config import settings
from app.api.project import router as project_router
from app.api.agent import router as agent_router
from app.api.orchestrator import router as orchestrator_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React/Vite frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    orchestrator_router,
    prefix="/api/orchestrator",
    tags=["Agent Orchestrator"]
)


app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"]
)


app.include_router(
    project_router,
    prefix="/api/projects",
    tags=["Projects"]
)

app.include_router(
    agent_router,
    prefix="/api/agents",
    tags=["Agents"]
)


@app.get("/")
def home():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "Running",
        "message": "AI Software Development Team Backend"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }