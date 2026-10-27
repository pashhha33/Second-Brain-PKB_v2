# TASK <ID: iter-005>

## Цель
1. Разбить `docs/metamodel/04-properties-relations.md` (306 строк) на логические файлы через ADR.
2. Расширить ядро типов согласно решениям человека:
   - Медиа: `film`, `track`, `image` (обёртка изображения).
   - Группа «Коллекции»: `film-series`, `album`, `gallery` (связь со стороны элемента/обёртки).
   - `chapter` (привязка к `book`); уточнить роли `book` (карточка / +файл / агрегатор глав).
3. Ввести `value_type: media` и визуальные свойства (`cover`, `poster`, `photo`…), которые ссылаются на обёртку `image`.
4. Создать реестр свойств ядра (визуальные + типовые: url, isbn, published, due…).
5. Добавить R-006 (остановка при ~300 строках).

## Контекст
- Базовая точка: тег `iter-004` / `0d59214`.
- Подтверждённые решения человека:
  - film + track в медиа;
  - `image` = обёртка над файлом изображения (метаданные + делает картинку частью базы);
  - группа коллекций (film-series, album, gallery), связь **со стороны** обёртки/элемента;
  - chapter → book; book может быть карточкой, карточкой+файлом или агрегатором глав;
  - визуальные свойства ссылаются на обёртку; нужен value_type `media` (в UI — галерея миниатюр).
- Уже есть: наследование, 12 value_type, 23 типа ядра, 11 отношений ядра, INV-01…INV-22.

### Прочитать перед началом
- `docs/CHECKPOINT.md`
- `docs/project-map/PROJECT_MAP.md`
- `docs/metamodel/00-overview.md`
- `docs/metamodel/01-invariants.md`
- `docs/metamodel/02-layers.md`
- `docs/metamodel/03-builtin-types.md`
- `docs/metamodel/04-properties-relations.md`
- `docs/metamodel/05-core-types.md`
- `docs/adr/ADR-003-properties-links.md`
- `docs/adr/ADR-004-type-inheritance.md`
- `docs/glossary/glossary.md`
- `docs/decisions/decision-log.md`
- `docs/_workflow/RULES.md`
- `docs/_workflow/OPEN_QUESTIONS.md`
- `docs/_workflow/iterations/iter-004/REPORT.md`

### Указания из разбора iter-004
- `excludes` покрывает и `relation_key` — подтверждено.
- `field_order` — подтверждено.
- Abstract-типы не вводим.
- id отношений ядра фиксированы, id типов ядра — нет.
- label встроенных метатипов оставляем английским (+ русский в aliases).
- Разбиение 04-файла — обязательно (R-004).
- Свойства ядра — в этой итерации.

## Scope

### Создать
1. `docs/adr/ADR-005-core-extension-and-split.md`  
   - разбиение `04-properties-relations.md`;  
   - введение `value_type: media`;  
   - модель обёртки `image` и группы коллекций;  
   - направление связей (со стороны элемента/обёртки);  
   - визуальные свойства → обёртка.  
   Статус = Accepted.

2. `docs/metamodel/04-properties.md`  
   Механика key/label, канонический value_type (включая новый `media`), встроенные свойства, служебные ключи, label/key системного слоя.

3. `docs/metamodel/06-relations.md`  
   Форма хранения отношений, отношения классификации, отношения ядра + новые (chapter-of / part-of-collection и т.п.), каноническая ссылка.

4. Обновлённый `docs/metamodel/05-core-types.md`  
   - добавить: film, track, image (обёртка), chapter;  
   - новая группа «Коллекции»: film-series, album, gallery;  
   - уточнить роли book;  
   - показать связи со стороны элемента/обёртки.

5. `docs/metamodel/07-core-properties.md`  
   Реестр свойств ядра с фиксированными id:
   - визуальные: cover, poster, photo, artwork (value_type: media, → image);
   - типовые: url, isbn, published, due, completed, duration, year и необходимые аналоги;
   - для каждого: property_key, label, value_type, required, applies_to.

### Изменить
- Удалить `docs/metamodel/04-properties-relations.md` после полного переноса содержимого.
- Обновить все относительные ссылки (00-overview, 01-invariants, 02-layers, 03-builtin-types, 05-core-types, ADR-003, ADR-004, glossary, CHECKPOINT, PROJECT_MAP).
- `docs/metamodel/01-invariants.md` — при необходимости новые/уточнённые INV для media и обёрток.
- `docs/_workflow/RULES.md` — добавить R-006: «При достижении ~300 строк файл не растёт — агент останавливается и выносит вопрос о разбиении».
- `docs/decisions/decision-log.md` — DL по разбиению, media, обёртке, коллекциям, свойствам ядра.
- `docs/CHECKPOINT.md`, `docs/project-map/PROJECT_MAP.md`, `docs/glossary/glossary.md`.

### Удалить
- `docs/metamodel/04-properties-relations.md` (после переноса).

**Вне scope:**
- schema/, plugin/, examples/, docs/validation/;
- JSON Schema и validation-rule;
- код плагина и UI-галереи (только контракт в документации);
- изменение уже принятых решений по наследованию и базовым value_type (кроме добавления media).

## Definition of Done
- [ ] ADR-005 Accepted.
- [ ] 04-файл разбит на 04-properties.md + 06-relations.md, ссылки обновлены, старый файл удалён.
- [ ] Ядро содержит film, track, image (обёртка), chapter, film-series, album, gallery; роли book уточнены.
- [ ] value_type `media` описан; визуальные свойства ссылаются на image-обёртку.
- [ ] Реестр свойств ядра (07-core-properties.md) создан с фиксированными id.
- [ ] R-006 добавлен в RULES.md.
- [ ] CHECKPOINT, PROJECT_MAP, glossary, decision-log согласованы.
- [ ] REPORT.md сформирован.
- [ ] Файлы вне scope не изменены.

## Ограничения и правила
- Соблюдать RULES.md (+ R-006).
- Вопросы — только в REPORT.md.
- Документация на русском; идентификаторы — английский kebab-case.
- Связи коллекций и chapter — **со стороны элемента/обёртки**.
- Не раздувать свойства ядра (ориентир 10–18).
- Коммит-сообщения предпочтительно на русском.

## Формат передачи
- Полный текст созданных/изменённых файлов.
- Текст коммита B:  
  `docs(iter-005): обёртка image, коллекции, film/track/chapter, value_type media, свойства ядра, разбиение 04`

## Ожидаемые решения
- DL-022+: value_type media + визуальные свойства → image.
- DL по модели обёртки и коллекций.
- DL по составу свойств ядра.
- R-006.