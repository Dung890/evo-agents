from abc import ABC, abstractmethod
from typing import Dict, Any, List
from src.core.aws.bedrock_service import BedrockService

class BaseAgent(ABC):
    """
    Base Agent class that all specialized agents inherit from.
    Defines common functionality and required interfaces.
    """

    def __init__(self, name: str, description: str):
        """
        Initialize the base agent

        Args:
            name (str): Agent name
            description (str): Description of the agent's purpose
        """
        self.name = name
        self.description = description
        self.bedrock_service = BedrockService()
        self.state: Dict[str, Any] = {}

    @abstractmethod
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request and return a response

        Args:
            request (Dict[str, Any]): The request to process

        Returns:
            Dict[str, Any]: The response from the agent
        """
        pass

    def get_llm_response(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Get a response from the LLM

        Args:
            prompt (str): The prompt to send to the LLM
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Temperature for generation (0.0-1.0)

        Returns:
            str: The LLM response text
        """
        response = self.bedrock_service.invoke_model(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.get("content", "")

    def update_state(self, updates: Dict[str, Any]) -> None:
        """
        Update the agent's state

        Args:
            updates (Dict[str, Any]): Updates to apply to the state
        """
        self.state.update(updates)

    def get_state(self) -> Dict[str, Any]:
        """
        Get the agent's current state

        Returns:
            Dict[str, Any]: The current state
        """
        return self.state

    def reset_state(self) -> None:
        """Reset the agent's state"""
        self.state = {}

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this agent

        Returns:
            List[str]: List of capability descriptions
        """
        pass
