from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Header, Static, TabbedContent
from textual.widgets._tabbed_content import TabPane

from openacatex.endpoints.agents import create_planner, create_reviewer
from openacatex.tools.config import load_config, save_config
from openacatex.tui.widgets import ChatTab, ConfigTab, TodoTab


class OpenAcaTeXApp(App):
    CSS = """
    #status-bar {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $text;
        padding: 0 1;
    }
    #status-bar Static {
        padding: 0 1;
    }
    .user-msg {
        color: $accent;
        padding: 0 1;
    }
    .llm-msg {
        color: $text;
        padding: 0 1;
    }
    .todo-item {
        padding: 0 1;
    }
    .todo-item.completed {
        color: $text-disabled;
        text-style: strike;
    }
    .provider-active {
        color: $success;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self._config = load_config()
        self._planner = create_planner(self._config)
        self._reviewer = create_reviewer(self._config)

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(id="tabs"):
            with TabPane("Chat", id="chat"):
                yield ChatTab(id="chat-tab")
            with TabPane("Todo", id="todo"):
                yield TodoTab(id="todo-tab")
            with TabPane("Config", id="config"):
                yield ConfigTab(
                    initial_api_key=self._config.api.openrouter.api_key,
                    initial_model=self._config.api.openrouter.model,
                    id="config-tab",
                )
        with Horizontal(id="status-bar"):
            yield Static(f"Status: Ready | Model: {self._config.api.active_provider}", id="status-text")

    def on_mount(self) -> None:
        self._update_status()

    def _update_status(self) -> None:
        provider = self._config.api.active_provider
        if provider == "openrouter":
            model = self._config.api.openrouter.model
            display = f"Model: OpenRouter: {model}"
        else:
            display = f"Model: {provider}"
        self.query_one("#status-text", Static).update(f"Status: Ready | {display}")

    async def on_chat_tab_message_sent(self, event: ChatTab.MessageSent) -> None:
        chat_tab = self.query_one("#chat-tab", ChatTab)
        chat_tab.add_message("user", event.text)
        result = await self._planner.run(event.text)
        chat_tab.add_message("assistant", result.output)

    async def on_config_tab_open_router_saved(self, event: ConfigTab.OpenRouterSaved) -> None:
        config_tab = self.query_one("#config-tab", ConfigTab)
        api_key, model = config_tab.get_openrouter_values()
        self._config.api.openrouter.api_key = api_key
        self._config.api.openrouter.model = model
        save_config(self._config)
        config_tab.set_status("or", "Saved!")

    async def on_config_tab_open_router_activated(self, event: ConfigTab.OpenRouterActivated) -> None:
        config_tab = self.query_one("#config-tab", ConfigTab)
        api_key, model = config_tab.get_openrouter_values()
        if not api_key:
            config_tab.set_status("or", "Error: No API key")
            return
        self._config.api.openrouter.api_key = api_key
        self._config.api.openrouter.model = model
        self._config.api.active_provider = "openrouter"
        self._planner = create_planner(self._config)
        self._reviewer = create_reviewer(self._config)
        save_config(self._config)
        self._update_status()
        config_tab.set_status("or", "Active", active=True)
        config_tab.set_status("mock", "", active=False)

    async def on_config_tab_mock_activated(self, event: ConfigTab.MockActivated) -> None:
        config_tab = self.query_one("#config-tab", ConfigTab)
        self._config.api.active_provider = "mock"
        self._planner = create_planner(self._config)
        self._reviewer = create_reviewer(self._config)
        save_config(self._config)
        self._update_status()
        config_tab.set_status("mock", "Active", active=True)
        config_tab.set_status("or", "", active=False)
