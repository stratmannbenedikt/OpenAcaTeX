from pydantic_ai import Agent

agent = Agent('test', instructions='Echo back the user message with "Mock received: " prefix.')


def create_mock_endpoint() -> Agent:
    return agent
