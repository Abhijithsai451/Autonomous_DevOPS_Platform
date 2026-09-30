from abc import ABC, abstractmethod
from typing import Dict, Any
from jsonschema import validate, ValidationError

from apps.tool_gateway.domain.tool_definition import ToolDefinition


class BaseTool(ABC):
    @property
    @abstractmethod
    def definition(self)-> ToolDefinition:
        pass

    def validate_input(self, input_data : Dict[str, Any])-> None:
        if self.validation.input_schema:
            try:
                validate(instance = input_data, schema= self.definition.input_schema)
            except ValidationError as e:
                raise ValueError(f"Invalid input schema for tool '{self.definition.slug}': {e.message}")

    @abstractmethod
    async def run(self, input_data: Dict[str, Any])-> Dict[str, Any]:
        pass



