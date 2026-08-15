import os
import sys
import shutil
import urllib.request
import urllib.parse
import json
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

def ensure_env_file():
    backend_env = backend_dir / ".env"
    backend_env_example = backend_dir / ".env.example"
    root_env_example = root_dir / ".env.example"

    if not backend_env.exists():
        if backend_env_example.exists():
            print("[INFO] Creating backend/.env from backend/.env.example...")
            shutil.copy(backend_env_example, backend_env)
        elif root_env_example.exists():
            print("[INFO] Creating backend/.env from .env.example...")
            shutil.copy(root_env_example, backend_env)
        else:
            print("[ERROR] Neither backend/.env nor backend/.env.example was found!")
            sys.exit(1)

def load_env():
    ensure_env_file()
    backend_env = backend_dir / ".env"
    if backend_env.exists():
        with open(backend_env, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    v = v.strip('"\'')
                    os.environ.setdefault(k.strip(), v)

def check_postgres():
    print("\n[SETUP] Checking PostgreSQL Database Connection...")
    db_url = os.environ.get("DATABASE_URL", "").strip()
    if not db_url:
        print("[ERROR] DATABASE_URL is missing in backend/.env configuration!")
        print("-> Please specify DATABASE_URL in backend/.env (e.g. postgresql://postgres:postgres@localhost:5432/ai_software_team)")
        sys.exit(1)

    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        # Parse DATABASE_URL using urllib.parse
        parsed = urllib.parse.urlparse(db_url)
        user = parsed.username or "postgres"
        password = parsed.password or ""
        host = parsed.hostname or "localhost"
        port = str(parsed.port or 5432)
        db_name = parsed.path.lstrip("/") or "ai_software_team"

        # 1. Attempt connection directly to target database
        try:
            conn = psycopg2.connect(
                dbname=db_name, user=user, password=password, host=host, port=port, connect_timeout=3
            )
            conn.close()
            print(f"[SUCCESS] Successfully connected to PostgreSQL database '{db_name}' on {host}:{port}.")
            return True
        except psycopg2.OperationalError as op_err:
            err_str = str(op_err)
            # If target database does not exist, attempt to connect to 'postgres' system DB and create target database
            if "does not exist" in err_str:
                print(f"[INFO] Database '{db_name}' does not exist yet. Attempting automatic creation...")
                try:
                    conn = psycopg2.connect(
                        dbname="postgres", user=user, password=password, host=host, port=port, connect_timeout=3
                    )
                    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                    cursor = conn.cursor()
                    cursor.execute(f'CREATE DATABASE "{db_name}";')
                    cursor.close()
                    conn.close()
                    print(f"[SUCCESS] Database '{db_name}' created successfully on PostgreSQL server.")
                    return True
                except Exception as create_err:
                    print(f"[ERROR] Automatic creation of database '{db_name}' failed: {create_err}")
                    print(f"[INFO] Please manually create database '{db_name}' in PostgreSQL.")
                    sys.exit(1)
            else:
                print(f"[ERROR] Could not connect to PostgreSQL server at {host}:{port}.")
                print(f"Error details: {err_str.strip()}")
                print("-> Please verify PostgreSQL is installed and running.")
                print("-> Verify your username, password, host, and port in backend/.env match your local PostgreSQL installation.")
                sys.exit(1)

    except ImportError:
        print("[ERROR] psycopg2 module is not available in Python environment.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Connection check failed: {e}")
        print("-> Please verify PostgreSQL service status and backend/.env credentials.")
        sys.exit(1)

def check_ollama():
    print("\n[SETUP] Checking Ollama AI Service Connection...")
    ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.environ.get("OLLAMA_MODEL", "llama3.1")
    mock_mode = os.environ.get("LLM_MOCK_MODE", "false").lower() in ("true", "1")

    if mock_mode:
        print("[INFO] LLM_MOCK_MODE is enabled in backend/.env. AI agents will execute in mock testing mode.")
        return

    try:
        req = urllib.request.Request(f"{ollama_url}/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "") for m in data.get("models", [])]
                print(f"[SUCCESS] Ollama service is active at {ollama_url}.")

                has_model = any(model_name in m for m in models)
                if has_model:
                    print(f"[SUCCESS] Required LLM model '{model_name}' is installed and ready.")
                else:
                    print(f"[WARNING] Ollama is active, but model '{model_name}' was not found in installed models.")
                    print(f"-> Run command in terminal: ollama run {model_name}")
                    print("-> Or set LLM_MOCK_MODE=true in backend/.env to test without LLM.")
                return
    except Exception:
        print(f"[WARNING] Ollama service is not responding at '{ollama_url}'.")
        print("-> To use real AI models, start Ollama and run: ollama run llama3.1")
        print("-> To test without Ollama, set LLM_MOCK_MODE=true in backend/.env")

if __name__ == "__main__":
    load_env()
    check_postgres()
    check_ollama()
