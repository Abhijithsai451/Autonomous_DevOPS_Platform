import os
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel


def get_llm_model(
        provider: str = "openai",
        model_name: str = "gpt-5o-mini",
        temperature : float = 0.0,
        ) -> BaseChatModel:
    """
    Factory function providing structured ChatModel instances
    """
    provider = os.getenv("LLM_PROVIDER", provider).lower()
    model_name = os.getenv("MODEL_NAME', model_name")
    key = os.getenv("OPENAI_API_KEY", "mock-key")
    if provider == "openai":
        return ChatOpenAI(
            model = model_name,
            temperature = temperature,
            api_key = key
        )
    else:
        raise ValueError(f"Unsupported LLM Provider: {provider}")

