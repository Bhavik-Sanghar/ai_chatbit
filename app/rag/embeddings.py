# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings


from app.config.settings import EMBEDDING_MODEL


def get_embedding_model():
    return HuggingFaceEmbeddings(
        model=EMBEDDING_MODEL,
    )
