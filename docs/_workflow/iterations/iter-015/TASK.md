# TASK <ID: iter-015>

## Цель
1. Реализовать подмену отображаемого имени в UI Obsidian по контракту (минимум **file explorer**; желательно **tabs**), используя `getDisplayTitle` / `VaultIndex`.
2. Feature-flag в настройках: «Подменять имя на title» (по умолчанию **вкл**).
3. Обновить `plugin/README.md` — как проверить в приложении на `examples/`.
4. Не трогать empty-link wizard, layer filter search/graph, runtime validation.

## Контекст
- База: `0d8c883` (после chore) / тег `iter-014` = `7078146`.
- Контракт: `docs/metamodel/10-plugin-ux-contracts.md` (display title), ADR-008, DL-032.
- Уже есть: `plugin/src/display-title.ts`, `vault-index.ts`, settings.

### Прочитать
- `plugin/src/main.ts`, `display-title.ts`, `vault-index.ts`, `settings-tab.ts`, `types.ts`
- `plugin/README.md`, `plugin/manifest.json`
- `docs/metamodel/10-plugin-ux-contracts.md`
- `docs/CHECKPOINT.md`
- `docs/_workflow/iterations/iter-014/REPORT.md`
- `docs/adr/ADR-008-plugin-ux-contracts.md`

## Scope

### Создать / изменить (код)
- Интеграция подмены title в **File explorer** (и по возможности **tabs** / leaf header).
- Устойчивость к переименованию/изменению frontmatter (события индекса уже есть — подписаться/обновить UI).
- Setting: enable/disable display title override.
- Не коммитить `plugin/main.js` / `node_modules`.

### Изменить (docs)
- `plugin/README.md` — шаги проверки в Obsidian.
- `docs/CHECKPOINT.md`, `PROJECT_MAP.md`, `decision-log.md` (DL по UI title).
- При необходимости — короткая отсылка в `10-plugin-ux-contracts.md` «реализовано частично: explorer…».

### Вне scope
- Search / graph / bookmarks full surface (можно stub/TODO).
- Empty-link creation.
- Layer filtering в explorer.
- Исполнение validation-rule.

## Definition of Done
- [ ] `npm run build` в `plugin/` успешен (зафиксировать в REPORT).
- [ ] При включённой опции в file explorer отображается `title`, не `type_prefix_id…`.
- [ ] При выключенной — поведение близко к stock Obsidian (имя файла).
- [ ] main.js не в git.
- [ ] CHECKPOINT / DL / README обновлены.
- [ ] REPORT.md сформирован.

## Ограничения
- RULES.md для docs.
- Вопросы — только в REPORT.md.
- Минимальный monkey-patch; не ломать мобильный API без пометки.
- Коммит:  
  `feat(iter-015): подмена title в explorer (display title UI)`

## Ожидаемые решения
- DL-053+: поверхности UI, вошедшие в v0.x; что отложено.