from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class DatabaseEngineerAgent(BaseAgent):
    agent_name: str = "Database Engineer"
    agent_role: str = "Database Schema & Migration Design"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Design relational database schema (tables, primary/foreign keys, indexes).\n"
            "2. Provide executable PostgreSQL DDL SQL script inside a sql block ````sql filename=schema.sql````.\n"
            "3. Provide ER diagram representation in Mermaid syntax.\n"
            "4. Specify indexing and performance optimization strategies."
        )
