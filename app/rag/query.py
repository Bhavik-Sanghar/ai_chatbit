from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.config.prompts import QUERY_REWRITE_PROMPT
from app.models.llm import get_chat_model


def build_query_rewriter():

    prompt = ChatPromptTemplate.from_template(QUERY_REWRITE_PROMPT)

    llm = get_chat_model()

    return prompt | llm | StrOutputParser()
