from abc import ABC, abstractmethod
from typing import Any

from pydantic_ai import Agent, AgentRunResult
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from openacatex.tools.config import AppConfig


class BaseAgent(ABC):
    def __init__(self, model: str | None = None, api_key: str | None = None):
        self._model_name = model
        self._api_key = api_key
        self._agent: Agent | None = None

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        pass

    @property
    def model_id(self) -> str:
        return self._model_name or "test"

    def _create_agent(self) -> Agent:
        if self._model_name and self._api_key:
            model_instance = OpenAIModel(
                self._model_name,
                provider=OpenAIProvider(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self._api_key,
                ),
            )
        else:
            model_instance = self._model_name or "test"
        return Agent(model_instance, instructions=self.system_prompt)

    async def run(self, user_input: str, context: dict[str, Any] | None = None) -> AgentRunResult:
        if self._agent is None:
            self._agent = self._create_agent()

        if context:
            user_input = self._inject_context(user_input, context)

        return await self._agent.run(user_input)

    def _inject_context(self, user_input: str, context: dict[str, Any]) -> str:
        context_str = "\n\n".join(self._format_context(context))
        return f"{context_str}\n\nUser request: {user_input}"

    def _format_context(self, context: dict[str, Any]) -> list[str]:
        lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"## {key.replace('_', ' ').title()}")
                for k, v in value.items():
                    if v:
                        lines.append(f"### {k.replace('_', ' ').title()}")
                        lines.append(str(v))
                lines.append("")
            elif value:
                lines.append(f"## {key.replace('_', ' ').title()}")
                lines.append(str(value))
                lines.append("")
        return lines


class PlannerAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return (
            "You are a planning assistant for academic LaTeX writing. "
            "Your role is to help users plan and organize revisions to their documents. "
            "Work with the user to create clear, actionable tasks. "
            "Each task should be focused and testable. "
            "Ask clarifying questions to ensure tasks are well-defined. "
            "When the user confirms a task list, summarize it clearly."
        )


class ReviewerAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return (
            "You are a review assistant for academic LaTeX writing. "
            "You receive a specific task to perform on a LaTeX document. "
            "You must propose changes by showing the old vs new content as a diff. "
            "Be precise and minimal - only change what the task requires. "
            "After proposing changes, wait for user feedback before proceeding."
        )


def create_planner(config: AppConfig) -> PlannerAgent:
    api_config = config.api
    if api_config.active_provider == "openrouter" and api_config.openrouter.api_key:
        return PlannerAgent(
            model=api_config.openrouter.model,
            api_key=api_config.openrouter.api_key,
        )
    return PlannerAgent()


def create_reviewer(config: AppConfig) -> ReviewerAgent:
    api_config = config.api
    if api_config.active_provider == "openrouter" and api_config.openrouter.api_key:
        return ReviewerAgent(
            model=api_config.openrouter.model,
            api_key=api_config.openrouter.api_key,
        )
    return ReviewerAgent()
