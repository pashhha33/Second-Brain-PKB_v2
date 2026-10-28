# TASK <ID: iter-007>

## Цель
1. Зафиксировать UX-контракты плагина в документации метамодели:
   - видимость слоёв (тумблеры + пресеты) в explorer, search, graph, quick switcher;
   - подмена отображаемого имени (`title` вместо имени файла) по образцу Front Matter Title, **встроенная** в наш плагин;
   - создание сущностей из пустых (unresolved) ссылок в теле заметки и в свойствах, с учётом контекста свойства/отношения.
2. Не реализовывать код и не начинать JSON Schema.

## Контекст
- Базовая точка: тег `iter-006` / `c78d8eb`.
- Решения человека: сначала UX-контракты; видимость слоёв = глобальные тумблеры + пресеты; подмена title — на усмотрение Оркестратора → **встраиваем**.
- Уже есть: `title`, каноническая ссылка `[[filename|title]]`, `layer`, реестры типов/свойств/отношений, field expansion.

### Прочитать перед началом
- `docs/CHECKPOINT.md`
- `docs/metamodel/00-overview.md`
- `docs/metamodel/02-layers.md`
- `docs/metamodel/04-properties.md`
- `docs/metamodel/05-core-types.md`
- `docs/metamodel/06-relations.md`
- `docs/metamodel/07-core-properties.md`
- `docs/metamodel/08-field-expansion.md`
- `docs/adr/ADR-003-properties-links.md`
- `docs/glossary/glossary.md`
- `docs/decisions/decision-log.md`
- `docs/_workflow/iterations/iter-006/REPORT.md`

## Scope

### Создать
1. `docs/adr/ADR-008-plugin-ux-contracts.md`  
   Решения:
   - видимость слоёв (A+B);
   - display title встроен в плагин (референс FMT, без обязательной зависимости);
   - empty-link creation (тело / свойство с одним контекстом / несколькими / без контекста).  
   Альтернативы, последствия, Статус=Accepted.

2. `docs/metamodel/10-plugin-ux-contracts.md`  
   Нормативный контракт для будущей реализации:
   - **Слои:** тумблеры system / classification / content; пресеты («Только знания», «Модель», «Всё»); где действует (explorer, search, graph, switcher); default (например content+classification видны, system скрыт — обосновать).
   - **Display title:** где подменять (explorer, search, tabs, header, graph, …); источник = `title`; файл не переименовывать; согласование с канонической ссылкой.
   - **Empty links:**
     - в теле → выбор типа (ядро + пользовательские);
     - в свойстве/отношении с одним допустимым target → создать этот тип без выбора;
     - с несколькими → выбор среди них;
     - без контекста → как в теле;
     - заполнение `title` из текста ссылки, имя файла по правилам метамодели, остальное — defaults / expansion.
   - Явно: это контракт поведения, не спецификация UI-кода.

### Изменить
- `docs/metamodel/00-overview.md` — артефакт 10, граница «контракты плагина».
- `docs/glossary/glossary.md` — Display title, Layer visibility, Empty link creation, Unresolved link…
- `docs/decisions/decision-log.md` — DL по трём блокам контракта.
- `docs/CHECKPOINT.md`, `docs/project-map/PROJECT_MAP.md`.
- При необходимости — короткая отсылка в `06-relations.md` / контракт плагина (без дублирования всего текста).

### Удалить
нет

**Вне scope:**
- schema/, JSON Schema, validation-rule;
- код плагина;
- примеры экземпляров;
- изменение состава ядра типов / field expansion;
- разбиение файлов, кроме случая R-006.

## Definition of Done
- [ ] ADR-008 Accepted.
- [ ] `10-plugin-ux-contracts.md` описывает слои (A+B), display title (встроенно), empty-link creation (все три случая контекста).
- [ ] Defaults видимости слоёв обоснованы.
- [ ] Глоссарий, CHECKPOINT, PROJECT_MAP, decision-log обновлены.
- [ ] REPORT.md сформирован.
- [ ] Код и schema/ не создавались.

## Ограничения
- RULES.md (+ R-006).
- Вопросы — только в REPORT.md.
- Документация на русском.
- Не раздувать: один нормативный файл контрактов + один ADR.

## Формат передачи
- Полные тексты файлов.
- Коммит B:  
  `docs(iter-007): UX-контракты плагина — видимость слоёв, display title, создание из пустых ссылок`

## Ожидаемые решения
- DL-031+: видимость слоёв (тумблеры + пресеты, defaults).
- DL: display title встроен в плагин.
- DL: семантика empty-link creation по контексту свойства/отношения.