import logging
import re
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all 12 specialized AI agents.
    Provides standard prompt building, shared context handling, LLM execution with retry logic,
    and automatic artifact extraction.
    """

    agent_name: str = "Base Agent"
    agent_role: str = "General Assistant"
    max_retries: int = 3

    def __init__(self, mock_mode: Optional[bool] = None):
        self.mock_mode = mock_mode

    def get_system_prompt(self) -> str:
        return (
            f"You are the {self.agent_name} in an automated multi-agent software development team.\n"
            f"Your Role: {self.agent_role}.\n"
            f"You must deliver high-quality, precise, comprehensive, and professional software engineering outputs.\n"
            f"When generating code, SQL, configuration, or documentation, present complete code inside fenced code blocks "
            f"with file names specified where applicable (e.g. ```python filename=main.py or ```sql filename=schema.sql)."
        )

    def build_user_prompt(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        prompt_parts = [
            f"### PROJECT INFORMATION",
            f"Project Name: {project_context.get('name', 'Software Project')}",
            f"Description: {project_context.get('description', 'N/A')}",
            f"\n### USER REQUIREMENT",
            f"{user_prompt}",
        ]

        if previous_outputs:
            prompt_parts.append("\n### PREVIOUS AGENT OUTPUTS & SHARED MEMORY")
            for prev_agent, output in previous_outputs.items():
                prompt_parts.append(f"\n--- Output from {prev_agent} ---")
                if isinstance(output, dict):
                    summary = output.get("summary", "")
                    content = output.get("raw_text", str(output))
                    prompt_parts.append(f"Summary: {summary}\n{content[:2000]}")
                else:
                    prompt_parts.append(str(output)[:2000])

        prompt_parts.append(f"\n### YOUR TASK ({self.agent_name})")
        prompt_parts.append(self.get_task_instructions(user_prompt, project_context, previous_outputs))

        return "\n".join(prompt_parts)

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return f"Perform your specific duty as {self.agent_name} based on the user requirement and context above."

    def extract_artifacts(self, text: str) -> List[Dict[str, str]]:
        """
        Extract code blocks and files from LLM text response.
        Looks for ```lang filename=path/file.ext or standard code blocks.
        """
        artifacts = []
        code_block_pattern = re.compile(
            r"```(?:([a-zA-Z0-9_\-+]+))?(?:\s+filename=([^\n]+))?\n(.*?)```",
            re.DOTALL
        )

        matches = code_block_pattern.findall(text)
        default_counter = 1

        for lang, fname, code in matches:
            lang = lang.strip() if lang else "txt"
            code = code.strip()
            if not code:
                continue

            if fname:
                file_name = fname.strip()
            else:
                ext_map = {
                    "python": "py", "py": "py", "javascript": "js", "js": "js",
                    "typescript": "ts", "ts": "ts", "tsx": "tsx", "jsx": "jsx",
                    "html": "html", "css": "css", "sql": "sql", "json": "json",
                    "yaml": "yaml", "yml": "yml", "dockerfile": "Dockerfile",
                    "bash": "sh", "sh": "sh", "markdown": "md", "md": "md"
                }
                ext = ext_map.get(lang.lower(), lang.lower())
                file_name = f"{self.agent_name.lower().replace(' ', '_')}_artifact_{default_counter}.{ext}"
                default_counter += 1

            artifacts.append({
                "file_name": file_name,
                "file_type": lang if lang else "code",
                "content": code
            })

        return artifacts

    def run(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = self.get_system_prompt()
        prompt = self.build_user_prompt(user_prompt, project_context, previous_outputs)

        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Executing {self.agent_name} (Attempt {attempt}/{self.max_retries})")
                if self.mock_mode or (self.mock_mode is None and settings.LLM_MOCK_MODE):
                    raw_response = (
                        f"[MOCK AI RESPONSE for {self.agent_name}]\n"
                        f"Processed task requirements for project.\n\n"
                        f"```markdown filename={self.agent_name.lower().replace(' ', '_')}_output.md\n"
                        f"# {self.agent_name} Deliverable\n"
                        f"Completed work for user prompt.\n"
                        f"```"
                    )
                else:
                    raw_response = LLMService.generate(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=0.7,
                        mock_mode=self.mock_mode
                    )

                artifacts = self.extract_artifacts(raw_response)
                summary_line = raw_response.strip().split("\n")[0][:150] if raw_response else "Execution completed."

                return {
                    "agent_name": self.agent_name,
                    "status": "success",
                    "summary": summary_line,
                    "raw_text": raw_response,
                    "artifacts": artifacts,
                    "retry_count": attempt - 1
                }

            except Exception as e:
                logger.warning(f"Error in {self.agent_name} attempt {attempt}: {str(e)}")
                last_exception = e

        return {
            "agent_name": self.agent_name,
            "status": "failed",
            "summary": f"Failed after {self.max_retries} attempts",
            "raw_text": str(last_exception),
            "artifacts": [],
            "error_message": str(last_exception),
            "retry_count": self.max_retries
        }
