from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


def create_openrouter_endpoint(api_key: str, model: str = "anthropic/claude-3-haiku") -> Agent:
    model_instance = OpenAIModel(
        model,
        provider=OpenAIProvider(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        ),
    )
    return Agent(model_instance, instructions="You are a helpful AI assistant for academic writing.")
