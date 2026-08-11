import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.agents.context import WorkflowContext
from app.agents.project_manager_agent import ProjectManagerAgent
from app.agents.business_analyst_agent import BusinessAnalystAgent
from app.agents.software_architect_agent import SoftwareArchitectAgent
from app.agents.database_engineer_agent import DatabaseEngineerAgent
from app.agents.api_developer_agent import APIDeveloperAgent
from app.agents.ui_ux_designer_agent import UIUXDesignerAgent
from app.agents.backend_developer_agent import BackendDeveloperAgent
from app.agents.frontend_developer_agent import FrontendDeveloperAgent
from app.agents.code_reviewer_agent import CodeReviewerAgent
from app.agents.security_engineer_agent import SecurityEngineerAgent
from app.agents.test_engineer_agent import TestEngineerAgent
from app.agents.devops_engineer_agent import DevOpsEngineerAgent
from app.database.models import AgentArtifact, AgentExecutionLog, Project, TaskExecution
from app.services.file_service import FileService

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Production-ready multi-agent workflow orchestrator for the 12 AI agents.
    Executes agents sequentially in exact required order, isolates artifacts by task ID,
    calculates live progress %, enforces cancellation checks, and generates a final workflow summary.
    """

    AGENT_ORDER: List[str] = [
        "Project Manager",
        "Business Analyst",
        "Software Architect",
        "Database Engineer",
        "API Developer",
        "UI/UX Designer",
        "Backend Developer",
        "Frontend Developer",
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
        "API Developer": APIDeveloperAgent,
        "UI/UX Designer": UIUXDesignerAgent,
        "Backend Developer": BackendDeveloperAgent,
        "Frontend Developer": FrontendDeveloperAgent,
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
    ) -> Dict[str, Any]:
        task = db.query(TaskExecution).filter(TaskExecution.id == task_execution_id).first()
        if not task:
            logger.error(f"TaskExecution {task_execution_id} not found.")
            return {"status": "error", "message": "Task not found"}

        if task.status in ["completed", "failed", "cancelled"]:
            logger.warning(f"TaskExecution {task_execution_id} is already in state '{task.status}'. Aborting duplicate run.")
            return {"status": task.status, "message": f"Task already {task.status}"}

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
        task.current_step = 0
        task.total_steps = len(self.AGENT_ORDER)
        task.percentage_completed = 0
        task.agents_completed = 0
        task.agents_failed = 0
        task.artifacts_generated = 0
        db.commit()

        total_agents = len(self.AGENT_ORDER)
        logger.info(f"Starting execution for Task {task.id} (Project: {task.project_id}) across {total_agents} agents.")

        for step_idx, agent_name in enumerate(self.AGENT_ORDER, start=1):
            # 1. Real Cancellation Check
            db.refresh(task)
            if task.status == "cancelled":
                logger.info(f"Task {task.id} was cancelled by user before step {step_idx} ({agent_name}). Halting execution.")
                return {"status": "cancelled", "message": "Workflow cancelled by user"}

            # Update step progress
            task.current_agent = agent_name
            task.current_step = step_idx
            task.percentage_completed = int(((step_idx - 1) / total_agents) * 100)
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

            # 3. Get selective context & run agent
            selective_payload = context.get_selective_context(agent_name)
            agent_class = self.AGENT_CLASS_MAP[agent_name]
            agent_instance = agent_class(mock_mode=mock_mode)

            result = agent_instance.run(
                user_prompt=context.user_prompt,
                project_context=context.project_context,
                previous_outputs=selective_payload
            )

            # 4. Process agent output & physical disk file writing
            if result.get("status") == "success":
                log_entry.status = "completed"
                log_entry.output_data = {
                    "summary": result.get("summary"),
                    "decisions": result.get("decisions", []),
                    "deliverables": result.get("deliverables", []),
                    "raw_text": result.get("raw_text"),
                    "artifacts_count": len(result.get("artifacts", []))
                }
                log_entry.completed_at = datetime.now(timezone.utc)
                log_entry.retry_count = result.get("retry_count", 0)

                # Save generated files to disk and DB
                for art in result.get("artifacts", []):
                    rel_path, clean_cat, content_hash = FileService.save_file(
                        project_id=task.project_id,
                        task_id=task.id,
                        category=art.get("category", "docs"),
                        file_name=art.get("file_name", "file.txt"),
                        content=art.get("content", "")
                    )

                    # Compute version
                    version = db.query(AgentArtifact).filter(
                        AgentArtifact.project_id == task.project_id,
                        AgentArtifact.file_name == art.get("file_name")
                    ).count() + 1

                    db_artifact = AgentArtifact(
                        task_id=task.id,
                        task_execution_id=task.id,
                        project_id=task.project_id,
                        agent_name=agent_name,
                        file_name=art.get("file_name"),
                        relative_path=rel_path,
                        file_path=rel_path,
                        category=clean_cat,
                        file_type=art.get("file_type", "code"),
                        content=art.get("content", ""),
                        version=version,
                        content_hash=content_hash
                    )
                    db.add(db_artifact)
                    task.artifacts_generated += 1

                context.add_agent_output(agent_name, result)
                task.agents_completed += 1
                task.percentage_completed = int((step_idx / total_agents) * 100)
                db.commit()
                logger.info(f"Step {step_idx}/{total_agents}: {agent_name} COMPLETED. Artifacts created: {len(result.get('artifacts', []))}")

            else:
                log_entry.status = "failed"
                log_entry.error_message = result.get("error_message", "Execution failed")
                log_entry.completed_at = datetime.now(timezone.utc)
                log_entry.retry_count = result.get("retry_count", 0)

                task.agents_failed += 1
                task.status = "failed"
                task.completed_at = datetime.now(timezone.utc)
                db.commit()
                logger.error(f"Step {step_idx}/{total_agents}: {agent_name} FAILED. Workflow aborted.")
                return {"status": "failed", "failed_agent": agent_name}

        # 5. Workflow Finalization & Synthesis
        db.refresh(task)
        if task.status not in ["cancelled", "failed"]:
            task.status = "completed"
            task.current_agent = None
            task.percentage_completed = 100
            task.completed_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"Task {task.id} COMPLETED successfully across all 12 agents. Total artifacts: {task.artifacts_generated}")

        return {"status": task.status}