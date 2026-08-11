from typing import Any, Dict
from uuid import UUID


class WorkflowContext:
    """
    Shared memory context passed across the 12 AI agents during execution.
    Provides selective contextual filtering so each agent receives only relevant inputs.
    """

    CONTEXT_MAP = {
        "Project Manager": [],
        "Business Analyst": ["Project Manager"],
        "Software Architect": ["Project Manager", "Business Analyst"],
        "Database Engineer": ["Business Analyst", "Software Architect"],
        "API Developer": ["Business Analyst", "Software Architect", "Database Engineer"],
        "UI/UX Designer": ["Business Analyst", "Software Architect"],
        "Backend Developer": ["Software Architect", "Database Engineer", "API Developer"],
        "Frontend Developer": ["Software Architect", "UI/UX Designer", "API Developer"],
        "Code Reviewer": ["Database Engineer", "API Developer", "Backend Developer", "Frontend Developer"],
        "Security Engineer": ["Database Engineer", "API Developer", "Backend Developer"],
        "Test Engineer": ["Business Analyst", "API Developer", "Backend Developer", "Frontend Developer"],
        "DevOps Engineer": ["Software Architect", "Database Engineer", "Backend Developer", "Frontend Developer"],
    }

    def __init__(self, task_execution_id: UUID, project_id: UUID, user_prompt: str, project_context: Dict[str, Any]):
        self.task_execution_id = task_execution_id
        self.project_id = project_id
        self.user_prompt = user_prompt
        self.project_context = project_context
        self.previous_outputs: Dict[str, Any] = {}

    def add_agent_output(self, agent_name: str, output: Dict[str, Any]):
        self.previous_outputs[agent_name] = output

    def get_selective_context(self, agent_name: str) -> Dict[str, Any]:
        relevant_agent_names = self.CONTEXT_MAP.get(agent_name, list(self.previous_outputs.keys()))
        filtered_outputs = {}
        for name in relevant_agent_names:
            if name in self.previous_outputs:
                filtered_outputs[name] = self.previous_outputs[name]
        return filtered_outputs
