# OpenAcaTeX

AI-assisted revision engine for scientific LaTeX writing. Terminal-based, deterministic, diff-first workflow.

## Python Version
- Requires Python 3.12+

## Package Manager
- Uses `uv` (lockfile present)

## Install & Run
```bash
uv sync                  # install dependencies
uv pip install -e .      # installs 'acatex' CLI to ~/.local/bin (already on PATH)
acatex                   # run in current LaTeX project directory
```

## Source Layout
```
src/openacatex/
  tui/         # Textual widget-based UI components
  endpoints/   # AI backend adapters (OpenAI, Anthropic, Ollama)
  workflows/   # Core state machine (planning → queue → patch → review → state)
  parsing/     # LaTeX, BibTeX, .sty, glossary parsers
  tools/       # Utilities (git integration, diff, etc.)
```

## Architecture

### State Machine
```
Load Project → Analyze → Generate Revision Plan → Execute One Task → Generate Diff
                                                                              ↓
                                            ┌──────────────┐                   │
                                            │ User Reviews │                   │
                                            └──────┬───────┘                   │
                                             ┌─────┴─────┐                    │
                                        Accept          Reject                 │
                                         │               │                    │
                                         ▼               ▼                    │
                                   Apply Patch    Record Preference            │
                                         │               │                    │
                                         └───────┬───────┘                    │
                                                 ▼                            │
                                            Update State                      │
                                                 │                            │
                                                 └──────────→ Next Task ──────┘
```

### Components
- **Repository Loader** - Parses .tex, .bib, .sty, figures, glossary, macros
- **Planning Agent** - Runs once at start; generates summary + prioritized todo list
- **State Manager** - Persists across sessions
- **Execution Agent** - One task per iteration; returns diff + reasoning + confidence

## State Directory (`.openacatex/`)
```
.openacatex/
  todo.json       # Task queue
  summary.json    # Project summary
  history.db      # Audit trail
  accepted/       # Accepted diffs
  rejected/       # Rejected diffs with reasons
  prompts/        # Cached prompts/responses
  cache/          # Parsed project state
```

## TUI Design
- Widget-based Textual interface with panels, scrollable lists, and keyboard navigation
- Focus management, proper component hierarchy (not raw input() prompts)

## Key Principles
- **Diff-first**: AI returns patches, never auto-modifies
- **Token-bounded context**: Each task gets only relevant files + summary + preferences
- **Restartable**: State persisted; resume from any point
- **Deterministic**: Same project = same review order (planning runs once)

## Dependencies
- `rich>=15.0.0`
- `textual>=8.2.7`