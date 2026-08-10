from typing import List


class AgentOrchestrator:

    AGENT_ORDER: List[str] = [
        "Project Manager",
        "Business Analyst",
        "Software Architect",
        "Database Engineer",
        "UI/UX Designer",
        "Frontend Developer",
        "Backend Developer",
        "API Developer",
        "Code Reviewer",
        "Security Engineer",
        "Test Engineer",
        "DevOps Engineer",
    ]

    def get_execution_order(self):
        return self.AGENT_ORDER

    def get_next_agent(self, completed_agents: List[str]):
        for agent in self.AGENT_ORDER:
            if agent not in completed_agents:
                return agent

        return None