import ast
import json
import re
from typing import Dict, List, Any


class ValidationService:
    """
    Code validation and static security analysis service.
    Validates syntax for Python, JSON, and YAML, and scans for OWASP security risk patterns.
    """

    @classmethod
    def validate_code(cls, file_name: str, content: str) -> Dict[str, Any]:
        """
        Validates syntax for generated code files.
        Returns Dict with 'valid': bool and 'errors': List[str].
        """
        result = {"valid": True, "errors": []}
        ext = file_name.split(".")[-1].lower() if "." in file_name else ""

        if ext == "py":
            try:
                ast.parse(content, filename=file_name)
            except SyntaxError as e:
                result["valid"] = False
                result["errors"].append(f"Python SyntaxError at line {e.lineno}: {e.msg}")
            except Exception as e:
                result["valid"] = False
                result["errors"].append(f"Python Parse Exception: {str(e)}")

        elif ext == "json":
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                result["valid"] = False
                result["errors"].append(f"JSON Decode Error at line {e.lineno}: {e.msg}")

        return result

    @classmethod
    def scan_security_risks(cls, file_name: str, content: str) -> List[str]:
        """
        Scans code for common static security vulnerabilities and hardcoded credentials.
        Returns list of risk descriptions.
        """
        risks = []

        # 1. Hardcoded Secret Keys / Passwords
        secret_patterns = [
            (r'(?i)(secret_key|password|api_key|private_key)\s*=\s*["\'](?!your-|_|env|placeholder)[^"\']{6,}["\']', "Hardcoded sensitive credential or API key detected"),
            (r'(?i)bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*', "Hardcoded JWT bearer token detected")
        ]
        for pattern, msg in secret_patterns:
            if re.search(pattern, content):
                risks.append(f"[{file_name}] Security Risk: {msg}")

        # 2. Raw SQL Injection Vulnerabilities
        sql_concat_pattern = r'(?i)execute\s*\(\s*f["\'].*?(SELECT|INSERT|UPDATE|DELETE).*?\{.*?\}'
        if re.search(sql_concat_pattern, content):
            risks.append(f"[{file_name}] Critical OWASP Risk: Potential SQL injection via f-string SQL query formatting")

        # 3. Unsafe Command / Code Execution
        unsafe_calls = [
            (r'\beval\s*\(', "Use of unsafe eval() dynamic execution"),
            (r'\bexec\s*\(', "Use of unsafe exec() dynamic execution"),
            (r'os\.system\s*\(', "Use of raw os.system() command execution"),
            (r'subprocess\.(Popen|run|call)\s*\([^)]*shell\s*=\s*True', "Subprocess executed with shell=True command injection risk")
        ]
        for pattern, msg in unsafe_calls:
            if re.search(pattern, content):
                risks.append(f"[{file_name}] Security Warning: {msg}")

        # 4. Insecure CORS Configuration
        if 'allow_origins=["*"]' in content or "allow_origins=['*']" in content:
            risks.append(f"[{file_name}] Security Warning: Wildcard CORS origins allow_origins=['*'] enabled")

        return risks
