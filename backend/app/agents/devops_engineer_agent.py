from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class DevOpsEngineerAgent(BaseAgent):
    agent_name: str = "DevOps Engineer"
    agent_role: str = "Containerization, CI/CD & Deployment Configuration"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Produce containerization Dockerfile for backend/frontend in ````dockerfile filename=Dockerfile````.\n"
            "2. Produce multi-container orchestration config in ````yaml filename=docker-compose.yml````.\n"
            "3. Produce GitHub Actions CI/CD pipeline workflow in ````yaml filename=.github/workflows/deploy.yml````.\n"
            "4. Provide complete Deployment Guide in ````markdown filename=deployment_guide.md````."
        )
