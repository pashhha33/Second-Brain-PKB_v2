# CHECKPOINT

## Дата
2026-10-27

## Фаза
1 — метамодель (в работе, iter-002 выполнена). Фаза 0 (каркас репозитория и workflow) завершена в iter-000.

## Состояние
Метамодель переведена на три слоя — `system`, `classification`, `content` (ADR-002, DL-010). В слое классификации зафиксированы Domain, Hierarchical category, Facet. Создан реестр восьми встроенных метатипов системного слоя с фиксированными UUIDv7. Связь «объект → его определение» формализована свойствами `defined_by` и `type_value` (DL-013). Набор `status` расширен значением `deprecated` (DL-011).

## Что готово
- `docs/metamodel/00-overview.md` — обновлён: три слоя, границы фазы 1, состав и порядок артефактов.
- `docs/metamodel/01-invariants.md` — инварианты INV-01…INV-14: `id` = UUIDv7, уникальность и неизменяемость `id`, `type`, `type_prefix`, имя файла `{{type_prefix}}_{{id}}`, `title`, `aliases[0] = title`, `layer` ∈ {`system`, `classification`, `content`}, `status` ∈ {`draft`, `accepted`, `deprecated`}, `owner`, `defined_by`, `type_value`, встроенные метатипы.
- `docs/metamodel/02-layers.md` — переписан под три слоя: назначение и состав каждого слоя, Domain / Hierarchical category / Facet с примерами, самоописание системного слоя, связь объекта с определением, жизненный цикл и `deprecated`.
- `docs/metamodel/03-builtin-types.md` — реестр восьми встроенных метатипов: фиксированные `id`, `type`, `type_prefix`, `title`, имена файлов, правило генерации `id`, правила работы с реестром.
- `docs/glossary/glossary.md` — обновлён: термины трёх слоёв, Domain, Hierarchical category, Facet, `deprecated`, `defined_by`, `type_value`; `taxonomy`, `schema layer`, `instance layer` помечены как устаревшие.
- `docs/adr/ADR-002-three-layers.md` — статус Accepted: решение S1…S6, альтернативы (число слоёв, наименования, идентификатор иерархии, способ связи с определением), последствия.
- `docs/adr/ADR-001-identity-and-typing.md` — добавлено примечание iter-002 о соответствии терминов двухслойной модели трёхслойной; статус DL-009 обновлён на Accepted (решения ADR-001 не пересматривались).
- Решения DL-010…DL-013 в `docs/decisions/decision-log.md`; правило R-005 в `docs/_workflow/RULES.md`.
- Удалены `.gitkeep` из `docs/metamodel/`, `docs/glossary/`, `docs/adr/` (разрешено TASK.md iter-002).

## Открытые хвосты фазы 1
- Реестр свойств и отношений (`docs/metamodel/04-properties-relations.md`) не создан: не определены состав свойств (`defined_by`, `type_value`, `layer`, `status`, `owner` как объекты `type: property`) и отношения классификации («родитель — потомок», «объект → домен / категория / значение фасета»).
- Процедура миграции экземпляров при переводе определения типа в `deprecated` не определена.
- Соответствие `layer` и `type` (INV-09) и согласованность `defined_by` / `type_value` (INV-12, INV-13) контролируются вручную до появления правил валидации фазы 2.
- Q-001 в `docs/_workflow/OPEN_QUESTIONS.md` (статусы фаз в `docs/PROJECT_BRIEF.md`) остаётся отложенным: триггер — любое изменение Brief — в iter-002 не сработал, файл не менялся.
- Тег `iter-001` в репозитории не поставлен (коммит B = `52bf7ef` есть); требуется действие человека.

## Что дальше
Следующая итерация — `iter-003`: реестр свойств и отношений (`04-properties-relations.md`) — определения базовых свойств и отношений модели, включая отношения классификации, плюс процедура миграции экземпляров для `deprecated`. Ставит Оркестратор. После закрытия фазы 1 — фаза 2 (JSON Schema и правила валидации по INV-01…INV-14).

## Как восстановить контекст за 3 шага
1. Прочитать этот файл.
2. Прочитать `docs/PROJECT_BRIEF.md` и `docs/project-map/PROJECT_MAP.md`.
3. Прочитать `docs/metamodel/01-invariants.md`, `docs/metamodel/02-layers.md`, `docs/metamodel/03-builtin-types.md`, `docs/adr/ADR-002-three-layers.md` и последние 10 записей `docs/decisions/decision-log.md`.

## Открытые вопросы
См. `docs/_workflow/OPEN_QUESTIONS.md`; вопросы итерации iter-002 — в `docs/_workflow/iterations/iter-002/REPORT.md` (раздел «Открытые вопросы к Оркестратору»).
