import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Type
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.agents.context import WorkflowContext
from app.agents.project_manager_agent import ProjectManagerAgent
from app.agents.business_analyst_agent import BusinessAnalystAgent
from app.agents.software_architect_agent import SoftwareArchitectAgent
from app.agents.database_engineer_agent import DatabaseEngineerAgent
from app.agents.ui_ux_designer_agent import UIUXDesignerAgent
from app.agents.frontend_developer_agent import FrontendDeveloperAgent
from app.agents.backend_developer_agent import BackendDeveloperAgent
from app.agents.api_developer_agent import APIDeveloperAgent
from app.agents.code_reviewer_agent import CodeReviewerAgent
from app.agents.security_engineer_agent import SecurityEngineerAgent
from app.agents.test_engineer_agent import TestEngineerAgent
from app.agents.devops_engineer_agent import DevOpsEngineerAgent
from app.database.models import AgentArtifact, AgentExecutionLog, Project, TaskExecution

logger = logging.getLogger(__name__)


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

    AGENT_CLASS_MAP: Dict[str, Type[BaseAgent]] = {
        "Project Manager": ProjectManagerAgent,
        "Business Analyst": BusinessAnalystAgent,
        "Software Architect": SoftwareArchitectAgent,
        "Database Engineer": DatabaseEngineerAgent,
        "UI/UX Designer": UIUXDesignerAgent,
        "Frontend Developer": FrontendDeveloperAgent,
        "Backend Developer": BackendDeveloperAgent,
        "API Developer": APIDeveloperAgent,
        "Code Reviewer": CodeReviewerAgent,
        "Security Engineer": SecurityEngineerAgent,
        "Test Engineer": TestEngineerAgent,
        "DevOps Engineer": DevOpsEngineerAgent,
    }

    def get_execution_order(self) -> List[str]:
        return self.AGENT_ORDER

    def get_next_agent(self, completed_agents: List[str]) -> Optional[str]:
        for agent in self.AGENT_ORDER:
            if agent not in completed_agents:
                return agent
        return None

    def execute_task(
        self,
        db: Session,
        task_execution_id: UUID,
        mock_mode: Optional[bool] = None
    ) -> Dict[str, str]:
        """
        Executes the 12-agent sequential workflow for a TaskExecution record.
        Integrates database tracking, context passing, artifact storage, and cancellation checks.
        """
        task = db.query(TaskExecution).filter(TaskExecution.id == task_execution_id).first()
        if not task:
            logger.error(f"TaskExecution {task_execution_id} not found.")
            return {"status": "error", "message": "Task not found"}

        project = db.query(Project).filter(Project.id == task.project_id).first()
        project_info = {
            "id": str(project.id) if project else "",
            "name": project.name if project else "Software Project",
            "description": project.description if project else ""
        }

        context = WorkflowContext(
            task_execution_id=task.id,
            project_id=task.project_id,
            user_prompt=task.user_prompt,
            project_context=project_info
        )

        task.status = "running"
        db.commit()

        logger.info(f"Starting execution for TaskExecution {task.id} (Project: {task.project_id})")

        for step_idx, agent_name in enumerate(self.AGENT_ORDER, start=1):
            # 1. Check Cancellation Status
            db.refresh(task)
            if task.status == "cancelled":
                logger.info(f"TaskExecution {task.id} was cancelled by user. Halting workflow.")
                break

            task.current_agent = agent_name
            db.commit()

            # 2. Create AgentExecutionLog
            log_entry = AgentExecutionLog(
                task_execution_id=task.id,
                project_id=task.project_id,
                agent_name=agent_name,
                step_number=step_idx,
                status="running",
                input_data={"user_prompt": task.user_prompt, "agent": agent_name},
                started_at=datetime.now(timezone.utc)
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)

            # 3. Instantiate and run agent
            agent_class = self.AGENT_CLASS_MAP[agent_name]
            agent_instance = agent_class(mock_mode=mock_mode)

            result = agent_instance.run(
                user_prompt=context.user_prompt,
                project_context=context.project_context,
                previous_outputs=context.previous_outputs
            )

            # 4. Handle Execution Result
            if result.get("status") == "success":
                log_entry.status = "completed"
                log_entry.output_data = {
                    "summary": result.get("summary"),
                    "raw_text": result.get("raw_text"),
                    "artifacts_count": len(result.get("artifacts", []))
                }
                log_entry.completed_at = datetime.now(timezone.utc)
                log_entry.retry_count = result.get("retry_count", 0)

                # Store Artifacts
                for art in result.get("artifacts", []):
                    db_artifact = AgentArtifact(
                        task_execution_id=task.id,
                        project_id=task.project_id,
                        agent_name=agent_name,
                        file_name=art["file_name"],
                        file_type=art["file_type"],
                        content=art["content"]
                    )
                    db.add(db_artifact)

                context.add_agent_output(agent_name, result)
                db.commit()
                logger.info(f"Step {step_idx}/{len(self.AGENT_ORDER)}: {agent_name} COMPLETED")

            else:
                log_entry.status = "failed"
                log_entry.error_message = result.get("error_message", "Execution failed")
                log_entry.completed_at = datetime.now(timezone.utc)
                log_entry.retry_count = result.get("retry_count", 0)

                task.status = "failed"
                task.completed_at = datetime.now(timezone.utc)
                db.commit()
                logger.error(f"Step {step_idx}/{len(self.AGENT_ORDER)}: {agent_name} FAILED. Workflow aborted.")
                return {"status": "failed", "failed_agent": agent_name}

        # 5. Finalize Task
        db.refresh(task)
        if task.status != "cancelled" and task.status != "failed":
            task.status = "completed"
            task.current_agent = None
            task.completed_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"TaskExecution {task.id} fully completed all 12 agents successfully.")

        return {"status": task.status}