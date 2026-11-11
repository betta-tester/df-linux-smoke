---
schema: discovery-brief
schema_version: 1
spec_stage: discovery
status: draft
generated_by: discovery-runtime
generated_at: '2026-11-11T07:47:39Z'
validation: pass
interview:
  frame: engineer
  sessions:
  - participant_role: customer
coverage:
  systems: covered
  interfaces: covered
  constraints: covered
  arch_preferences: covered
  risks: covered
  feasibility_review: covered
  gate_passed: true
open_questions: 0
blocking_open_questions: 0
conflicts: 0
traces_to:
- upstream.md
---

# Discovery Brief — betta-tester/df-linux-smoke (engineer-фрейм)

## Constraints

- **CON-01** без сети и записи на диск; без сторонних зависимостей в рантайме; Python 3.12+, uv, pytest

## System Assessment

- **S-01** репо df-linux-smoke без кода; новый Python-пакет smoke в src-раскладке, владелец betta-tester

## Interfaces

- **IF-01** консольная команда smoke (entry point в [project.scripts]); вход argv, выход stdout и код возврата; --version печатает "smoke <версия>"
  traces: [S-01]

## Architecture Preferences

- **AP-01** argparse + importlib.metadata.version("smoke"); тесты pytest через subprocess; без click/typer. Feasibility FR-01 — реализуемо полностью, один модуль и один тест
  traces: [S-01, CON-01]

## Risks

- **RK-01** importlib.metadata.version падает PackageNotFoundError, если пакет не установлен; тесты запускать после uv sync через uv run