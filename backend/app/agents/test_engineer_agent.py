from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class TestEngineerAgent(BaseAgent):
    agent_name: str = "Test Engineer"
    agent_role: str = "Automated Test Suite & QA Strategy"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Develop comprehensive test plan, unit tests, integration tests, and API test cases.\n"
            "2. Produce executable Python pytest test suite inside ````python filename=tests/test_application.py````.\n"
            "3. Produce test runner instructions and test report in ````markdown filename=test_plan.md````."
        )
