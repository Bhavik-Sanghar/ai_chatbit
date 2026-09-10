from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.config.prompts import ROUTER_PROMPT
from app.models.llm import get_chat_model


class RouteDecision(BaseModel):
    route: Literal["general", "document"]


def build_router():

    prompt = ChatPromptTemplate.from_template(ROUTER_PROMPT)

    llm = get_chat_model()

    structured_llm = llm.with_structured_output(RouteDecision)

    return prompt | structured_llm
