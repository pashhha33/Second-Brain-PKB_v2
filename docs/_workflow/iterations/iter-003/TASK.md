# TASK <ID: iter-003>

## Цель
1. Создать реестр базовых свойств и отношений модели (`docs/metamodel/04-properties-relations.md`).
2. Для каждого свойства явно зафиксировать пару **key** (машинный идентификатор) и **label** (человекочитаемое имя для UI).
3. Описать отношения классификации.
4. Зафиксировать процедуру поведения при `status: deprecated`.
5. Зафиксировать каноническую форму внутренней ссылки: `[[{{type_prefix}}_{{id}}|{{title}}]]`.
6. Мелкие чистки: удалить мусорный файл `h origin main --tags`, удалить `docs/_workflow/iterations/.gitkeep`, перевести DL-009 в Accepted текстом, добавить русские aliases у встроенных метатипов.

## Контекст
- Базовая точка: тег `iter-002` / `0c29116`.
- Новые требования человека (обязательны к отражению):
  1. Плагин нормализует ссылки в форму `[[имя_файла|title]]`.
  2. Свойства имеют key (для редактирования/хранения) и label (для отображения). Референс — представление свойств в exocortex. Если виджет Obsidian не подходит — собственный UI.
- Уже принято: три слоя, 8 метатипов, INV-01…INV-14, DL-010…DL-013.

### Прочитать перед началом
- Все файлы из предыдущего TASK.md iter-003 + 
- `docs/metamodel/03-builtin-types.md` (особенно структуру записи метатипа)
- `docs/adr/ADR-001-identity-and-typing.md`
- `docs/adr/ADR-002-three-layers.md`

### Указания из разбора
- DL-009 → Accepted (поправить текст).
- Русские aliases у метатипов.
- Удалить мусорный файл и `iterations/.gitkeep`.
- Один файл `04-properties-relations.md` (при >300 строк — разбить по R-004).

## Scope

### Создать
1. `docs/metamodel/04-properties-relations.md`  
   Содержание обязательно:
   - Базовые свойства модели как объекты `type: property`.  
     Для каждого: `key`, `label` (или `title` + явное правило, что label = title), тип значения, обязательность, к каким слоям/типам применимо.
     Минимум свойств: id, type, defined_by, type_value, title, aliases, layer, status, owner + key/label-механика.
   - Отношения классификации (parent-child категорий, object→domain, object→hierarchical-category, object→facet-value).
   - Каноническая форма ссылки: `[[{{type_prefix}}_{{id}}|{{title}}]]` — как инвариант или правило.
   - Поведение при `deprecated` определения типа.

2. При необходимости — короткий ADR-003 (если пара key/label или форма ссылки требуют разбора альтернатив).

### Изменить
- `docs/metamodel/03-builtin-types.md` — русские aliases.
- `docs/decisions/decision-log.md` — DL-009 = Accepted; новые DL по key/label и по канонической ссылке.
- `docs/metamodel/01-invariants.md` — при необходимости новый INV по форме ссылки и/или по key/label.
- `docs/glossary/glossary.md`, `docs/CHECKPOINT.md`, `docs/project-map/PROJECT_MAP.md`.
- Точечные правки `00-overview.md` / `02-layers.md` только для согласованности.

### Удалить
- `h origin main --tags`
- `docs/_workflow/iterations/.gitkeep`

**Вне scope:**
- Любой код плагина, schema/, examples/, validation/;
- Детальная реализация UI (только требования к метамодели и контракт для плагина);
- Пользовательские типы предметной области.

## Definition of Done
- [ ] `04-properties-relations.md` создан, содержит key/label, отношения классификации, правило ссылки, deprecated-процедуру.
- [ ] Встроенные метатипы имеют русские aliases.
- [ ] DL-009 в decision-log = Accepted.
- [ ] Мусорный файл и iterations/.gitkeep удалены.
- [ ] Инварианты / глоссарий / CHECKPOINT / PROJECT_MAP согласованы.
- [ ] REPORT.md сформирован.
- [ ] Вне scope ничего не тронуто.

## Ограничения и правила
- RULES.md полностью.
- Вопросы — только в REPORT.md.
- Документация на русском.
- Не реализовывать плагин — только метамодель и контракт.

## Формат передачи
- Полный текст файлов.
- Коммит B:  
  `docs(iter-003): реестр свойств (key/label), классификационные отношения, каноническая ссылка, deprecated, чистки`

## Ожидаемые решения
- DL-014 (или следующий): каждое свойство имеет key + label.
- DL-015: каноническая форма внутренней ссылки `[[filename|title]]`.
- Уточнение семантики deprecated.