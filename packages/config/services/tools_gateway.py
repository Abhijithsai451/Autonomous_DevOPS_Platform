from pydantic_settings import BaseSettings, SettingsConfigDict


class ToolGatewayServiceSettings(BaseSettings):
    NATS_URL: str
    GRPC_PORT: int = 50051
    REST_PORT: int = 8004
    DEFAULT_TIMEOUT_SECONDS: int = 30
    model_config = SettingsConfigDict( extra="ignore")
