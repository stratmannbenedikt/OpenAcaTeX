from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Input, Static, TabbedContent, TabPane


class ConfigTab(Horizontal):
    class OpenRouterSaved(Message):
        pass

    class OpenRouterActivated(Message):
        pass

    class MockActivated(Message):
        pass

    def __init__(self, initial_api_key: str = "", initial_model: str = "", *, id: str | None = None) -> None:
        super().__init__(id=id)
        self._initial_api_key = initial_api_key
        self._initial_model = initial_model

    def set_initial_values(self, api_key: str, model: str) -> None:
        self._initial_api_key = api_key
        self._initial_model = model

    def compose(self):
        with TabbedContent(id="config-tabs"):
            with TabPane("OpenRouter", id="or-tab"):
                yield Static("API Key:")
                yield Input(placeholder="sk-or-...", id="or-apikey-input", password=True)
                yield Static("Model:")
                yield Input(placeholder="anthropic/claude-3-haiku-20240307", id="or-model-input")
                with Horizontal(id="or-buttons"):
                    yield Button("Save", id="or-save-btn", variant="primary")
                    yield Button("Activate", id="or-activate-btn")
                yield Static("", id="or-status")
            with TabPane("Mock", id="mock-tab"):
                yield Static("(Always available for testing)")
                yield Button("Activate", id="mock-activate-btn")
                yield Static("", id="mock-status")

    def on_mount(self) -> None:
        self.query_one("#or-apikey-input", Input).value = self._initial_api_key
        self.query_one("#or-model-input", Input).value = self._initial_model

    def set_status(self, provider: str, status: str, active: bool = False) -> None:
        status_widget = self.query_one(f"#{provider}-status", Static)
        status_widget.update(status)
        status_widget.classes = "provider-active" if active else ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "or-save-btn":
            self.post_message(self.OpenRouterSaved())
        elif event.button.id == "or-activate-btn":
            self.post_message(self.OpenRouterActivated())
        elif event.button.id == "mock-activate-btn":
            self.post_message(self.MockActivated())

    def get_openrouter_values(self) -> tuple[str, str]:
        apikey = self.query_one("#or-apikey-input", Input).value
        model = self.query_one("#or-model-input", Input).value
        return apikey, model
