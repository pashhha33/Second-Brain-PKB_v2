# TASK <ID: iter-009>

## Цель
1. Начать фазу 2: JSON Schema для обязательных свойств объекта и определений системного слоя (по INV-01…INV-27 и реестрам).
2. Создать первые правила валидации как объекты `type: validation-rule`.
3. Технические хвосты: указатель DL в `09-structural-invariants.md` (R-007); Q-005 и Q-006 → ОТКЛОНЕНО в OPEN_QUESTIONS.

## Контекст
- Базовая точка: тег `iter-008` / `59795ef`.
- Фаза 1 закрыта (метамодель + UX-контракты).
- Реестры подготовлены к переносу: property_key, value_type (14), required/applies_to/cardinality, extends/excludes/field_order, media→image, field-expansion, layer.

### Прочитать перед началом
- `docs/CHECKPOINT.md`
- `docs/PROJECT_BRIEF.md`
- `docs/project-map/PROJECT_MAP.md`
- `docs/metamodel/00-overview.md`
- `docs/metamodel/01-invariants.md`
- `docs/metamodel/09-structural-invariants.md`
- `docs/metamodel/03-builtin-types.md`
- `docs/metamodel/04-properties.md`
- `docs/metamodel/05-core-types.md`
- `docs/metamodel/06-relations.md`
- `docs/metamodel/07-core-properties.md`
- `docs/metamodel/08-field-expansion.md`
- `docs/metamodel/10-plugin-ux-contracts.md`
- `docs/decisions/decision-log.md`
- `docs/_workflow/OPEN_QUESTIONS.md`
- `docs/_workflow/RULES.md`
- `docs/_workflow/iterations/iter-008/REPORT.md`

## Scope

### Создать
1. `docs/adr/ADR-009-phase2-schemas.md` (при необходимости разбора альтернатив формата схем и правил)  
   Границы: что входит в первую волну схем, формат `validation-rule`, связь с инвариантами. Статус=Accepted.

2. Каталог `schema/`  
   Минимум:
   - схема обязательных свойств **любого объекта** (id, type, defined_by, title, aliases, layer, status, owner и согласование с INV);
   - при разумном объёме — схема(ы) определений `type` / `property` / `relation` / `field-expansion` (ключевые служебные поля).  
   Формат: JSON Schema (draft, указать какой — 2020-12 или draft-07; обосновать в ADR или REPORT).

3. `docs/validation/`  
   Первые правила как **описания объектов** `type: validation-rule` (markdown/YAML-описания, не обязательно исполняемый код):
   - уникальность `id`;
   - имя файла = `{{type_prefix}}_{{id}}`;
   - `media` / `list<media>` → цель `type: image`;
   - у `image` обязателен `attachment`;
   - ацикличность `extends`;
   - при возможности: согласованность `defined_by` / `type_value`, базовая проверка trigger_values ⊆ enum_values.  
   Каждое правило: id (или placeholder), название, проверяемый инвариант, краткий алгоритм/условие, severity (error/warning).

### Изменить
- `docs/metamodel/09-structural-invariants.md` — актуальный диапазон DL (R-007).
- `docs/_workflow/OPEN_QUESTIONS.md` — Q-005, Q-006 → ОТКЛОНЕНО (вопросы-подтверждения без возражений).
- `docs/CHECKPOINT.md`, `docs/project-map/PROJECT_MAP.md` — фаза 2 «в работе»; артефакты schema/ и validation/.
- `docs/decisions/decision-log.md` — DL по старту фазы 2, формату схем, составу первой волны правил.
- `docs/glossary/glossary.md` — при появлении новых терминов (JSON Schema mapping, validation rule instance…).
- `docs/metamodel/00-overview.md` / `PROJECT_BRIEF.md` — только если нужно отразить старт фазы 2 (статусы уже частично в Brief).

### Удалить
нет

**Вне scope:**
- код плагина (`plugin/`);
- примеры vault / эталонные заметки (фаза 3);
- полный охват всех INV одной схемой (достаточно ядра + ключевые правила);
- UI, исполняемый валидатор в CI (достаточно документов и schema-файлов);
- изменение состава ядра типов / UX-контрактов.

## Definition of Done
- [ ] В `schema/` есть схема(ы) обязательных свойств объекта (и при наличии — определений).
- [ ] В `docs/validation/` описаны ≥5 первых validation-rule с привязкой к INV.
- [ ] ADR-009 создан, если были альтернативы; иначе обоснование формата в REPORT.
- [ ] 09-structural-invariants: указатель DL обновлён; Q-005/Q-006 ОТКЛОНЕНО.
- [ ] CHECKPOINT, PROJECT_MAP, decision-log согласованы (фаза 2 начата).
- [ ] REPORT.md сформирован.
- [ ] plugin/ и примеры экземпляров не создавались.

## Ограничения и правила
- RULES.md (+ R-006, R-007) полностью.
- Вопросы — только в REPORT.md.
- Документация на русском; идентификаторы схем/ключей — английский.
- Не раздувать первую волну: лучше 2–4 схемы и 5–8 правил, чем «всё сразу».
- Коммит-сообщения предпочтительно на русском.

## Формат передачи
- Полные тексты созданных/изменённых файлов (включая JSON Schema).
- Текст коммита B:  
  `docs(iter-009): фаза 2 — JSON Schema ядра объекта, первые validation-rule`

## Ожидаемые решения
- DL-036+: старт фазы 2, выбранная версия JSON Schema, состав первой волны.
- DL: перечень первых validation-rule и их severity.
- Q-005, Q-006 → ОТКЛОНЕНО.