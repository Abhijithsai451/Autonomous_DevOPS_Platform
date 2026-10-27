import os
from typing import Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from apps.agent_runtime.config.settings import agent_runtime_settings as settings

load_dotenv()
class LLMClient:
    def __init__(self,model_name: Optional[str] = None,base_url: Optional[str] = None,api_key: Optional[str] = None,
                 temperature: float = 0.2, ):
        self.model_name = settings.LLM_MODEL or model_name
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = ChatOpenAI(model=self.model_name,base_url=self.base_url,api_key=self.api_key,temperature=temperature)

    def execute(self, message: str) -> str:
        response = self.model.invoke([HumanMessage(content= message)])
        return response

    async def aexecute(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Asynchronous chat execution for non-blocking agent runs."""
        messages = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=message))

        response = await self.model.ainvoke(messages)
        return str(response.content)




