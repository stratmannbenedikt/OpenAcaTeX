import tomllib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass
class Task:
    id: int
    description: str
    status: TaskStatus = TaskStatus.PENDING
    diff: str | None = None
    review_comments: str | None = None


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class LatexDocument:
    path: Path | None = None
    body: str = ""
    commands: str = ""
    bibliography: str = ""

    def is_empty(self) -> bool:
        return not (self.body or self.commands or self.bibliography)

    def update(self, body: str = "", commands: str = "", bibliography: str = "") -> None:
        if body:
            self.body = body
        if commands:
            self.commands = commands
        if bibliography:
            self.bibliography = bibliography


@dataclass
class SessionContext:
    project_path: Path | None = None
    document: LatexDocument = field(default_factory=LatexDocument)
    tasks: list[Task] = field(default_factory=list)
    chat_history: list[ChatMessage] = field(default_factory=list)
    current_task_index: int = 0
    _task_counter: int = 0

    @property
    def current_task(self) -> Task | None:
        if 0 <= self.current_task_index < len(self.tasks):
            return self.tasks[self.current_task_index]
        return None

    @property
    def pending_tasks(self) -> list[Task]:
        return [t for t in self.tasks if t.status == TaskStatus.PENDING]

    @property
    def completed_tasks(self) -> list[Task]:
        return [t for t in self.tasks if t.status in (TaskStatus.ACCEPTED, TaskStatus.REJECTED)]

    def add_task(self, description: str) -> Task:
        self._task_counter += 1
        task = Task(id=self._task_counter, description=description)
        self.tasks.append(task)
        return task

    def advance_to_next_task(self) -> None:
        self.current_task_index += 1

    def reset_chat_history(self) -> None:
        self.chat_history.clear()

    def add_message(self, role: str, content: str) -> None:
        self.chat_history.append(ChatMessage(role=role, content=content))

    def get_reviewer_context(self) -> dict:
        task = self.current_task
        return {
            "document": {
                "body": self.document.body,
                "commands": self.document.commands,
                "bibliography": self.document.bibliography,
            },
            "task": {
                "id": task.id if task else None,
                "description": task.description if task else None,
                "status": task.status.value if task else None,
            },
        }


SESSION_FILE = Path(".openacatex") / "session.toml"


def _serialize_session(ctx: SessionContext) -> str:
    lines = []
    if ctx.project_path:
        lines.append(f"project_path = {repr(str(ctx.project_path))}")

    lines.append("")
    lines.append("[document]")
    lines.append(f"path = {repr(str(ctx.document.path)) if ctx.document.path else ''}")
    lines.append(f"body = {repr(ctx.document.body)}")
    lines.append(f"commands = {repr(ctx.document.commands)}")
    lines.append(f"bibliography = {repr(ctx.document.bibliography)}")

    lines.append("")
    lines.append("[[tasks]]")
    for t in ctx.tasks:
        lines.append(f"id = {t.id}")
        lines.append(f'description = {repr(t.description)}')
        lines.append(f'status = "{t.status.value}"')
        if t.diff:
            lines.append(f'diff = {repr(t.diff)}')
        if t.review_comments:
            lines.append(f'review_comments = {repr(t.review_comments)}')
        lines.append("")

    lines.append("[[chat_history]]")
    for m in ctx.chat_history:
        lines.append(f'role = {repr(m.role)}')
        lines.append(f'content = {repr(m.content)}')
        lines.append("")

    lines.append(f"current_task_index = {ctx.current_task_index}")

    return "\n".join(lines)


def load_session() -> SessionContext:
    if not SESSION_FILE.exists():
        return SessionContext()

    data = tomllib.loads(SESSION_FILE.read_text())
    ctx = SessionContext()

    if "project_path" in data and data["project_path"]:
        ctx.project_path = Path(data["project_path"])

    if "document" in data:
        doc_data = data["document"]
        ctx.document = LatexDocument(
            path=Path(doc_data["path"]) if doc_data.get("path") else None,
            body=doc_data.get("body", ""),
            commands=doc_data.get("commands", ""),
            bibliography=doc_data.get("bibliography", ""),
        )

    if "tasks" in data:
        ctx._task_counter = 0
        ctx.tasks = []
        for t_data in data["tasks"]:
            ctx._task_counter = max(ctx._task_counter, t_data["id"])
            ctx.tasks.append(Task(
                id=t_data["id"],
                description=t_data["description"],
                status=TaskStatus(t_data.get("status", "pending")),
                diff=t_data.get("diff"),
                review_comments=t_data.get("review_comments"),
            ))

    if "chat_history" in data:
        ctx.chat_history = [
            ChatMessage(role=m["role"], content=m["content"])
            for m in data["chat_history"]
        ]

    ctx.current_task_index = data.get("current_task_index", 0)
    return ctx


def save_session(ctx: SessionContext) -> None:
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(_serialize_session(ctx))
