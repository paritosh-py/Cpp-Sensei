import os

def load_env():
    """
    Manually parses the .env file to load variables into os.environ.
    This maintains a zero-dependency architecture, preventing packaging and loading
    issues in Electron production environments.
    """
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    # Clean whitespaces and strip string quotes
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val
        except Exception as e:
            print(f"[Config] Error reading .env file: {e}")

# Load environment configurations
load_env()

# Centralized Configurations
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
# Use gemini-2.5-flash by default: optimized for coding, fast, token-efficient, and free-tier friendly
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash").strip()

# AI Parameter limits and behaviors
AI_TEMPERATURE = float(os.environ.get("AI_TEMPERATURE", "0.4"))
AI_MAX_OUTPUT_TOKENS = int(os.environ.get("AI_MAX_OUTPUT_TOKENS", "1024"))

# Host/Port Settings (for local/Electron execution)
BACKEND_HOST = os.environ.get("BACKEND_HOST", "127.0.0.1").strip()
BACKEND_PORT = int(os.environ.get("BACKEND_PORT", "8000"))

# Log configuration load status securely
if GEMINI_API_KEY:
    # Do not print the API key for security reasons
    print(f"[Config] Backend initialized with {GEMINI_MODEL}. API Key configured.")
else:
    print("[Config] WARNING: GEMINI_API_KEY is not set. AI services will be unavailable until a key is configured in a .env file.")
