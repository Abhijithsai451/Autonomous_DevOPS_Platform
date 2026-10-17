from packages.config.services.agent_runtime import AgentRuntimeServiceSettings

_settings = AgentRuntimeServiceSettings()
class AgentRuntimeSettingsAdapter():
    def __init__(self, config: AgentRuntimeServiceSettings) -> None:
        self._config = config

    @property
    def AGENT_RUNTIME_DATABASE_URL(self) -> str:
        return self._config.AGENT_RUNTIME_DATABASE_URL

    @property
    def NATS_URL(self) -> str:
        return self._config.NATS_URL

    @property
    def REDIS_HOST(self) -> str:
        return self._config.REDIS_HOST

    @property
    def REDIS_PORT(self) -> str:
        return self._config.REDIS_PORT

    @property
    def OPENAI_API_KEY(self):
        return self._config.OPENAI_API_KEY

agent_runtime_settings = AgentRuntimeSettingsAdapter(_settings)