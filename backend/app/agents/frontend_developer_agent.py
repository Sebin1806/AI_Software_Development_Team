import json
from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class FrontendDeveloperAgent(BaseAgent):
    agent_name: str = "Frontend Developer"
    agent_role: str = "Frontend UI Components & Application Implementation"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Generate React/TypeScript UI pages and components based on UI/UX designs and API specifications.\n"
            "2. Implement state management, API integration client, and router configuration.\n"
            "3. Provide styles and responsive layout.\n"
            "Include complete frontend code files inside the `files` array of your JSON output format."
        )

    def get_mock_response(self, user_prompt: str, project_context: Dict[str, Any]) -> str:
        mock_data = {
            "summary": "Implemented React + TypeScript components, pages, and API client integration",
            "decisions": ["React 18 with Vite", "TypeScript interface schemas", "Axios client for API communication"],
            "deliverables": ["React components", "API integration client", "Page routing"],
            "files": [
                {
                    "path": "frontend/src/App.tsx",
                    "category": "frontend",
                    "content": "import React from 'react';\nexport default function App() {\n  return <div><h1>Generated App</h1></div>;\n}"
                },
                {
                    "path": "frontend/src/api/client.ts",
                    "category": "frontend",
                    "content": "export async function fetchData() {\n  const res = await fetch('/api/v1/items');\n  return res.json();\n}"
                }
            ]
        }
        return f"```json\n{json.dumps(mock_data, indent=2)}\n```"
