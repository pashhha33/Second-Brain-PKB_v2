# TASK <ID: iter-014>

## Цель
1. Начать фазу 4: минимальный каркас Obsidian-плагина в `plugin/`.
2. Инфраструктура: manifest, точка входа, чтение markdown + YAML frontmatter, in-memory индекс (`id`, filename, `type`, `layer`, `title`, path).
3. Stubs под UX-контракты: `getDisplayTitle`, видимость слоя (default: content+classification видны, system скрыт).
4. Документы: старт фазы 4 в Brief / CHECKPOINT / PROJECT_MAP; DL.

## Контекст
- Базовая точка: тег `iter-013` / `8b4c603`.
- Контракты: `docs/metamodel/10-plugin-ux-contracts.md` (ADR-008).
- Идентичность: `{{type_prefix}}_{{id}}`, `title` / `aliases[0]`, UUIDv7 (ADR-001).
- `.gitignore` уже содержит `plugin/main.js` — не коммитить артефакт сборки.
- examples/ — источник тестовых заметок для ручной проверки индекса (копирование vault не обязательно в этой итерации).

### Прочитать перед началом
- `docs/CHECKPOINT.md`
- `docs/PROJECT_BRIEF.md`
- `docs/project-map/PROJECT_MAP.md`
- `docs/metamodel/10-plugin-ux-contracts.md`
- `docs/metamodel/01-invariants.md`
- `docs/adr/ADR-001-identity-and-typing.md`
- `docs/adr/ADR-008-plugin-ux-contracts.md`
- `examples/README.md`
- `docs/decisions/decision-log.md`
- `docs/_workflow/iterations/iter-013/REPORT.md`

## Scope

### Создать
1. `plugin/` — каркас:
   - `manifest.json` (id, name, version, minAppVersion, description);
   - `package.json` / `tsconfig.json` (TypeScript, obsidian types);
   - `src/main.ts` (или `main.ts`) — класс Plugin: `onload` / `onunload`;
   - модуль парсинга frontmatter → нормализованный объект (минимум полей INV: id, type, title, aliases, layer, status, owner при наличии);
   - `VaultIndex` (или аналог): map по id и по path; обновление при create/modify/delete (минимально — full scan на load + events);
   - stubs: `getDisplayTitle(file | path) → string` (title из индекса, иначе basename);
   - stubs: `isLayerVisible(layer)` + settings default (content=true, classification=true, system=false);
   - `plugin/README.md` — сборка (`npm i && npm run build`), symlink/copy в `.obsidian/plugins/…`, ограничения v1.

2. При необходимости — пустые `styles.css`, `versions.json` по принятому шаблону Obsidian.

### Изменить
- `docs/PROJECT_BRIEF.md` — фаза 4 «в работе» / «начата».
- `docs/CHECKPOINT.md`, `docs/project-map/PROJECT_MAP.md`, `docs/metamodel/00-overview.md`.
- `docs/decisions/decision-log.md` — DL старта фазы 4, границы каркаса.
- `docs/glossary/glossary.md` — при появлении терминов (Vault index, Display title stub…).

### Удалить
нет

**Вне scope:**
- Полная подмена title в explorer/search/tabs (monkey-patch UI);
- Empty-link creation wizard;
- Runtime-исполнение 19 validation-rule;
- Фильтрация file explorer по layer (достаточно stub API + settings storage);
- Публикация в community plugins;
- Изменение schema/, validation rules, examples (кроме ссылки «проверено на examples» в README plugin).

## Definition of Done
- [ ] `plugin/` собирается командой из README без ошибок TypeScript.
- [ ] На `onload` строится индекс по `.md` с YAML; доступ по id и path.
- [ ] `getDisplayTitle` и default layer visibility соответствуют контракту (зафиксировано в коде/README).
- [ ] Brief / CHECKPOINT / PROJECT_MAP отражают старт фазы 4.
- [ ] `plugin/main.js` не в git (gitignore).
- [ ] REPORT.md сформирован.

## Ограничения
- RULES.md (+ R-006, R-007) для docs.
- Вопросы — только в REPORT.md.
- Документация plugin README — на русском или двуязычно (кратко); код — английские идентификаторы.
- Минимальный diff docs: не переписывать метамодель.
- Коммит-сообщение предпочтительно на русском / conventional с телом на русском.

## Формат передачи
- Полные тексты исходников `plugin/**` (без node_modules, без main.js) и изменённых docs.
- Коммит B:  
  `feat(iter-014): каркас plugin — индекс frontmatter, stubs title/layer`

## Ожидаемые решения
- DL-050+: старт фазы 4, границы каркаса (что stub, что нет).