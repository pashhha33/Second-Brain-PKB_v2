# TASK <ID: iter-010>

## Цель
1. Вторая волна фазы 2: расширить схемы и правила валидации (межобъектные проверки, служебные ключи validation-rule, предупреждения).
2. Технические хвосты iter-009: R-002 во вступлениях Brief/CHECKPOINT (при необходимости), сводка критерия успеха фазы 1 в 00-overview до iter-008, уточнение HANDOFF/OPEN_QUESTIONS (агент может обновлять реестр по явному пункту TASK; статусы предварительные).
3. Убедиться, что `iter-009.patch` отсутствует в дереве.

## Контекст
- Базовая точка: тег `iter-009` / `594803b` (после удаления patch — актуальный HEAD main).
- Первая волна: 3 схемы (object, system-definitions, media), 8 правил severity:error, ADR-009, DL-036…DL-039.
- Граница: схема = форма одного frontmatter; rule = файл / другие объекты / множества / вычисления.

### Прочитать перед началом
- `docs/CHECKPOINT.md`
- `docs/PROJECT_BRIEF.md`
- `docs/project-map/PROJECT_MAP.md`
- `docs/adr/ADR-009-phase2-schemas.md`
- `docs/validation/00-validation-rules.md`
- `docs/validation/01-first-wave-rules.md`
- `schema/object.json`, `schema/system-definitions.json`, `schema/media.json`
- `docs/metamodel/01-invariants.md`, `09-structural-invariants.md`
- `docs/metamodel/04-properties.md`, `06-relations.md`, `07-core-properties.md`, `08-field-expansion.md`
- `docs/decisions/decision-log.md`
- `docs/_workflow/OPEN_QUESTIONS.md`, `HANDOFF_PROTOCOL.md`, `RULES.md`
- `docs/_workflow/iterations/iter-009/REPORT.md`

## Scope

### Создать
1. `docs/validation/02-second-wave-rules.md`  
   Правила второй волны (описания объектов validation-rule), минимум:
   - существование цели канонической ссылки / media-link;
   - уникальность `property_key` / `relation_key` / `type_value` / `rule_key` в пределах vault;
   - ацикличность `parent`, `part-of`, `blocks` (где применимо);
   - 1–3 warning-правила (например INV-27 «неактивное поле», глубина `extends`, устаревший deprecated в активных ссылках).  
   Каждое: rule_key, checks, severity, applies_to, condition, message, связь с INV.

2. При необходимости — дополнение схем:
   - фрагмент/схема для `validation-rule` (служебные ключи) в `system-definitions.json` или отдельный файл;
   - не обязательны полные enum_values всех свойств ядра.

3. ADR только если появятся спорные альтернативы (иначе обоснование в REPORT + DL).

### Изменить
- `docs/validation/00-validation-rules.md` — реестр служебных ключей validation-rule; ссылка на вторую волну; кандидаты обновлены.
- `schema/system-definitions.json` (или новый schema-файл) — определение validation-rule, если ещё не покрыто.
- `docs/metamodel/00-overview.md` — сводка закрытия фазы 1 доведена до iter-008 (1–2 предложения).
- `docs/PROJECT_BRIEF.md` / `docs/CHECKPOINT.md` — вводные 1–2 предложения после H1, если R-002 нарушен.
- `docs/_workflow/HANDOFF_PROTOCOL.md` — строка: агент может технически обновлять OPEN_QUESTIONS **по явному указанию TASK**; статусы до приёмки Оркестратором предварительные.
- `docs/_workflow/OPEN_QUESTIONS.md` — при необходимости уточнить Q-005/Q-006; без массового пересмотра.
- `docs/CHECKPOINT.md`, `docs/project-map/PROJECT_MAP.md`, `docs/decisions/decision-log.md`, `docs/glossary/glossary.md`.
- Проверка: `iter-009.patch` нет в корне (если появился снова — не коммитить / удалить).

### Удалить
- любой случайно вернувшийся `iter-009.patch` / аналог в корне.

**Вне scope:**
- код плагина, CI-валидатор, examples/;
- полный перенос всех свойств ядра в schema;
- изменение UX-контрактов и состава ядра типов;
- requires_properties / матрица коллекций (можно одним rule-кандидатом в списке «третья волна», без реализации).

## Definition of Done
- [ ] ≥4 новых rule второй волны описаны (в т.ч. link-target exists, unique machine keys, cycle на графовых отношениях).
- [ ] Служебные ключи validation-rule зафиксированы в реестре.
- [ ] Схема/фрагмент validation-rule согласован с реестром (если добавлялся).
- [ ] Хвосты: overview фазы 1, R-002 при необходимости, HANDOFF про OPEN_QUESTIONS.
- [ ] CHECKPOINT / PROJECT_MAP / decision-log обновлены.
- [ ] REPORT.md сформирован; patch-артефактов в коммите нет.

## Ограничения
- RULES.md (+ R-006, R-007).
- Вопросы — только в REPORT.md.
- Не раздувать: лучше 5–10 правил второй волны, чем «все INV».
- Коммит на русском.

## Формат передачи
- Полные тексты новых/изменённых файлов (включая JSON при изменении schema).
- Коммит B:  
  `docs(iter-010): фаза 2 — вторая волна validation-rule, служебные ключи, хвосты iter-009`

## Ожидаемые решения
- DL-040+: состав второй волны, severity warning vs error.
- DL: формат/схема объекта validation-rule (если не закрыто в ADR-009).
- Уточнение HANDOFF по OPEN_QUESTIONS.