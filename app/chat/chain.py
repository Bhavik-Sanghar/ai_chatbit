from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.config.prompts import GENERAL_SYSTEM_PROMPT
from app.models.llm import get_chat_model

from app.chat.memory import get_session_history


def build_chat_chain():
    llm = get_chat_model()

    prompt = ChatPromptTemplate.from_messages([
        ("system", GENERAL_SYSTEM_PROMPT),

        MessagesPlaceholder(
            variable_name="history"
        ),

        ("human", "{question}"),
    ])

    chain = prompt | llm | StrOutputParser()

    chat_chain = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history",
    )

    return chat_chain