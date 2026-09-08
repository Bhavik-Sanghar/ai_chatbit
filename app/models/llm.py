from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI

from app.config.settings import (
    GOOGLE_API_KEY,
    MISTRAL_API_KEY,
    PRIMARY_MODEL,
    BACKUP_MODEL,
    TEMPERATURE,
    MAX_RETRIES
)


def get_primary_model():
    return ChatGoogleGenerativeAI(
        model=PRIMARY_MODEL,
        temperature=TEMPERATURE,
        google_api_key=GOOGLE_API_KEY,
        max_retries=MAX_RETRIES
    )


def get_backup_model():
    return ChatMistralAI(
        model=BACKUP_MODEL,
        temperature=TEMPERATURE,
        mistral_api_key=MISTRAL_API_KEY,
        max_retries=MAX_RETRIES
    )


def get_chat_model():
    primary = get_primary_model()
    backup = get_backup_model()

    return primary.with_fallbacks([backup])