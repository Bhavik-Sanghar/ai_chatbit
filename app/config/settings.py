from dotenv import load_dotenv
import os

load_dotenv()


# ─────────────────────────────────────────────
# API Keys
# ─────────────────────────────────────────────

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


# ─────────────────────────────────────────────
# Chat Models
# ─────────────────────────────────────────────

PRIMARY_MODEL = "gemini-3.5-flash-lite"
BACKUP_MODEL = "labs-leanstral-1-5"
MAX_RETRIES = 2
TEMPERATURE = 0.0


# ─────────────────────────────────────────────
# RAG Configuration
# ─────────────────────────────────────────────

# EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

RETRIEVAL_K = 4


# ─────────────────────────────────────────────
# Database / Persistence Configuration
# ─────────────────────────────────────────────

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5433/rag_db",
)

PG_VECTOR_COLLECTION_NAME = "document_embeddings"
PG_CHAT_HISTORY_TABLE_NAME = "chat_history"
