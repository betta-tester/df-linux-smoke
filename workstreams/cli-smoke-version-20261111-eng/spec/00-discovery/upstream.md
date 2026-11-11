---
schema: discovery-brief
schema_version: 1
spec_stage: discovery
status: approved
approved_by: discovery-runtime
approved_at: '2026-11-11T07:47:05Z'
approver: betta-tester
approved_content_hash: sha256:b8c47591755051c6d370a53cb5d552eb7ca7f2b0251e2791e45d8d2f22034c80
generated_by: discovery-runtime
generated_at: '2026-11-11T07:43:22Z'
validation: pass
interview:
  frame: customer
  sessions:
  - participant_role: customer
coverage:
  goals: covered
  personas: covered
  jobs: covered
  functions: covered
  nfr: covered
  constraints: covered
  success_metrics: covered
  out_of_scope: covered
  risks: missing
  gate_passed: true
open_questions: 0
blocking_open_questions: 0
conflicts: 0
traces_to: []
---

# Discovery Brief — betta-tester/df-linux-smoke (customer-фрейм)

## Goals

- **G-01** при разборе бага версия пакета известна точно, а не угадывается

## Personas

- **P-01** разработчик, разбирающий баг-репорты (primary)
- **P-02** пользователь, который запускает команду и пересылает вывод (secondary)

## Jobs-to-be-done

- **J-01** когда приходит баг-репорт, узнать точную установленную версию одной командой

## Functional Requirements

- **FR-01** команда smoke --version печатает "smoke <версия>" из метаданных установленного пакета и выходит с кодом 0
  traces: [G-01, J-01]
  **Priority**: Must
  **Acceptance**: uv run smoke --version печатает "smoke " и значение importlib.metadata.version("smoke"), код выхода 0

## Non-Functional

- **NFR-01** ответ быстрее 1 секунды; без сети и без записи на диск; только стандартная библиотека Python 3.12+
  **Target**: время ответа < 1 с; 0 сетевых вызовов; 0 записей на диск

## Constraints

- **CON-01** Python 3.12+, uv, pytest, src-раскладка; имя пакета и команды smoke; версия только в pyproject.toml

## Success Metrics

- **M-01** доля баг-репортов с точной версией из smoke --version — с 0% до 100% за 3 месяца
  traces: [G-01]

## Out of Scope

- **OUT-01** проверка обновлений, диагностика окружения, публикация в PyPI, другие команды