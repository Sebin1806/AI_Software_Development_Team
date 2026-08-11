from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class SecurityEngineerAgent(BaseAgent):
    agent_name: str = "Security Engineer"
    agent_role: str = "Security Vulnerability & Compliance Audit"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Audit application architecture, code, and database schema for OWASP Top 10 security risks.\n"
            "2. Evaluate authentication, authorization, secret management, SQL injection, and XSS mitigations.\n"
            "3. Provide actionable security recommendations and hardened code configuration snippets.\n"
            "Produce the Security Audit report inside a markdown code block ````markdown filename=security_audit.md````."
        )
