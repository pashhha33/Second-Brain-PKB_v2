# TASK <ID: iter-002>

## Цель
1. Зафиксировать трёхслойную модель: системный / классификации / наполнения.
2. В слое классификации явно выделить три сущности: Domain, Hierarchical category, Facet.
3. Создать реестр встроенных метатипов системного слоя (с фиксированными id и type_prefix), включая метатипы, необходимые для поддержки слоя классификации.
4. Формализовать связь «объект → его определение» (INV-12).
5. Добавить статус `deprecated`.
6. Удалить `.gitkeep` из заполненных папок.

## Контекст
- Базовая точка: `52bf7ef`. Тег `iter-001` должен быть поставлен.
- Подтверждены DL-006…DL-009 (DL-009 = Accepted), ASCII kebab-case, vault-wide id, owner = строка.
- Человек уточнил состав слоя классификации:
  1. Домен (Domain)
  2. Иерархические категории (Hierarchical categories)
  3. Фасет (Facet)
- Текущий `02-layers.md` описывает два слоя — его нужно заменить трёхслойной моделью.

### Прочитать перед началом
- `docs/CHECKPOINT.md`
- `docs/project-map/PROJECT_MAP.md`
- `docs/metamodel/00-overview.md`
- `docs/metamodel/01-invariants.md`
- `docs/metamodel/02-layers.md`
- `docs/adr/ADR-001-identity-and-typing.md`
- `docs/glossary/glossary.md`
- `docs/decisions/decision-log.md`
- `docs/_workflow/RULES.md`
- `docs/_workflow/OPEN_QUESTIONS.md`
- `docs/_workflow/iterations/iter-001/REPORT.md`

### Указания из разбора прошлой итерации
- DL-009 подтверждён.
- R-005: CHECKPOINT.md и PROJECT_MAP.md — разрешённые исключения из kebab-case.
- Удалить `.gitkeep` из docs/metamodel/, docs/glossary/, docs/adr/.
- Добавить `deprecated` в status.
- Переход на три слоя + явное выделение Domain / Hierarchical category / Facet — обязателен.

## Scope

### Создать
1. `docs/adr/ADR-002-three-layers.md`  
   Решение о трёх слоях (system / classification / content).  
   Обязательно описать:
   - назначение каждого слоя;
   - какие сущности живут в слое классификации (Domain, Hierarchical category, Facet);
   - как системный слой обеспечивает самоописание;
   - альтернативы (оставить два слоя / другие варианты именования);
   - последствия для инвариантов и будущих реестров.
   Статус = Accepted.

2. `docs/metamodel/03-builtin-types.md`  
   Реестр встроенных метатипов **системного** слоя.  
   Для каждого метатипа: фиксированный `id` (UUIDv7), `type`, `type_prefix`, `title`, краткое назначение, к какому слою относится определяемая им сущность.  
   Минимальный набор (можно расширить с обоснованием):
   - type
   - property
   - relation
   - domain
   - hierarchical-category (или taxonomy — выбрать один идентификатор и зафиксировать)
   - facet
   - automation
   - validation-rule

### Изменить
- `docs/metamodel/02-layers.md` — полностью переписать под три слоя. Явно описать Domain, Hierarchical category, Facet как жителей слоя классификации. Примеры для каждого слоя.
- `docs/metamodel/01-invariants.md` — обновить:
  - INV-09: `layer` ∈ {`system`, `classification`, `content`} (или выбранные идентификаторы);
  - INV-10: добавить `deprecated`;
  - INV-12: формальная связь объекта с его определением.
- `docs/glossary/glossary.md` — термины трёх слоёв + Domain, Hierarchical category, Facet, deprecated.
- `docs/decisions/decision-log.md` — минимум:
  - DL-010: принятие трёхслойной модели + состав слоя классификации (Domain, Hierarchical category, Facet);
  - DL-011: расширение status значением `deprecated`;
  - при необходимости — DL по выбору идентификаторов слоёв и метатипов.
- `docs/CHECKPOINT.md`, `docs/project-map/PROJECT_MAP.md`.
- Удалить `.gitkeep` из трёх папок.

### Удалить
- `docs/metamodel/.gitkeep`
- `docs/glossary/.gitkeep`
- `docs/adr/.gitkeep`

**Вне scope:**
- schema/, plugin/, examples/, docs/validation/;
- детальные пользовательские типы предметной области (Person, Book…);
- JSON Schema и правила валидации;
- изменения workflow-файлов (кроме RULES при новых R).

## Definition of Done
- [ ] ADR-002 принят, трёхслойная модель описана.
- [ ] В `02-layers.md` явно присутствуют Domain, Hierarchical category, Facet в слое классификации.
- [ ] Реестр встроенных метатипов создан, у каждого есть фиксированный id и type_prefix.
- [ ] INV-09, INV-10, INV-12 обновлены.
- [ ] `deprecated` добавлен.
- [ ] `.gitkeep` удалены.
- [ ] Глоссарий, CHECKPOINT, PROJECT_MAP, decision-log обновлены.
- [ ] REPORT.md сформирован.
- [ ] Файлы вне scope не изменены.

## Ограничения и правила
- Соблюдать RULES.md (+ R-005).
- Вопросы — только в REPORT.md.
- Документация на русском; идентификаторы на английском.
- Коммит-сообщения предпочтительно на русском.
- При выборе английских идентификаторов слоёв и метатипов — предложить варианты и зафиксировать один (через DL).

## Формат передачи
- Полный текст всех созданных/изменённых файлов.
- Текст коммита B:  
  `docs(iter-002): трёхслойная модель (system/classification/content), Domain/Category/Facet, реестр метатипов, deprecated`

## Ожидаемые решения
- DL-010: трёхслойная модель + состав classification-слоя.
- DL-011: status += deprecated.
- Выбор точных идентификаторов (`system`/`classification`/`content` или другие) — зафиксировать.
- Фиксированные UUIDv7 для встроенных метатипов — сгенерировать один раз и записать в реестр.