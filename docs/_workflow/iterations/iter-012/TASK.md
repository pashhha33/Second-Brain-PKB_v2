# TASK <ID: iter-012>

## Цель
1. Начать фазу 3: каталог `examples/` с эталонными заметками для проверки 5 JSON Schema и 14 validation-rule.
2. Покрыть ключевые кейсы: content-объект, system-definition, image+attachment, facet-value, book/person (в т.ч. триггеры), по возможности chapter/коллекция.
3. Обновить PROJECT_BRIEF (счётчики после iter-011) и служебные файлы под старт фазы 3.

## Контекст
- Базовая точка: тег `iter-011` / `8255ed6`.
- Схемы: `object.json`, `system-definitions.json`, `media.json`, `facet-value.json`, `core-property-values.json`.
- Правила: первая + вторая волна (14), кандидаты третьей волны не реализовывать.
- Имена файлов: `{{type_prefix}}_{{id}}`; `title` / `aliases` по INV-07/08; канонические ссылки по INV-15.
- Иллюстративные `id` не смешивать с реестровыми (раздел в `03-builtin-types.md`).

### Прочитать перед началом
- `docs/CHECKPOINT.md`
- `docs/PROJECT_BRIEF.md`
- `docs/project-map/PROJECT_MAP.md`
- `docs/metamodel/00-overview.md`
- `docs/metamodel/01-invariants.md`
- `docs/metamodel/05-core-types.md`
- `docs/metamodel/07-core-properties.md`
- `docs/metamodel/08-field-expansion.md`
- `docs/metamodel/10-plugin-ux-contracts.md`
- `docs/adr/ADR-009-phase2-schemas.md`
- `docs/adr/ADR-010-schema-second-wave.md`
- `schema/*.json`
- `docs/validation/00-validation-rules.md`
- `docs/validation/01-first-wave-rules.md`
- `docs/validation/02-second-wave-rules.md`
- `docs/decisions/decision-log.md`
- `docs/_workflow/iterations/iter-011/REPORT.md`

## Scope

### Создать
1. `examples/README.md`  
   Назначение каталога; как соотнести файл со схемой и правилами; соглашение об id и путях `attachment`; что намеренно не покрыто.

2. Эталонные заметки (ориентир **8–15** `.md`), frontmatter + короткое тело:
   - content: `note` и/или `person`;
   - `book` (желательно с `format` или связью);
   - `image` с `attachment` (путь-заглушка допустим, напр. `attachments/example.png`);
   - `facet-value` (+ при необходимости объект `facet`);
   - 1–2 объекта system-слоя (упрощённое определение `property` / `type` / `field-expansion` — без требования реальных bootstrap-id метатипов, если это блокирует; согласовать с `defined_by` в комментарии README);
   - по возможности: `chapter` + `chapter-of`, или элемент коллекции + `part-of-collection`.

3. В README — таблица: **файл → схема(ы) → релевантные rule_key**.

### Изменить
- `docs/PROJECT_BRIEF.md` — фаза 3 «в работе» / «начата»; счётчики фазы 2 после iter-011 (5 схем, 14 rules, 19 кандидатов — по CHECKPOINT).
- `docs/CHECKPOINT.md`, `docs/project-map/PROJECT_MAP.md`, `docs/metamodel/00-overview.md`.
- `docs/decisions/decision-log.md` — DL о старте фазы 3 и составе первого набора examples.
- `docs/glossary/glossary.md` — Example note / Fixture (при необходимости).

### Удалить
нет

**Вне scope:**
- третья волна validation-rule;
- plugin/, CI, исполняемый валидатор в репозитории;
- negative-examples (заведомо невалидные) — **не** включать, если не запрошены отдельно;
- новые типы/свойства ядра;
- изменение схем, кроме обнаружения явной ошибки (тогда — вопрос в REPORT, не «тихо чинить»).

## Definition of Done
- [ ] `examples/README.md` и ≥8 эталонных заметок.
- [ ] Таблица соответствия файл ↔ схема ↔ rules.
- [ ] Brief / CHECKPOINT / PROJECT_MAP отражают старт фазы 3.
- [ ] decision-log обновлён.
- [ ] REPORT.md сформирован.
- [ ] schema/ и validation rules не менялись без явной ошибки + вопроса.

## Ограничения
- RULES.md (+ R-006, R-007).
- Вопросы — только в REPORT.md.
- Документация и README на русском; type_value / ключи — английский kebab-case.
- Не раздувать: лучше 10 согласованных файлов, чем 30 слабо связанных.
- Коммит на русском.

## Формат передачи
- Полные тексты `examples/**` и изменённых docs.
- Коммит B:  
  `docs(iter-012): фаза 3 — эталонные examples под схемы и validation-rule`

## Ожидаемые решения
- DL-046+: старт фазы 3, состав первого набора fixtures.