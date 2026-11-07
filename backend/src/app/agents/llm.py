from langchain.chat_models import init_chat_model

from ..core.config import config_value


def get_llm():
    return init_chat_model(
        config_value.LLM
    )
