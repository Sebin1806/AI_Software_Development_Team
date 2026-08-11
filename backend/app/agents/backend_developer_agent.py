import json
from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class BackendDeveloperAgent(BaseAgent):
    agent_name: str = "Backend Developer"
    agent_role: str = "Backend Services & Business Logic Implementation"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Implement backend business logic using Python FastAPI and SQLAlchemy.\n"
            "2. Implement database models, repository services, and authentication handlers based on API specs.\n"
            "3. Ensure clean architecture with proper exception handling.\n"
            "Include complete backend code files inside the `files` array of your JSON output format."
        )

    def get_mock_response(self, user_prompt: str, project_context: Dict[str, Any]) -> str:
        mock_data = {
            "summary": "Implemented backend FastAPI models, routes, and business logic services",
            "decisions": ["FastAPI framework", "SQLAlchemy ORM models", "Layered service repository pattern"],
            "deliverables": ["Backend service implementation", "Database ORM models"],
            "files": [
                {
                    "path": "backend/app/main.py",
                    "category": "backend",
                    "content": "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'status': 'active'}"
                },
                {
                    "path": "backend/app/services/main_service.py",
                    "category": "backend",
                    "content": "class MainService:\n    def get_data(self):\n        return {'data': 'sample'}"
                }
            ]
        }
        return f"```json\n{json.dumps(mock_data, indent=2)}\n```"
