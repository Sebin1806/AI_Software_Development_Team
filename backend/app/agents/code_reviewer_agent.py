import json
from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class CodeReviewerAgent(BaseAgent):
    agent_name: str = "Code Reviewer"
    agent_role: str = "Source Code Quality & AST Syntax Audit"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Inspect generated frontend, backend, database, and API code for AST syntax errors, anti-patterns, and code smells.\n"
            "2. Verify adherence to SOLID principles, clean code structure, and error handling.\n"
            "3. Highlight specific findings, syntax validation status, and recommended refactoring items.\n"
            "Include deliverables inside the `files` array of your JSON output format."
        )

    def get_mock_response(self, user_prompt: str, project_context: Dict[str, Any]) -> str:
        mock_data = {
            "summary": "Completed AST syntax review and code quality audit across frontend and backend codebases",
            "decisions": [
                "PASSED: All generated Python files passed AST syntax parsing",
                "PASSED: Clean separation of service layers and ORM repositories",
                "RECOMMENDATION: Add typed Pydantic request body schemas to remaining endpoints"
            ],
            "deliverables": ["Code Quality Audit Report", "Refactoring Checklist"],
            "files": [
                {
                    "path": "docs/code_review.md",
                    "category": "docs",
                    "content": "# Code Review Audit Report\n\n- Syntax Validation: 100% Passed\n- Architecture: Layered FastAPI + React pattern verified."
                }
            ]
        }
        return f"```json\n{json.dumps(mock_data, indent=2)}\n```"
