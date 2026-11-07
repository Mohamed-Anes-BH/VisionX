import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = BASE_DIR / "visionx_marketing.db"

class Settings(BaseModel):
    PROJECT_NAME: str = "VisionX Marketing Automation Agent"
    AGENT_SLUG: str = "agent-marketing-automation-visionx"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
    NOYAU_URL: str = os.getenv("NOYAU_URL", "http://localhost:8000")
    AUDIT_SALT: str = os.getenv("AUDIT_SALT", "VisionX_Audit_Salt_2026")
    
settings = Settings()
