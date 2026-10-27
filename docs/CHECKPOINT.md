# CHECKPOINT

## Дата
2026-10-27

## Фаза
1 — метамодель (в работе, iter-003 выполнена; содержательно фаза 1 закрыта). Фаза 0 завершена в iter-000.

## Состояние
Метамодель описана полностью на уровне документов: три слоя (`system`, `classification`, `content`), девять встроенных метатипов с фиксированными UUIDv7, реестр базовых свойств с парой **key / label**, четыре встроенных отношения классификации, каноническая форма внутренней ссылки `[[{{type_prefix}}_{{id}}|{{title}}]]`, значения фасетов как объекты `facet-value` и процедура поведения при `status: deprecated`. Инварианты — INV-01…INV-17. Далее — фаза 2: перенос инвариантов и реестров в JSON Schema и правила валидации.

## Что готово
- `docs/metamodel/04-properties-relations.md` (создан) — механика key/label, девять встроенных свойств с фиксированными `id`, служебные ключи определений, форма хранения отношений, четыре отношения классификации (`parent`, `category-domain`, `object-category`, `object-facet-value`), каноническая форма ссылки, значения фасетов, процедура `deprecated` по слоям, контракт для плагина (7 требований).
- `docs/adr/ADR-003-properties-links.md` (создан) — статус Accepted: решения P1…P5, альтернативы по key/label (5), форме ссылки (6), представлению значений фасета (4), последствия.
- `docs/metamodel/03-builtin-types.md` — добавлена запись 9 (`facet-value`, фиксированный `id`), таблица русских `aliases[1]` для всех метатипов, обновлено правило генерации `id` (единая последовательность iter-002 + iter-003).
- `docs/metamodel/01-invariants.md` — добавлены INV-15 (каноническая ссылка), INV-16 (`property_key`, `label` = `title`), INV-17 (`relation_key`); INV-04, INV-12, INV-14 приведены в соответствие; обновлён список кандидатов в правила валидации фазы 2.
- `docs/metamodel/02-layers.md` — подраздел Facet value, отношения классификации вместо «планируется», ссылки на реестр свойств; девять метатипов.
- `docs/metamodel/00-overview.md` — границы фазы 1, таблица артефактов (добавлены 04-properties-relations и ADR-003), порядок появления, критерий успеха.
- `docs/glossary/glossary.md` — новые термины: Property key, Label, Relation key, Facet value, Canonical internal link, Value type, Cardinality; пересмотрены Property, Relation, Facet, Built-in metatype, deprecated; снята пометка `черновик` у Property и Relation.
- `docs/decisions/decision-log.md` — DL-009 переведён в Accepted (текстом), добавлены DL-014 (key/label и состав полей определений), DL-015 (каноническая ссылка), DL-016 (`facet-value`).
- `docs/adr/ADR-002-three-layers.md` — примечание iter-003 о девятом метатипе (решение не пересматривалось).
- Удалён мусорный файл `h origin main --tags` (785 строк вывода git с ANSI-кодами, случайно добавленный в коммите B iter-002).

## Открытые хвосты
- Машиночитаемые артефакты отсутствуют: JSON Schema и правила валидации — фаза 2 (`schema/`, `docs/validation/`). Реестры iter-003 подготовлены к переносу: `property_key` → имя поля, `value_type` → тип, `required`/`applies_to`/`cardinality` → ограничения.
- Отношение «объект → домен» не введено: домен объекта выводится из `category-domain` его категорий (осознанное решение, см. `04-properties-relations.md`, раздел 5, правило 3). Если потребуется явное отношение — добавляется как пользовательское.
- `docs/_workflow/OPEN_QUESTIONS.md` не обновлялся Оркестратором с iter-001: в реестре одна запись (Q-001). Вопросы агента из REPORT.md iter-002 (10 штук) статусов не получили; часть из них фактически закрыта указаниями TASK.md iter-003 (DL-009 → Accepted, `.gitkeep`, один файл `04-properties-relations.md`, русские `aliases`), часть остаётся открытой — см. REPORT.md iter-003.
- Пометки `черновик` у терминов Automation и Validation rule сохраняются до появления реестра правил валидации (фаза 2); у Property и Relation сняты в iter-003.
- Q-001 (статусы фаз в `docs/PROJECT_BRIEF.md`) остаётся отложенным: триггер не сработал, файл не менялся.

## Что дальше
Следующая итерация — `iter-004`: начало фазы 2 — JSON Schema для обязательных свойств объекта (по INV-01…INV-17 и реестру `04-properties-relations.md`) и первые правила валидации как объекты `type: validation-rule`. Ставит Оркестратор. Альтернатива — фаза 3 (примеры), если человек хочет сначала увидеть эталонные заметки трёх слоёв.

## Как восстановить контекст за 3 шага
1. Прочитать этот файл.
2. Прочитать `docs/PROJECT_BRIEF.md` и `docs/project-map/PROJECT_MAP.md`.
3. Прочитать `docs/metamodel/01-invariants.md`, `docs/metamodel/04-properties-relations.md`, `docs/metamodel/03-builtin-types.md` и последние 10 записей `docs/decisions/decision-log.md`.

## Открытые вопросы
См. `docs/_workflow/OPEN_QUESTIONS.md`; вопросы итерации iter-003 — в `docs/_workflow/iterations/iter-003/REPORT.md` (раздел «Открытые вопросы к Оркестратору»).
