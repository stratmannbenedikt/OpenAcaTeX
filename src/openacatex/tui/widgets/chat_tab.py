from textual.containers import Horizontal, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Input, Static


class ChatTab(Horizontal):
    class MessageSent(Message):
        def __init__(self, text: str) -> None:
            self.text = text
            super().__init__()

    def __init__(self, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self._messages: list[tuple[str, str]] = []

    def compose(self):
        with VerticalScroll(id="chat-messages"):
            yield Static("Welcome to OpenAcaTeX Chat", id="chat-welcome")
        yield Horizontal(
            Input(placeholder="Type a message...", id="chat_input"),
            Button("Send", id="chat_send_btn", variant="primary"),
            id="chat-input-area",
        )

    def add_message(self, role: str, content: str) -> None:
        self._messages.append((role, content))
        messages = self.query_one("#chat-messages", VerticalScroll)
        welcome = self.query_one("#chat-welcome", Static)
        if welcome.parent and welcome in list(messages.children):
            welcome.remove()
        classes = "user-msg" if role == "user" else "llm-msg"
        messages.mount(Static(f"{role.title()}: {content}", classes=classes))
        messages.scroll_end(animate=True)

    def clear_messages(self) -> None:
        self._messages.clear()
        messages = self.query_one("#chat-messages", VerticalScroll)
        for widget in list(messages.children):
            widget.remove()
        messages.mount(Static("Welcome to OpenAcaTeX Chat", id="chat-welcome"))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "chat_input":
            text = event.value
            event.input.value = ""
            self.post_message(self.MessageSent(text))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "chat_send_btn":
            input_widget = self.query_one("#chat_input", Input)
            if input_widget.value:
                text = input_widget.value
                input_widget.value = ""
                self.post_message(self.MessageSent(text))
