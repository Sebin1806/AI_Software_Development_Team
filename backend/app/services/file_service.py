import hashlib
import logging
import os
from pathlib import Path
from typing import Dict, Any, Tuple
from uuid import UUID

logger = logging.getLogger(__name__)

BASE_GENERATED_DIR = Path("generated_projects").resolve()


class FileService:
    """
    Physical disk file generation and path safety service.
    Ensures generated files are stored isolated under generated_projects/<project_id>/<task_id>/<category>/<file_name>.
    Enforces strict path sanitization to prevent directory traversal attacks (../).
    """

    CATEGORY_MAP = {
        "frontend": "frontend",
        "backend": "backend",
        "database": "database",
        "sql": "database",
        "tests": "tests",
        "test": "tests",
        "docs": "docs",
        "markdown": "docs",
        "deployment": "deployment",
        "dockerfile": "deployment",
        "yaml": "deployment",
        "yml": "deployment"
    }

    @classmethod
    def resolve_category(cls, category: str, file_name: str) -> str:
        cat_lower = category.lower().strip() if category else ""
        if cat_lower in cls.CATEGORY_MAP:
            return cls.CATEGORY_MAP[cat_lower]

        ext = file_name.split(".")[-1].lower() if "." in file_name else ""
        ext_category = {
            "tsx": "frontend", "jsx": "frontend", "js": "frontend", "html": "frontend", "css": "frontend",
            "py": "backend",
            "sql": "database",
            "yaml": "deployment", "yml": "deployment", "dockerfile": "deployment",
            "md": "docs", "txt": "docs"
        }
        return ext_category.get(ext, "docs")

    @classmethod
    def get_safe_task_dir(cls, project_id: UUID, task_id: UUID) -> Path:
        target_dir = (BASE_GENERATED_DIR / str(project_id) / str(task_id)).resolve()
        if not str(target_dir).startswith(str(BASE_GENERATED_DIR)):
            raise ValueError(f"Unsafe directory traversal detected: {target_dir}")
        return target_dir

    @classmethod
    def save_file(
        cls,
        project_id: UUID,
        task_id: UUID,
        category: str,
        file_name: str,
        content: str
    ) -> Tuple[str, str, str]:
        """
        Saves a generated file to disk safely.
        Returns Tuple[relative_path, category, content_hash].
        """
        clean_category = cls.resolve_category(category, file_name)
        task_dir = cls.get_safe_task_dir(project_id, task_id)
        
        # Sanitize file_name to prevent directory traversal
        clean_filename = os.path.basename(file_name)
        if not clean_filename or clean_filename in (".", ".."):
            clean_filename = f"artifact_{hashlib.md5(content.encode()).hexdigest()[:8]}.txt"

        category_dir = (task_dir / clean_category).resolve()
        if not str(category_dir).startswith(str(task_dir)):
            raise ValueError(f"Unsafe path traversal attempt in category: {clean_category}")

        category_dir.mkdir(parents=True, exist_ok=True)

        full_file_path = (category_dir / clean_filename).resolve()
        if not str(full_file_path).startswith(str(category_dir)):
            raise ValueError(f"Unsafe path traversal attempt in filename: {clean_filename}")

        # Compute content hash
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        # Write content safely
        with open(full_file_path, "w", encoding="utf-8") as f:
            f.write(content)

        relative_path = f"{project_id}/{task_id}/{clean_category}/{clean_filename}"
        logger.info(f"Saved physical artifact: {relative_path} ({len(content)} bytes)")

        return relative_path, clean_category, content_hash
