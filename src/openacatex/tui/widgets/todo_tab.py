from dataclasses import dataclass
from enum import Enum

from textual.containers import Horizontal, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Input, Static


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass
class TodoItem:
    id: int
    text: str
    completed: bool = False


class TodoTab(Horizontal):
    class TaskAdded(Message):
        def __init__(self, text: str) -> None:
            self.text = text
            super().__init__()

    class TaskToggled(Message):
        def __init__(self, todo_id: int) -> None:
            self.todo_id = todo_id
            super().__init__()

    class TaskDeleted(Message):
        def __init__(self, todo_id: int) -> None:
            self.todo_id = todo_id
            super().__init__()

    def __init__(self, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self._todos: list[TodoItem] = []
        self._counter: int = 0

    def set_todos(self, todos: list[TodoItem]) -> None:
        self._todos = todos
        self._counter = max((t.id for t in todos), default=0)
        self._render()

    def get_todos(self) -> list[TodoItem]:
        return self._todos.copy()

    def compose(self):
        with VerticalScroll(id="todo-list"):
            yield Static("No tasks yet. Add one below.", id="todo-empty")
        yield Horizontal(
            Input(placeholder="Add a task...", id="todo_input"),
            Button("Add", id="todo_add_btn", variant="primary"),
            id="todo-input-area",
        )

    def _render(self) -> None:
        todo_list = self.query_one("#todo-list", VerticalScroll)
        empty_msg = self.query_one("#todo-empty", Static)

        for widget in list(todo_list.children):
            if widget.id != "todo-empty":
                widget.remove()

        if not self._todos:
            empty_msg.styles.display = "block"
        else:
            empty_msg.styles.display = "none"
            for todo in self._todos:
                item_class = "todo-item completed" if todo.completed else "todo-item"
                container = Horizontal(
                    Static(f"[{'x' if todo.completed else ' '}] {todo.text}", classes=item_class),
                    Button("Toggle", id=f"todo_complete_{todo.id}"),
                    Button("Delete", id=f"todo_delete_{todo.id}"),
                    classes="todo-row",
                )
                todo_list.mount(container)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "todo_input":
            self._add_todo(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "todo_add_btn":
            input_widget = self.query_one("#todo_input", Input)
            if input_widget.value:
                self._add_todo(input_widget.value)
                input_widget.value = ""
        elif event.button.id.startswith("todo_complete_"):
            todo_id = int(event.button.id.split("_")[-1])
            self._toggle_todo(todo_id)
        elif event.button.id.startswith("todo_delete_"):
            todo_id = int(event.button.id.split("_")[-1])
            self._delete_todo(todo_id)

    def _add_todo(self, text: str) -> None:
        self._counter += 1
        todo = TodoItem(id=self._counter, text=text)
        self._todos.append(todo)
        self.post_message(self.TaskAdded(text))
        self._render()

    def _toggle_todo(self, todo_id: int) -> None:
        for todo in self._todos:
            if todo.id == todo_id:
                todo.completed = not todo.completed
                break
        self.post_message(self.TaskToggled(todo_id))
        self._render()

    def _delete_todo(self, todo_id: int) -> None:
        self._todos = [t for t in self._todos if t.id != todo_id]
        self.post_message(self.TaskDeleted(todo_id))
        self._render()
