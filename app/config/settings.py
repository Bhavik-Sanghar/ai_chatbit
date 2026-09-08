from dotenv import load_dotenv
import os

load_dotenv()


# ─────────────────────────────────────────────
# API Keys
# ─────────────────────────────────────────────

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


# ─────────────────────────────────────────────
# Chat Models
# ─────────────────────────────────────────────

PRIMARY_MODEL = "gemini-2.5-flash"
BACKUP_MODEL = "labs-leanstral-1-5"
MAX_RETRIES= 2
TEMPERATURE = 0.0


# ─────────────────────────────────────────────
# RAG Configuration
# ─────────────────────────────────────────────

EMBEDDING_MODEL = "gemini-embedding-001"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

RETRIEVAL_K = 4