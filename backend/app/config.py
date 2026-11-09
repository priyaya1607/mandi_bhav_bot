import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "CROPORA AI - Mandi Bhav Bot"
    PROJECT_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # PostgreSQL connection string
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg://postgres:postgres@localhost:5432/mandi_bhav_db"
    )
    
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Official Government of India data.gov.in API Key
    DATAGOV_API_KEY: str = os.getenv(
        "DATAGOV_API_KEY", 
        "579b464db66ec23bdd000001653ce763dfe14792751dbd619aeae85f"
    )
    DATAGOV_RESOURCE_ID: str = os.getenv(
        "DATAGOV_RESOURCE_ID", 
        "9ef84268-d588-465a-a308-a864a43d0070"
    )

settings = Settings()
