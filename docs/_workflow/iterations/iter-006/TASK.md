# TASK <ID: iter-006>

## Цель
1. Ввести в метамодель механизм **триггерных свойств** (field expansion): значение свойства-триггера определяет набор дополнительных полей объекта.
2. Правила развёртывания — отдельные объекты системного слоя (не вшиваются в определение типа).
3. Зафиксировать три канонических примера:
   - `person` + `occupation` (мультивыбор → объединение полей профессий);
   - `book` + `format` (ebook / paper / audiobook → разные поля);
   - `image` + `creation_method` (при `ai-generated` → метаданные генерации).
4. При необходимости разбить `01-invariants.md` (296 строк, R-006) — только если без этого нельзя чисто описать новые инварианты.
5. Обновить реестры, глоссарий, CHECKPOINT.

## Контекст
- Базовая точка: тег `iter-005` / `242eafe`.
- Решения человека:
  - механизм нужен сейчас;
  - первые триггеры: occupation, format, creation_method;
  - правила — объекты системного слоя (вариант B).
- Уже есть: 29 типов ядра, 15 свойств ядра, media, image-обёртка, коллекции, INV-01…INV-24, R-006.

### Прочитать перед началом
- `docs/CHECKPOINT.md`
- `docs/project-map/PROJECT_MAP.md`
- `docs/metamodel/00-overview.md`
- `docs/metamodel/01-invariants.md`
- `docs/metamodel/03-builtin-types.md`
- `docs/metamodel/04-properties.md`
- `docs/metamodel/05-core-types.md`
- `docs/metamodel/06-relations.md`
- `docs/metamodel/07-core-properties.md`
- `docs/adr/ADR-005-core-extension-and-split.md`
- `docs/glossary/glossary.md`
- `docs/decisions/decision-log.md`
- `docs/_workflow/RULES.md`
- `docs/_workflow/OPEN_QUESTIONS.md`
- `docs/_workflow/iterations/iter-005/REPORT.md`

### Указания
- Правила expansion — объекты (новый метатип или `validation-rule` / отдельный тип — обосновать выбор).
- Мультивыбор триггера → union наборов полей.
- Не реализовывать UI и JSON Schema — только метамодель и контракт.

## Scope

### Создать
1. `docs/adr/ADR-006-field-expansion.md`  
   Контекст, Решение, Альтернативы (≥2: в определении типа vs отдельные объекты; один метатип vs validation-rule), Последствия, Статус=Accepted.  
   Зафиксировать:
   - понятие триггерного свойства;
   - объект правила развёртывания (поля: trigger_property, trigger_value(s), adds_properties, mode: union/…);
   - семантика multi-select;
   - поведение при смене/удалении значения триггера (данные не удаляются, поля становятся неактивными / предупреждение — выбрать и обосновать);
   - три канонических примера.

2. `docs/metamodel/08-field-expansion.md`  
   Нормативное описание механизма + три примера (person/occupation, book/format, image/creation_method) с YAML-схемами правил и списком добавляемых свойств.

3. При необходимости — дополнения в `07-core-properties.md` (новые свойства-триггеры и свойства, которые они разворачивают: model, prompt, seed… для AI; narrator, page_count… для format; specialization… для occupation).

### Изменить
- `docs/metamodel/03-builtin-types.md` — если появляется новый метатип (например `field-expansion` или расширение `validation-rule`).
- `docs/metamodel/01-invariants.md` — новые INV по expansion; **если файл превысит ~300 строк — остановиться и разбить через ADR** (R-006).
- `docs/metamodel/04-properties.md` / `05-core-types.md` / `06-relations.md` — точечные правки и ссылки.
- `docs/glossary/glossary.md` — Trigger property, Field expansion, Expansion rule…
- `docs/decisions/decision-log.md` — DL-027+ (механизм, метатип правил, семантика multi-select, поведение при смене триггера).
- `docs/CHECKPOINT.md`, `docs/project-map/PROJECT_MAP.md`.
- `docs/metamodel/03-builtin-types.md` — строка про иллюстративные id в примерах (вопрос 8 iter-005, вариант C).

### Удалить
нет

**Вне scope:**
- JSON Schema, код плагина, UI динамических полей;
- примеры экземпляров (фаза 3);
- новые группы типов;
- разбиение 01-invariants, если новые INV умещаются без превышения лимита (иначе — обязательно через ADR).

## Definition of Done
- [ ] ADR-006 Accepted, механизм описан, альтернативы разобраны.
- [ ] `08-field-expansion.md` создан, три канонических примера на месте.
- [ ] Правила — объекты системного слоя (выбор метатипа обоснован).
- [ ] Семантика multi-select (union) и поведение при смене триггера зафиксированы.
- [ ] При необходимости добавлены свойства-триггеры и разворачиваемые поля в реестр свойств ядра.
- [ ] Инварианты / глоссарий / CHECKPOINT / PROJECT_MAP / decision-log обновлены.
- [ ] Пояснение про иллюстративные id добавлено.
- [ ] REPORT.md сформирован.
- [ ] R-006 соблюдён (при приближении к 300 строкам — разбиение или стоп с вопросом).

## Ограничения и правила
- RULES.md (+ R-006) полностью.
- Вопросы — только в REPORT.md.
- Документация на русском; идентификаторы — английский kebab-case.
- Не раздувать первую версию: только 3 триггера и необходимые им поля.
- Коммит-сообщения предпочтительно на русском.

## Формат передачи
- Полный текст созданных/изменённых файлов.
- Текст коммита B:  
  `docs(iter-006): триггерные свойства (field expansion), occupation/format/creation_method, правила как объекты`

## Ожидаемые решения
- DL-027: введение field expansion, правила = объекты системного слоя.
- DL-028: семантика multi-select = union; поведение при смене триггера.
- DL по выбору метатипа правил (новый `field-expansion` vs расширение `validation-rule`).
- При разбиении 01-invariants — отдельный DL/ADR.