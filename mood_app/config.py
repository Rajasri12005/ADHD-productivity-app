from dotenv import load_dotenv
import os

load_dotenv()

# Example for a local Windows installation
DATABASE_URL = "postgresql://postgres:R4j4sr31276@db.mltzkyptebnbqmaevufi.supabase.co:5432/postgres"
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
