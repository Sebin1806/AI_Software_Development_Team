import json
from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class APIDeveloperAgent(BaseAgent):
    agent_name: str = "API Developer"
    agent_role: str = "REST API Specification & Contract Design"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Design RESTful API endpoints based on system architecture and database design.\n"
            "2. Define request payloads, path parameters, query parameters, response schemas, and status codes.\n"
            "3. Produce complete OpenAPI 3.0 specification in YAML/JSON and FastAPI route definitions.\n"
            "Include your deliverables inside the `files` array of your JSON output format."
        )

    def get_mock_response(self, user_prompt: str, project_context: Dict[str, Any]) -> str:
        mock_data = {
            "summary": "Designed REST API endpoints and OpenAPI 3.0 specification",
            "decisions": ["RESTful resource URLs", "JSON request/response format", "Bearer JWT header authentication"],
            "deliverables": ["OpenAPI 3.0 specification", "FastAPI route contract"],
            "files": [
                {
                    "path": "docs/openapi.yaml",
                    "category": "docs",
                    "content": "openapi: 3.0.0\ninfo:\n  title: Project API\n  version: 1.0.0\npaths:\n  /api/v1/resources:\n    get:\n      summary: List resources\n      responses:\n        '200':\n          description: Success"
                },
                {
                    "path": "backend/app/api/v1_routes.py",
                    "category": "backend",
                    "content": "from fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get('/items')\ndef list_items():\n    return {'items': []}"
                }
            ]
        }
        return f"```json\n{json.dumps(mock_data, indent=2)}\n```"
