from typing import Any, Dict, Optional
from uuid import UUID


class WorkflowContext:
    """
    Shared memory context passed across all 12 AI agents during execution.
    """

    def __init__(self, task_execution_id: UUID, project_id: UUID, user_prompt: str, project_context: Dict[str, Any]):
        self.task_execution_id = task_execution_id
        self.project_id = project_id
        self.user_prompt = user_prompt
        self.project_context = project_context
        self.previous_outputs: Dict[str, Any] = {}

    def add_agent_output(self, agent_name: str, output: Dict[str, Any]):
        self.previous_outputs[agent_name] = output

    def get_agent_payload(self) -> Dict[str, Any]:
        return {
            "task_execution_id": str(self.task_execution_id),
            "project_id": str(self.project_id),
            "user_prompt": self.user_prompt,
            "project_context": self.project_context,
            "previous_outputs": self.previous_outputs,
        }
