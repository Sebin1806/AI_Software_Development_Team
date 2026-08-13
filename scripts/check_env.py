import os
import sys
import urllib.request
import urllib.parse
import json
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

def load_env():
    env_file = backend_dir / ".env"
    if not env_file.exists():
        env_file = Path(__file__).resolve().parent.parent / ".env"
    
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    v = v.strip('"\'')
                    os.environ.setdefault(k.strip(), v)

def check_postgres():
    print("\n[SETUP] Checking PostgreSQL Database Connection...")
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("[ERROR] DATABASE_URL is missing in backend/.env")
        return False

    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        # Parse DATABASE_URL
        # format: postgresql://user:password@host:port/dbname
        clean_url = db_url.replace("postgresql://", "")
        auth_host, db_name = clean_url.split("/", 1)
        if "?" in db_name:
            db_name = db_name.split("?")[0]
        
        user_pass, host_port = auth_host.split("@", 1)
        user, password = user_pass.split(":", 1)
        
        if ":" in host_port:
            host, port = host_port.split(":", 1)
        else:
            host, port = host_port, "5432"

        # Try connecting to target database
        try:
            conn = psycopg2.connect(
                dbname=db_name, user=user, password=password, host=host, port=port, connect_timeout=3
            )
            conn.close()
            print(f"[SUCCESS] Connected to PostgreSQL database '{db_name}'.")
            return True
        except psycopg2.OperationalError:
            # Target database might not exist, attempt to connect to 'postgres' DB and create target database
            print(f"[INFO] Target database '{db_name}' does not exist yet. Attempting to create it...")
            try:
                conn = psycopg2.connect(
                    dbname="postgres", user=user, password=password, host=host, port=port, connect_timeout=3
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor = conn.cursor()
                cursor.execute(f'CREATE DATABASE "{db_name}";')
                cursor.close()
                conn.close()
                print(f"[SUCCESS] Database '{db_name}' created successfully!")
                return True
            except Exception as create_err:
                print(f"[WARNING] Could not automatically create database '{db_name}': {create_err}")
                print(f"[INFO] Please ensure database '{db_name}' is created manually in PostgreSQL.")
                return False

    except ImportError:
        print("[WARNING] psycopg2 module not available in Python environment.")
        return False
    except Exception as e:
        print(f"[WARNING] Could not connect to PostgreSQL: {e}")
        print("[INFO] Please verify PostgreSQL is running and check credentials in backend/.env")
        return False

def check_ollama():
    print("\n[SETUP] Checking Ollama AI Service Connection...")
    ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.environ.get("OLLAMA_MODEL", "llama3.1")
    mock_mode = os.environ.get("LLM_MOCK_MODE", "false").lower() in ("true", "1")

    if mock_mode:
        print("[INFO] LLM_MOCK_MODE is enabled in backend/.env. AI agents will run in test mock mode.")
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
                    print(f"[SUCCESS] Required model '{model_name}' is installed and ready.")
                else:
                    print(f"[WARNING] Ollama is active, but model '{model_name}' was not found.")
                    print(f"-> Run command: ollama run {model_name}")
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
