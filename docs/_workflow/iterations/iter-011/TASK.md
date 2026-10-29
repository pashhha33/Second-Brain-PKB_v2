# TASK <ID: iter-011>

## Цель
1. Расширить машиночитаемый слой фазы 2 схемами второй волны: `facet-value`, ключевые формы значений / свойств ядра (не обязательно все 23 свойства целиком).
2. Согласовать схемы с реестрами (`07-core-properties`, facet в metamodel) и границей «схема = один frontmatter».
3. Технически: убедиться, что `iter-*.patch` нет в дереве; при отсутствии в `.gitignore` — добавить `iter-*.patch`.

## Контекст
- Базовая точка: тег `iter-010` / `e194240` (после chore по patch — актуальный main).
- Уже есть: `object.json`, `system-definitions.json`, `media.json`; 8 + 6 validation-rule; ADR-009; DL-036…DL-042.
- Человек выбрал схемы, а не третью волну правил и не examples.

### Прочитать перед началом
- `docs/CHECKPOINT.md`, `PROJECT_BRIEF.md`, `project-map/PROJECT_MAP.md`
- `docs/adr/ADR-009-phase2-schemas.md`
- `schema/object.json`, `schema/system-definitions.json`, `schema/media.json`
- `docs/validation/00-validation-rules.md`, `01-first-wave-rules.md`, `02-second-wave-rules.md`
- `docs/metamodel/04-properties.md`, `07-core-properties.md`, `03-builtin-types.md`
- разделы про facet / facet-value в metamodel и glossary
- `docs/decisions/decision-log.md`
- `docs/_workflow/iterations/iter-010/REPORT.md`

## Scope

### Создать
1. `schema/facet-value.json` (или эквивалентное имя)  
   Форма объекта `type: facet-value`: обязательные поля модели + `facet` (link), согласование с INV и реестром.

2. Схема(ы) для **форм значений / подмножества свойств ядра**, например:
   - `schema/core-property-values.json` с `$defs` для типичных value_type и 5–12 наиболее критичных свойств (url, isbn, published, attachment, cover/poster/photo как media, occupation/format/creation-method как enum-триггеры…);
   - **не** требуется отдельный JSON-файл на каждое из 23 свойств.

3. При необходимости — `docs/adr/ADR-010-schema-second-wave.md`  
   Если есть альтернативы (один файл vs несколько, allOf к object.json, жёсткий additionalProperties). Иначе — обоснование в REPORT + DL.

### Изменить
- `schema/object.json` / `system-definitions.json` / `media.json` — только точечные `$ref` / согласованность, без ломки первой волны.
- `docs/validation/00-validation-rules.md` — ссылки на новые схемы; кандидаты третьей волны правил не реализовывать, можно кратко перечислить.
- `docs/CHECKPOINT.md`, `PROJECT_MAP.md`, `00-overview.md`, `decision-log.md`, `glossary.md`.
- `.gitignore` — `iter-*.patch` (если ещё нет).
- Не коммитить `iter-010.patch` / аналоги.

### Удалить
- любой `iter-*.patch` в корне, если снова появился.

**Вне scope:**
- третья волна validation-rule (отдельная итерация);
- examples/, plugin/, CI;
- requires_properties / матрица коллекций как правила;
- полный enum_values всех свойств ядра в schema;
- изменение UX-контрактов и состава ядра типов.

## Definition of Done
- [ ] Схема facet-value создана и согласована с моделью.
- [ ] Есть схема/defs для ключевых value forms / core properties (обоснованный минимум, не «все 23»).
- [ ] Первая волна схем не сломана; $id/$ref согласованы.
- [ ] CHECKPOINT / PROJECT_MAP / decision-log обновлены.
- [ ] patch-артефакты не в коммите; gitignore при необходимости.
- [ ] REPORT.md сформирован.

## Ограничения
- RULES.md (+ R-006, R-007).
- Вопросы — только в REPORT.md.
- JSON Schema 2020-12 (как в ADR-009), если нет сильной причины сменить.
- Коммит на русском.

## Формат передачи
- Полные тексты schema + изменённых docs.
- Коммит B:  
  `docs(iter-011): фаза 2 — схемы facet-value и форм значений свойств ядра`

## Ожидаемые решения
- DL-043+: состав схем второй волны (что вошло / что отложено).
- При ADR-010 — Accepted с альтернативами.