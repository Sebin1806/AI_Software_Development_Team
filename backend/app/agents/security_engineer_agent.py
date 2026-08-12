import json
from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class SecurityEngineerAgent(BaseAgent):
    agent_name: str = "Security Engineer"
    agent_role: str = "OWASP Security Audit & Vulnerability Assessment"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Audit generated application code against OWASP Top 10 security risks.\n"
            "2. Verify JWT authentication security, password hashing, SQL injection prevention, and CORS policies.\n"
            "3. Identify any hardcoded credentials, unhandled exceptions, or unescaped outputs.\n"
            "Include your security report and remediation policy inside the `files` array of your JSON output format."
        )

    def get_mock_response(self, user_prompt: str, project_context: Dict[str, Any]) -> str:
        mock_data = {
            "summary": "Completed OWASP Top 10 security audit and credential leak scan",
            "decisions": [
                "PASSED: Passlib bcrypt password hashing verified",
                "PASSED: Parameterized SQLAlchemy queries prevent SQL injection",
                "SECURITY ADVISORY: Ensure JWT SECRET_KEY is supplied via environment variables in production"
            ],
            "deliverables": ["OWASP Security Audit Report", "Hardcoded Credentials Scan Results"],
            "files": [
                {
                    "path": "docs/security_audit.md",
                    "category": "docs",
                    "content": "# OWASP Security Audit Report\n\n- OWASP Top 10 Assessment: Compliant\n- Authentication: Bearer JWT verified."
                }
            ]
        }
        return f"```json\n{json.dumps(mock_data, indent=2)}\n```"
