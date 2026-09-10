from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.chat.memory import get_session_history
from app.config.prompts import RAG_SYSTEM_PROMPT
from app.models.llm import get_chat_model
from app.rag.query import build_query_rewriter
from app.rag.retriever import SessionRetriever


def format_docs(docs):
    return "\n\n".join(
        f"[Source: {doc.metadata['filename']}, "
        f"Page: {doc.metadata['page']}]\n"
        f"{doc.page_content}"
        for doc in docs
    )


def format_history(messages):
    return "\n".join(f"{message.type}: {message.content}" for message in messages)


def build_rag_chain(retriever: SessionRetriever):

    query_rewriter = build_query_rewriter()
    answer_llm = get_chat_model()

    answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", RAG_SYSTEM_PROMPT),
            ("human", "{question}"),
        ]
    )

    def prepare_inputs(inputs):

        history = inputs["history"]

        history_text = format_history(history)

        rewritten_query = query_rewriter.invoke(
            {
                "history": history_text,
                "question": inputs["question"],
            }
        )

        documents = retriever.invoke(
            query=rewritten_query,
            document_ids=inputs["document_ids"],
        )

        return {
            "context": format_docs(documents),
            "question": inputs["question"],
        }

    rag_pipeline = (
        RunnableLambda(prepare_inputs) | answer_prompt | answer_llm | StrOutputParser()
    )

    rag_chain = RunnableWithMessageHistory(
        rag_pipeline,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history",
    )

    return rag_chain
