from packages.config.services.tools_gateway import ToolGatewayServiceSettings

_settings = ToolGatewayServiceSettings()

class ToolGatewaySettingsAdapter():
    def __init__(self, config: ToolGatewayServiceSettings) -> None:
        self._config = config

    @property
    def GRPC_PORT(self)-> str:
        return self._config.GRPC_PORT

    @property
    def REST_PORT(self) -> str:
        return self._config.REST_PORT

    @property
    def DEFAULT_TIMEOUT_SECONDS(self) -> str:
        return self._config.DEFAULT_TIMEOUT_SECONDS

    @property
    def NATS_URL(self) -> str:
        return self._config.NATS_URL

    @property
    def DATABASE_URL(self) -> str:
        return self._config.DATABASE_URL

    @property
    def REDIS_URL(self) -> str:
        return self._config.REDIS_URL
tool_gateway_settings = ToolGatewaySettingsAdapter(_settings)
