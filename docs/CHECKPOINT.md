# CHECKPOINT

## Дата
2026-10-27

## Фаза
1 — метамодель (в работе). Фаза 0 (каркас репозитория и workflow) завершена в iter-000.

## Состояние
Создан каркас фазы 1: обзор метамодели, жёсткие инварианты объекта, разделение на слой схемы и слой экземпляров, первичный глоссарий и ADR-001 (идентичность и типизация). Однозначно зафиксировано, как устроен объект, как формируется имя файла заметки и какие свойства обязательны.

## Что готово
- `docs/metamodel/00-overview.md` — границы фазы 1, состав и порядок появления артефактов.
- `docs/metamodel/01-invariants.md` — инварианты INV-01…INV-12: `id` = UUIDv7, уникальность и неизменяемость `id`, `type`, `type_prefix`, имя файла `{{type_prefix}}_{{id}}`, `title`, `aliases[0] = title`, `layer`, `status`, `owner`, самоописание схемы.
- `docs/metamodel/02-layers.md` — schema vs instance, правило самоописания, работа `type` и имени файла на обоих слоях.
- `docs/glossary/glossary.md` — первичный глоссарий (Object, Type, Property, Relation, Taxonomy, Facet, Automation, Validation rule, слои, Status, Owner, id, title, aliases, type_prefix, note filename, UUIDv7, Vault, Built-in metatype).
- `docs/adr/ADR-001-identity-and-typing.md` — статус Accepted; решение R1…R7, альтернативы (ULID vs UUIDv7, варианты `type_prefix`, варианты именования файлов), последствия.
- Решения DL-006…DL-009 в `docs/decisions/decision-log.md`.

## Открытые хвосты фазы 1
- Реестр встроенных метатипов (`type`, `property`, `relation`, `taxonomy`, `facet`, `automation`, `validation-rule`) с фиксированными `id` и `type_prefix` — не создан (планируемый файл `docs/metamodel/03-builtin-types.md`).
- Механизм связи экземпляра с определением типа (INV-12) описан семантически, формальное свойство-указатель не выбрано.
- Полный набор значений `status` (расширение после `draft`/`accepted`) и процедура снятия типа с эксплуатации — не определены.
- DL-009 (правило вычисления `type_prefix`) — статус Proposed, требует подтверждения человека.

## Что дальше
Следующая итерация — `iter-002`: реестр встроенных метатипов и формализация связи «экземпляр → определение» (INV-12), при необходимости — расширение набора `status`. Ставит Оркестратор. После закрытия фазы 1 — фаза 2 (JSON Schema и правила валидации).

## Как восстановить контекст за 3 шага
1. Прочитать этот файл.
2. Прочитать `docs/PROJECT_BRIEF.md` и `docs/project-map/PROJECT_MAP.md`.
3. Прочитать `docs/metamodel/01-invariants.md`, `docs/adr/ADR-001-identity-and-typing.md` и последние 10 записей `docs/decisions/decision-log.md`.

## Открытые вопросы
См. `docs/_workflow/OPEN_QUESTIONS.md`; вопросы итерации iter-001 — в `docs/_workflow/iterations/iter-001/REPORT.md` (раздел «Открытые вопросы к Оркестратору»).
