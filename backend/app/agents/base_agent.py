import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all 12 specialized AI agents.
    Provides standard prompt building, selective context handling, LLM execution with retry logic,
    structured JSON parsing with fenced code block fallback, and artifact extraction.
    """

    agent_name: str = "Base Agent"
    agent_role: str = "General Assistant"
    max_retries: int = 3

    def __init__(self, mock_mode: Optional[bool] = None):
        self.mock_mode = mock_mode

    def get_system_prompt(self) -> str:
        return (
            f"You are the {self.agent_name} in an automated 12-agent software engineering team.\n"
            f"Role: {self.agent_role}.\n"
            f"Your output MUST be high quality, precise, non-hallucinated, and formatted as a JSON object matching this structure:\n"
            "```json\n"
            "{\n"
            '  "summary": "Brief summary of your work",\n'
            '  "decisions": ["Key engineering decision 1", "Key decision 2"],\n'
            '  "deliverables": ["Deliverable 1 description", "Deliverable 2"],\n'
            '  "files": [\n'
            '    {\n'
            '      "path": "relative/file/path.ext",\n'
            '      "category": "frontend|backend|database|docs|deployment|tests",\n'
            '      "content": "Complete code or document text here"\n'
            '    }\n'
            '  ]\n'
            "}\n"
            "```\n"
            "If code or documents are required, place them inside the `files` array with complete content."
        )

    def build_user_prompt(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        prompt_parts = [
            f"### PROJECT METADATA",
            f"Project Name: {project_context.get('name', 'Software Project')}",
            f"Description: {project_context.get('description', 'N/A')}",
            f"\n### ORIGINAL USER REQUIREMENT",
            f"{user_prompt}",
        ]

        if previous_outputs:
            prompt_parts.append("\n### RELEVANT PREVIOUS AGENT OUTPUTS")
            for prev_agent, output in previous_outputs.items():
                prompt_parts.append(f"\n--- Output from {prev_agent} ---")
                if isinstance(output, dict):
                    summary = output.get("summary", "")
                    decisions = output.get("decisions", [])
                    content = output.get("raw_text", str(output))
                    prompt_parts.append(f"Summary: {summary}")
                    if decisions:
                        prompt_parts.append(f"Decisions: {', '.join(decisions)}")
                    prompt_parts.append(f"Details:\n{content[:2500]}")
                else:
                    prompt_parts.append(str(output)[:2500])

        prompt_parts.append(f"\n### YOUR TASK ({self.agent_name})")
        prompt_parts.append(self.get_task_instructions(user_prompt, project_context, previous_outputs))

        return "\n".join(prompt_parts)

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return f"Perform your specific duty as {self.agent_name} based on the requirement and context above."

    def parse_output(self, text: str) -> Dict[str, Any]:
        """
        Parses LLM output into structured dict and extracts artifacts.
        Tries JSON parsing first; falls back to markdown & fenced code block extraction.
        """
        result = {
            "summary": "",
            "decisions": [],
            "deliverables": [],
            "artifacts": []
        }

        # 1. Attempt JSON block extraction
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        raw_json = json_match.group(1) if json_match else text

        try:
            parsed = json.loads(raw_json)
            if isinstance(parsed, dict):
                result["summary"] = parsed.get("summary", "")
                result["decisions"] = parsed.get("decisions", [])
                result["deliverables"] = parsed.get("deliverables", [])

                for f in parsed.get("files", []):
                    if isinstance(f, dict) and f.get("path") and f.get("content"):
                        file_name = os.path.basename(f["path"])
                        ext = file_name.split(".")[-1] if "." in file_name else "txt"
                        result["artifacts"].append({
                            "file_name": file_name,
                            "relative_path": f["path"],
                            "category": f.get("category", "docs"),
                            "file_type": ext,
                            "content": f["content"]
                        })
                if result["artifacts"]:
                    return result
        except Exception:
            pass

        # 2. Fallback: Extract fenced code blocks
        code_block_pattern = re.compile(
            r"```(?:([a-zA-Z0-9_\-+]+))?(?:\s+filename=([^\n]+))?\n(.*?)```",
            re.DOTALL
        )
        matches = code_block_pattern.findall(text)
        default_counter = 1

        for lang, fname, code in matches:
            lang = lang.strip() if lang else "txt"
            code = code.strip()
            if not code or lang == "json":
                continue

            file_name = fname.strip() if fname else f"{self.agent_name.lower().replace(' ', '_')}_{default_counter}.{lang}"
            default_counter += 1

            result["artifacts"].append({
                "file_name": file_name,
                "relative_path": file_name,
                "category": "docs",
                "file_type": lang,
                "content": code
            })

        if not result["summary"]:
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            result["summary"] = lines[0][:150] if lines else f"{self.agent_name} output generated."

        return result

    def get_mock_response(self, user_prompt: str, project_context: Dict[str, Any]) -> str:
        agent_slug = self.agent_name.lower().replace(' ', '_')
        mock_data = {
            "summary": f"{self.agent_name} completed task for project {project_context.get('name', 'App')}",
            "decisions": [f"Selected standard architecture pattern for {self.agent_name}"],
            "deliverables": [f"{self.agent_name} specification & deliverable"],
            "files": [
                {
                    "path": f"{agent_slug}_output.md",
                    "category": "docs",
                    "content": f"# {self.agent_name} Deliverable\n\nCompleted tasks for user requirement: {user_prompt[:100]}"
                }
            ]
        }
        return f"```json\n{json.dumps(mock_data, indent=2)}\n```"

    def run(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = self.get_system_prompt()
        prompt = self.build_user_prompt(user_prompt, project_context, previous_outputs)

        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Executing {self.agent_name} (Attempt {attempt}/{self.max_retries})")
                if self.mock_mode or (self.mock_mode is None and settings.LLM_MOCK_MODE):
                    raw_response = self.get_mock_response(user_prompt, project_context)
                else:
                    raw_response = LLMService.generate(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=0.7,
                        mock_mode=self.mock_mode
                    )

                parsed_data = self.parse_output(raw_response)

                return {
                    "agent_name": self.agent_name,
                    "status": "success",
                    "summary": parsed_data["summary"],
                    "decisions": parsed_data["decisions"],
                    "deliverables": parsed_data["deliverables"],
                    "raw_text": raw_response,
                    "artifacts": parsed_data["artifacts"],
                    "retry_count": attempt - 1
                }

            except Exception as e:
                logger.warning(f"Error in {self.agent_name} attempt {attempt}: {str(e)}")
                last_exception = e

        return {
            "agent_name": self.agent_name,
            "status": "failed",
            "summary": f"Failed after {self.max_retries} attempts",
            "decisions": [],
            "deliverables": [],
            "raw_text": str(last_exception),
            "artifacts": [],
            "error_message": str(last_exception),
            "retry_count": self.max_retries
        }
