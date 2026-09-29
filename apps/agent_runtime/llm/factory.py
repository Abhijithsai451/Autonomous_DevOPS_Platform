import os
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm_model(
                provider: str = "gemini",
                model_name: str = "gemini-1.5-flash",
                temperature: float = 0.0,
                ) -> BaseChatModel:
    """
    Factory function providing structured ChatModel instances.
    Defaults to Google Gemini.
    """
    provider = os.getenv("LLM_PROVIDER", provider).lower()
    model_name = os.getenv("LLM_MODEL", model_name)

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is required.")

        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=api_key,
            convert_system_message_to_human=True,
        )

    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required.")

        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

