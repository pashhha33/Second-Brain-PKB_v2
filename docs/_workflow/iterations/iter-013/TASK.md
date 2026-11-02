# TASK <ID: iter-013>

## Цель
1. **B:** расширить `examples/` (медиа/коллекции и недостающие связи).
2. **A:** третья волна validation-rule — приоритетные кандидаты из реестра (в т.ч. цель `facet` → `type: facet`, согласованность коллекций/элементов, 1–2 других error/warning из списка кандидатов).
3. Согласовать новые правила с README examples (какие fixtures их иллюстрируют).

## Контекст
- База: тег `iter-012` / `ec3206e`.
- Сейчас: 5 схем, 14 rules, 19 кандидатов третьей волны; 13 examples.
- Не открывать фазу 4 (plugin/).

### Прочитать перед началом
- `docs/CHECKPOINT.md`, `PROJECT_BRIEF.md`, `project-map/PROJECT_MAP.md`
- `examples/README.md` + существующие `examples/*.md`
- `docs/validation/00-validation-rules.md`, `01-first-wave-rules.md`, `02-second-wave-rules.md`
- `docs/metamodel/05-core-types.md`, `06-relations.md`, `07-core-properties.md`
- `docs/adr/ADR-009-phase2-schemas.md`, `ADR-010-schema-second-wave.md`
- `schema/*.json` (только чтение, правки — лишь при явной ошибке + вопрос в REPORT)
- `docs/decisions/decision-log.md`
- `docs/_workflow/iterations/iter-012/REPORT.md`

## Scope

### Создать
1. `docs/validation/03-third-wave-rules.md`  
   Минимум **4–7** правил, среди них обязательно:
   - цель ключа `facet` у `facet-value` — объект `type: facet` (error; аналог media→image);
   - согласованность element ↔ collection (`film`→`film-series`, `track`→`album`, `image`→`gallery`) для `part-of-collection` (error или warning — обосновать);
   - ещё 2–5 из кандидатов реестра (уникальность/существование целей, deprecated, requires_properties — только если можно описать без новой метамодели).  
   Формат как в 01/02: rule_key, checks, severity, applies_to, condition, message, связь с INV/DL/реестром.

2. Новые эталоны в `examples/` (**+4…8** файлов), приоритет:
   - `track` + `album` **или** `film` + `film-series` (чтобы закрыть матрицу коллекций);
   - недостающие связи author / part-of-collection / object-facet-value, если их ещё нет в наборе;
   - не раздувать system-слой без нужды.

### Изменить
- `docs/validation/00-validation-rules.md` — реестр третьей волны, обновление кандидатов (что взято / что осталось).
- `examples/README.md` — таблицы файл→схема→rules; покрытие новых rules; «вне набора».
- `docs/CHECKPOINT.md`, `PROJECT_MAP.md`, `00-overview.md`, `PROJECT_BRIEF.md` (счётчики rules / examples).
- `docs/decisions/decision-log.md` — DL по составу третьей волны и расширению fixtures.
- `docs/glossary/glossary.md` — при новых терминах.

### Удалить
нет

**Вне scope:**
- plugin/, CI, negative-examples (отдельным решением);
- новые типы/свойства ядра сверх уже принятых;
- перенос enum_values в schema;
- requires_properties как изменение field-expansion (только rule-описание, если без ломки ADR-006);
- правка схем «заодно» без ошибки и вопроса в REPORT.

## Definition of Done
- [ ] `03-third-wave-rules.md` с ≥4 правилами, включая facet→facet и матрицу коллекций.
- [ ] +≥4 example-заметок; все новые канонические ссылки резолвятся внутри `examples/`.
- [ ] README examples обновлён; 00-validation-rules отражает третью волну.
- [ ] CHECKPOINT / PROJECT_MAP / Brief / decision-log согласованы.
- [ ] schema/ не менялись без явной ошибки + вопроса в REPORT.
- [ ] REPORT.md сформирован.

## Ограничения
- RULES.md (+ R-006, R-007).
- Вопросы — только в REPORT.md.
- Не раздувать: лучше 5 чётких rules + 6 examples, чем 15 слабых.
- Коммит на русском.

## Формат передачи
- Полные тексты новых/изменённых файлов.
- Коммит B:  
  `docs(iter-013): третья волна validation-rule и расширение examples (медиа/коллекции)`

## Ожидаемые решения
- DL-048+: состав третьей волны (severity, матрица коллекций).
- DL: расширение набора examples.