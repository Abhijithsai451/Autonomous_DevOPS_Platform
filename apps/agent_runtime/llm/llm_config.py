from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from openai import api_key

from apps.agent_runtime.config.settings import agent_runtime_settings


class LLMConfig:
    def __init__(self, model_name="gpt-4o-mini",api_key = api_key ):
        self.model_name = model_name
        self.api_key = api_key
        self.model = ChatOpenAI(model_name=model_name, api_key=api_key)

    def execute(self, message: str) -> str:
        response = self.model.invoke([HumanMessage(content= message)])
        return response



llm_model = LLMConfig(model_name = "gpt-4o-mini", api_key=agent_runtime_settings.OPENAI_API_KEY)

