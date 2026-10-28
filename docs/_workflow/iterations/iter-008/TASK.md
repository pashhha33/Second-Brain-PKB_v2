# TASK <ID: iter-008>

## Цель
1. Закрыть хвосты iter-007:
   - исключение `media` / `list<media>` из создания по пустой ссылке;
   - обновить статусы фаз в `PROJECT_BRIEF.md` и закрыть Q-001;
   - восстановить полноценный `OPEN_QUESTIONS.md`;
   - ввести R-007 (технические правки указателей DL / перекрёстных ссылок);
   - поправить устаревшие диапазоны DL в `01-invariants.md` и `02-layers.md`.
2. Не начинать фазу 2 (schema/, validation-rule).

## Контекст
- Базовая точка: тег `iter-007` / `5034fd3`.
- Решения Оркестратора по вопросам REPORT iter-007:
  - фильтрация слоёв — как сделано (A);
  - default видимости отдельно от пресетов (A);
  - media: empty-link не применяется (A);
  - status созданного объекта = draft (A);
  - R-007 + точечные правки ссылок (B+A);
  - OPEN_QUESTIONS восстановить (A);
  - PROJECT_BRIEF — обновить фазы, закрыть Q-001 (A).

### Прочитать перед началом
- `docs/CHECKPOINT.md`
- `docs/PROJECT_BRIEF.md`
- `docs/project-map/PROJECT_MAP.md`
- `docs/metamodel/10-plugin-ux-contracts.md`
- `docs/metamodel/06-relations.md`
- `docs/metamodel/01-invariants.md`
- `docs/metamodel/02-layers.md`
- `docs/adr/ADR-008-plugin-ux-contracts.md`
- `docs/_workflow/OPEN_QUESTIONS.md`
- `docs/_workflow/RULES.md`
- `docs/_workflow/iterations/iter-007/REPORT.md`
- `docs/decisions/decision-log.md`

## Scope

### Создать
нет (при необходимости короткий ADR только если появится спорное решение — не ожидается)

### Изменить
1. `docs/metamodel/10-plugin-ux-contracts.md`  
   Явное исключение: для свойств с `value_type` `media` / `list<media>` создание из пустой ссылки **не** применяется; обёртка `image` создаётся через выбор файла (ссылка на `06-relations.md` / INV-24).

2. `docs/PROJECT_BRIEF.md`  
   Таблица статусов фаз: фаза 0 — завершена; фаза 1 — завершена (документы + UX-контракты); фаза 2+ — не начата / по факту. Закрытие Q-001.

3. `docs/_workflow/OPEN_QUESTIONS.md`  
   Восстановить полные записи Q-001…Q-003 (и при необходимости ключевые из REPORT iter-004…007 со статусами). Q-001 → РЕШЕНО после правки Brief.

4. `docs/_workflow/RULES.md`  
   Добавить **R-007**: при добавлении DL агент обновляет указатели диапазонов DL и перекрёстные ссылки в файлах, которые решение затрагивает; такие правки считаются техническими и не требуют отдельного пункта TASK.

5. `docs/metamodel/01-invariants.md`, `docs/metamodel/02-layers.md`  
   Актуальные диапазоны DL (до DL-033); в `02-layers.md` — краткая отсылка на видимость слоёв (`10-plugin-ux-contracts.md` / DL-031), если уместно.

6. `docs/decisions/decision-log.md`  
   DL на исключение media из empty-link (если не покрыто только правкой контракта); при необходимости DL на R-007 / закрытие Q-001.

7. `docs/CHECKPOINT.md`, `docs/project-map/PROJECT_MAP.md`  
   Состояние после чисток; Q-001 закрыт.

### Удалить
нет

**Вне scope:**
- schema/, docs/validation/, JSON Schema;
- код плагина;
- новые типы, свойства, field expansion;
- изменение UX-контрактов кроме пункта про media.

## Definition of Done
- [ ] В `10-plugin-ux-contracts.md` зафиксировано исключение media / list<media>.
- [ ] PROJECT_BRIEF: статусы фаз актуальны; Q-001 закрыт.
- [ ] OPEN_QUESTIONS восстановлен с формулировками и статусами.
- [ ] R-007 добавлен в RULES.md.
- [ ] Указатели DL в 01/02 обновлены.
- [ ] CHECKPOINT и PROJECT_MAP согласованы.
- [ ] REPORT.md сформирован.
- [ ] schema/ и plugin/ не создавались.

## Ограничения
- RULES.md (+ R-006, новое R-007).
- Вопросы — только в REPORT.md.
- Документация на русском.
- Минимальный diff: только хвосты.

## Формат передачи
- Полные тексты изменённых файлов.
- Коммит B:  
  `docs(iter-008): хвосты UX — media/empty-link, Brief фазы, OPEN_QUESTIONS, R-007`

## Ожидаемые решения
- DL (при необходимости): media не участвует в empty-link creation.
- R-007.
- Q-001 → РЕШЕНО.