# TASK <ID: iter-004>

## Цель
1. Уточнить механику `label` / `key` / `title` для системного слоя (label — для UI, key — индикатор).
2. Ввести наследование типов: `extends` + `excludes` + порядок представления унаследованных полей (по образцу FileClass).
3. Расширить набор допустимых `value_type`.
4. Создать реестр ядра типов плагина по группам «Знания / Контекст / Медиа / Действия» с использованием наследования.
5. Добавить минимальный набор отношений ядра (author, about, part-of, participant, derived-from, supports, blocks, located-in и др.).

## Контекст
- Базовая точка: тег `iter-003` / коммит `0a95600`.
- Решения человека:
  - label для системного слоя; key может выступать индикатором;
  - наследование типов включаем;
  - расширенный value_type подтверждаем;
  - iter-004 = наследование + value_type + ядро типов.
- Референс по наследованию и типам полей: FileClass (linear `extends`, `excludes`, nearest-wins, cycle-guard).
- Уже есть: три слоя, 9 метатипов, key/label для свойств, каноническая ссылка, INV-01…INV-17, DL-014…DL-016.

### Прочитать перед началом
- `docs/CHECKPOINT.md`
- `docs/project-map/PROJECT_MAP.md`
- `docs/metamodel/00-overview.md`
- `docs/metamodel/01-invariants.md`
- `docs/metamodel/02-layers.md`
- `docs/metamodel/03-builtin-types.md`
- `docs/metamodel/04-properties-relations.md`
- `docs/adr/ADR-001-identity-and-typing.md`
- `docs/adr/ADR-002-three-layers.md`
- `docs/adr/ADR-003-properties-links.md`
- `docs/glossary/glossary.md`
- `docs/decisions/decision-log.md`
- `docs/_workflow/RULES.md`
- `docs/_workflow/OPEN_QUESTIONS.md`
- `docs/_workflow/iterations/iter-003/REPORT.md`

### Указания из разбора
- OPEN_QUESTIONS.md обязан обновляться Оркестратором в коммите A (все разобранные вопросы получают статус).
- label/key для системного слоя уточняем в этой итерации.
- Наследование — одиночное, линейное, с `excludes` и явным порядком представления полей.

## Scope

### Создать
1. `docs/adr/ADR-004-type-inheritance.md`  
   Решение о наследовании типов.  
   Обязательные разделы: Контекст, Решение, Альтернативы (≥2, включая «без наследования» и «множественное»), Последствия, Статус=Accepted.  
   Зафиксировать:
   - `extends` (0..1, ссылка на родительский тип);
   - `excludes` (список property_key);
   - правило разрешения полей (корень → лист, nearest wins);
   - запрет циклов;
   - порядок представления унаследованных + собственных полей;
   - влияние на `defined_by` / `type_value`.

2. `docs/metamodel/05-core-types.md`  
   Реестр ядра типов.  
   Группы (обязательны):
   - **Знания**: note, concept, claim, question, source, quote …
   - **Контекст**: person, organization, place, event, project, area …
   - **Медиа**: book, article, video, image, file, link …
   - **Действия**: task, habit, goal, decision, meeting …
   Для каждого типа: `type_value`, `label` (ru), краткое назначение, `extends` (если есть), типичные отношения, пример.  
   Показать 2–3 цепочки наследования (например source → book, event → meeting).

### Изменить
- `docs/metamodel/01-invariants.md`  
  - Новые инварианты (или расширение существующих) по:
    - `extends` / `excludes`;
    - порядку полей;
    - расширенному `value_type`;
    - уточнению `label` vs `title` для определений системного слоя.
- `docs/metamodel/04-properties-relations.md`  
  - Расширить таблицу/список допустимых `value_type` (минимум):
    `string`, `text`, `number`, `boolean`, `date`, `datetime`, `enum`, `list<string>`, `list<enum>`, `link`, `list<link>`, `uuid`  
    (object/json — только если агент считает необходимым и обоснует).
  - Добавить раздел «Отношения ядра» (author, about, part-of, participant, derived-from, supports, blocks, located-in + 2–4 по необходимости).
  - Уточнить механику label/key для системного слоя в соответствии с решением человека.
- `docs/metamodel/03-builtin-types.md` — только точечные правки, если потребуются для согласованности.
- `docs/metamodel/00-overview.md`, `docs/metamodel/02-layers.md` — согласование с наследованием и ядром типов.
- `docs/glossary/glossary.md` — новые термины: type inheritance, extends, excludes, field order, расширенные value_type, названия групп ядра.
- `docs/decisions/decision-log.md` — минимум:
  - DL-017: наследование типов (`extends` + `excludes` + порядок);
  - DL-018: расширенный набор value_type;
  - DL-019: состав ядра типов и отношений (или несколько DL по группам — на усмотрение агента).
- `docs/CHECKPOINT.md`, `docs/project-map/PROJECT_MAP.md`.

### Удалить
нет

**Вне scope:**
- schema/, plugin/, examples/, docs/validation/;
- JSON Schema и правила валидации;
- код плагина;
- множественное наследование;
- детальные пользовательские типы сверх ядра;
- Object/ObjectList как обязательный value_type (только по обоснованной необходимости).

## Definition of Done
- [ ] ADR-004 создан, Accepted, описывает extends/excludes/порядок/циклы.
- [ ] В инвариантах зафиксированы правила наследования и расширенный value_type.
- [ ] `04-properties-relations.md` содержит расширенный value_type и отношения ядра.
- [ ] `05-core-types.md` создан, четыре группы, наследование показано на примерах.
- [ ] label/key для системного слоя уточнены и согласованы.
- [ ] Глоссарий, CHECKPOINT, PROJECT_MAP, decision-log обновлены.
- [ ] REPORT.md сформирован по шаблону.
- [ ] Файлы вне scope не изменены.

## Ограничения и правила
- Соблюдать RULES.md полностью (включая R-005).
- Вопросы — только в REPORT.md.
- Документация на русском; идентификаторы type_value / property_key / relation_key — английский kebab-case.
- Ядро типов держать компактным (ориентир 20–25 типов, не 50).
- Коммит-сообщения предпочтительно на русском.
- Один файл ≈ одна тема; при приближении к 300 строкам — остановиться и вынести вопрос (R-004).

## Формат передачи
- Полный текст всех созданных/изменённых файлов.
- Текст коммита B:  
  `docs(iter-004): наследование типов, расширенный value_type, ядро типов (знания/контекст/медиа/действия)`

## Ожидаемые решения
- DL-017: наследование (extends, excludes, порядок представления, запрет циклов).
- DL-018: канонический список value_type.
- DL-019+: состав ядра типов и отношений ядра.
- Уточнение label vs title для определений системного слоя (если требует отдельного DL).