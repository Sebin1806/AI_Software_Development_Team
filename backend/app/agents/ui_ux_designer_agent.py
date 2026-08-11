from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class UIUXDesignerAgent(BaseAgent):
    agent_name: str = "UI/UX Designer"
    agent_role: str = "Interface Design & User Experience Specification"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Define application page layouts, components hierarchy, and visual design tokens.\n"
            "2. Define user navigation flows and screen wireframes.\n"
            "3. Specify color themes (dark/light), typography, and responsive design guidelines.\n"
            "Produce the UI/UX specification document inside a markdown block ````markdown filename=ui_ux_design.md````."
        )
