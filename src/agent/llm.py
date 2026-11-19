from langchain_openai.chat_models.base import ChatOpenAI
from pydantic.types import SecretStr

from src.config.settings import settings


def build_model(base_url: str, model_name: str) -> ChatOpenAI:
    return ChatOpenAI(
        base_url=base_url,
        api_key=SecretStr(settings.LLAMA_CPP_API_KEY),
        model=model_name,
        temperature=settings.LLM_TEMPERATURE,
        timeout=settings.LLM_TIMEOUT_SECONDS,
        max_retries=settings.LLM_MAX_RETRIES,
        use_responses_api=settings.LLM_USE_RESPONSES_API,
    )
