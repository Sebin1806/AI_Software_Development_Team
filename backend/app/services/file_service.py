import hashlib
import io
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from uuid import UUID
import zipfile

logger = logging.getLogger(__name__)

BASE_GENERATED_DIR = Path("generated_projects").resolve()


class FileService:
    """
    Physical disk file generation, path safety, and ZIP archiving service.
    Preserves exact nested file directory structure (e.g., frontend/src/App.tsx, backend/app/main.py)
    safely isolated under generated_projects/<project_id>/<task_id>/.
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
    def resolve_category(cls, category: str, file_path: str) -> str:
        cat_lower = category.lower().strip() if category else ""
        if cat_lower in cls.CATEGORY_MAP:
            return cls.CATEGORY_MAP[cat_lower]

        path_lower = file_path.lower()
        if path_lower.startswith("frontend/") or "src/" in path_lower:
            return "frontend"
        if path_lower.startswith("backend/") or "app/" in path_lower:
            return "backend"
        if path_lower.startswith("database/") or "migrations/" in path_lower:
            return "database"
        if path_lower.startswith("tests/") or "test_" in path_lower:
            return "tests"
        if path_lower.startswith("deployment/") or "docker" in path_lower or "k8s" in path_lower:
            return "deployment"

        ext = file_path.split(".")[-1].lower() if "." in file_path else ""
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
        file_path: str,
        content: str
    ) -> Tuple[str, str, str, str]:
        """
        Saves a generated file preserving nested directory paths.
        Returns Tuple[relative_path, clean_filename, clean_category, content_hash].
        """
        clean_category = cls.resolve_category(category, file_path)
        task_dir = cls.get_safe_task_dir(project_id, task_id)

        # Normalize relative path to prevent escaping root task_dir
        clean_rel_path = os.path.normpath(file_path).replace("\\", "/")
        while clean_rel_path.startswith("../") or clean_rel_path.startswith("./"):
            clean_rel_path = clean_rel_path.lstrip("./").lstrip("../")

        if not clean_rel_path:
            clean_rel_path = f"file_{hashlib.md5(content.encode()).hexdigest()[:8]}.txt"

        clean_filename = os.path.basename(clean_rel_path)

        # Build absolute path on disk
        full_file_path = (task_dir / clean_rel_path).resolve()
        if not str(full_file_path).startswith(str(task_dir)):
            raise ValueError(f"Unsafe path traversal attempt blocked for path: {file_path}")

        full_file_path.parent.mkdir(parents=True, exist_ok=True)

        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        with open(full_file_path, "w", encoding="utf-8") as f:
            f.write(content)

        stored_relative_path = f"{project_id}/{task_id}/{clean_rel_path}"
        logger.info(f"Saved nested artifact: {stored_relative_path} ({len(content)} bytes)")

        return clean_rel_path, clean_filename, clean_category, content_hash

    @classmethod
    def create_project_zip(cls, project_id: UUID, task_id: Optional[UUID] = None) -> io.BytesIO:
        """
        Bundles physical files under generated_projects/<project_id>/<task_id>/ into a downloadable ZIP archive.
        """
        proj_dir = (BASE_GENERATED_DIR / str(project_id)).resolve()
        if not str(proj_dir).startswith(str(BASE_GENERATED_DIR)) or not proj_dir.exists():
            raise FileNotFoundError(f"No generated files found for project {project_id}")

        if task_id:
            search_dir = (proj_dir / str(task_id)).resolve()
        else:
            # Pick latest task directory
            subdirs = [d for d in proj_dir.iterdir() if d.is_dir()]
            if not subdirs:
                raise FileNotFoundError(f"No task outputs found for project {project_id}")
            search_dir = sorted(subdirs, key=lambda d: d.stat().st_mtime, reverse=True)[0]

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, _, files in os.walk(search_dir):
                for file in files:
                    abs_file = Path(root) / file
                    rel_arc_path = abs_file.relative_to(search_dir)
                    zip_file.write(abs_file, arcname=str(rel_arc_path))

        zip_buffer.seek(0)
        return zip_buffer
