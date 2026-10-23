from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentRuntimeServiceSettings(BaseSettings):
    AGENT_RUNTIME_DATABASE_URL: str
    NATS_URL: str
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_URL: str
    OPENAI_API_KEY: str
    OLLAMA_BASE_URL: str
    LLM_MODEL: str

    model_config = SettingsConfigDict( extra="ignore")