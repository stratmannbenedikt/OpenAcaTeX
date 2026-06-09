from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Input, Static


class ChatScreen(Screen):
    def compose(self):
        yield VerticalScroll(
            Static("Welcome to OpenAcaTeX Chat", classes="welcome"),
            id="messages",
        )
        yield Input(placeholder="Type a message...", id="chat_input")
        yield Button("Send", id="send_btn", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send_btn":
            self._send_message()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._send_message()

    def _send_message(self):
        from openacatex.endpoints.mock import mock_llm_response

        input_widget = self.query_one("#chat_input", Input)
        messages_mount = self.query_one("#messages", VerticalScroll)
        user_text = input_widget.value.strip()
        if not user_text:
            return
        messages_mount.mount(Static(f"[bold]You:[/bold] {user_text}"))

        response = mock_llm_response(user_text)
        messages_mount.mount(Static(f"[bold]AI:[/bold] {response}"))

        input_widget.value = ""
