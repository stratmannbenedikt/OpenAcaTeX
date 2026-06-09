# OpenAcaTeX

AI-assisted revision engine for scientific LaTeX writing. Terminal-based, deterministic, diff-first workflow.

## Quick Start

```bash
uv sync
uv pip install -e .
acatex
```

## Features

- **Structured Revision Workflow**: Planning → Queue → Patch → Review → State update loop
- **Diff-first**: AI returns patches, never auto-modifies files
- **Token-bounded context**: Each task gets only relevant files + summary + preferences
- **Persistent state**: Resume from any point with `.openacatex/` directory
- **Widget-based TUI**: Tabbed interface for Chat, Todo management, and Configuration

## Architecture

```
Repository Loader → Planning Agent → State Manager → Execution Agent
                                                    ↓
                                              User Review
                                                    ↓
                                         Accept / Reject → Apply / Record
```

## Development

```bash
uv run pytest        # run tests
uv run ruff check    # lint
```

## Requirements

- Python 3.12+