from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class BusinessAnalystAgent(BaseAgent):
    agent_name: str = "Business Analyst"
    agent_role: str = "Requirements Analysis & Specification"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Analyze functional and non-functional requirements based on the project plan.\n"
            "2. Define user roles and personas.\n"
            "3. Create detailed User Stories with Acceptance Criteria (Given-When-Then format).\n"
            "4. Identify potential edge cases and constraints.\n"
            "Produce the complete requirements specification document in a markdown block ````markdown filename=requirements.md````."
        )
