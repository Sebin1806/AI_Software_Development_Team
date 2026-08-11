from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class CodeReviewerAgent(BaseAgent):
    agent_name: str = "Code Reviewer"
    agent_role: str = "Source Code Quality & Refactoring Analysis"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Inspect generated frontend, backend, and API code for bugs, anti-patterns, and code smells.\n"
            "2. Verify adherence to SOLID principles, DRY, clean code, and performance best practices.\n"
            "3. Highlight specific issues and provide recommended refactored code snippets.\n"
            "Produce the complete Code Review report inside a markdown code block ````markdown filename=code_review.md````."
        )
