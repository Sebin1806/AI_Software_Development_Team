from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class ProjectManagerAgent(BaseAgent):
    agent_name: str = "Project Manager"
    agent_role: str = "Project Workflow & Execution Planning"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Analyze the user prompt and software request.\n"
            "2. Define the project scope, objectives, and high-level milestones.\n"
            "3. Outline the execution plan across the 12 agent team.\n"
            "4. Specify recommended tech stack and module breakdown.\n"
            "Produce a structured project roadmap document inside a markdown code block ````markdown filename=project_plan.md````."
        )
