/**
 * plugin_harness.cjs — головная проверка чистых модулей каркаса плагина (фаза 4, iter-014).
 *
 * Вне репозитория: каталог `tools/` в `.gitignore`, в коммит B не входит.
 * Вход: `tools/build/*.js` — модули `plugin/src/` без импорта `obsidian`, собранные
 * `npx tsc -p tools/tsconfig.harness.json`; данные — `examples/*.md` (19 эталонных заметок).
 * Проверяются: индекс по id и пути, производные идентичности (INV-01, INV-05, INV-06, INV-08,
 * INV-09), отображаемое имя (§3 контракта), видимость слоёв (§2), подмножество YAML,
 * инкрементальное обновление и нарушение уникальности `id`.
 */

"use strict";

const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const BUILD = path.join(__dirname, "build");
const EXAMPLES = path.join(ROOT, "examples");

const { indexFiles, VaultIndex } = require(path.join(BUILD, "vault-index.js"));
const { normalizeEntry } = require(path.join(BUILD, "frontmatter.js"));
const { parseYamlSubset, splitFrontmatter } = require(path.join(BUILD, "yaml.js"));
const { getDisplayTitle, getTitleIndicator, hasTitleError, collisionIndicators } = require(
	path.join(BUILD, "display-title.js"),
);
const {
	applyPreset,
	CANONICAL_PRESETS,
	DEFAULT_LAYER_VISIBILITY,
	DEFAULT_SETTINGS,
	isEntryVisible,
	isLayerVisible,
	matchingPreset,
	normalizeSettings,
	resetToDefault,
	setLayerVisible,
} = require(path.join(BUILD, "layer-visibility.js"));
const { expectedBasename, isUuidV7, layerOfType, parseCanonicalLink, typePrefix } = require(
	path.join(BUILD, "identity.js"),
);

let passed = 0;
const failures = [];
const notes = [];

function check(condition, message) {
	if (condition) {
		passed++;
	} else {
		failures.push(message);
	}
	return Boolean(condition);
}

function note(message) {
	notes.push(message);
}

function section(title) {
	console.log(`=== ${title} ===`);
}

function readExamples() {
	const names = fs.readdirSync(EXAMPLES).filter((name) => name.endsWith(".md"));
	const notesFiles = names.filter((name) => name !== "README.md");
	return {
		all: names.map((name) => ({ path: `examples/${name}`, text: fs.readFileSync(path.join(EXAMPLES, name), "utf8") })),
		objects: notesFiles.map((name) => ({
			path: `examples/${name}`,
			text: fs.readFileSync(path.join(EXAMPLES, name), "utf8"),
		})),
		plain: names.filter((name) => name === "README.md").map((name) => `examples/${name}`),
	};
}

// ------------------------------------------------------------------ A. индекс на examples/
section("A. Индекс по 19 эталонным заметкам examples/");
const data = readExamples();
const index = indexFiles(data.objects);
const entries = index.entries();
const stats = index.stats();

check(entries.length === 19, `A1: в индексе 19 записей (найдено ${entries.length})`);
check(
	entries.every((entry) => entry.kind === "object"),
	`A2: все записи — объекты модели (${entries.filter((e) => e.kind !== "object").map((e) => e.path).join(", ")})`,
);
check(stats.objects === 19, `A3: stats.objects = 19 (получено ${stats.objects})`);
check(
	stats.byLayer.system === 3 && stats.byLayer.classification === 2 && stats.byLayer.content === 14,
	`A4: слои 3/2/14 (получено ${stats.byLayer.system}/${stats.byLayer.classification}/${stats.byLayer.content})`,
);
check(stats.partial === 0 && stats.plain === 0, `A5: partial и plain отсутствуют (${stats.partial}/${stats.plain})`);
check(stats.duplicateIds.length === 0, `A6: повторов id нет (${stats.duplicateIds.join(", ")})`);

let byIdOk = true;
let byPathOk = true;
let filenameOk = true;
let prefixOk = true;
let aliasesOk = true;
let layerOk = true;
let uuidOk = true;
for (const entry of entries) {
	if (index.getById(entry.id) !== entry) byIdOk = false;
	if (index.getByPath(entry.path) !== entry) byPathOk = false;
	if (expectedBasename(entry.type, entry.id) !== entry.basename) filenameOk = false;
	if (entry.basename.split("_")[0] !== entry.typePrefix) prefixOk = false;
	if (!entry.aliases || entry.aliases[0] !== entry.title) aliasesOk = false;
	if (entry.expectedLayer !== entry.layer) layerOk = false;
	if (!isUuidV7(entry.id)) uuidOk = false;
}
check(byIdOk, "A7: доступ по id возвращает ту же запись");
check(byPathOk, "A8: доступ по пути возвращает ту же запись");
check(filenameOk, "A9: INV-06 — имя файла = {{type_prefix}}_{{id}}");
check(prefixOk, "A10: INV-05 — префикс в имени файла совпадает с производным от type");
check(aliasesOk, "A11: INV-08 — aliases[0] = title");
check(layerOk, "A12: INV-09 — layer согласован с type");
check(uuidOk, "A13: INV-01 — все id в форме UUIDv7");

const typeExample = entries.find((entry) => entry.type === "type");
const propertyExample = entries.find((entry) => entry.type === "property");
const expansionExample = entries.find((entry) => entry.type === "field-expansion");
check(typeExample && typeExample.machineKey === "note", `A14: machineKey определения типа (${typeExample && typeExample.machineKey})`);
check(
	propertyExample && propertyExample.machineKey === "cover",
	`A15: machineKey определения свойства (${propertyExample && propertyExample.machineKey})`,
);
check(expansionExample && expansionExample.layer === "system", "A16: field-expansion — системный слой (INV-14)");
check(
	entries.every((entry) => entry.status && entry.owner && entry.definedBy),
	"A17: status, owner и defined_by присутствуют у всех объектов",
);

// ------------------------------------------------------------------ B. отображаемое имя
section("B. Отображаемое имя (§3 контракта)");
let titleOk = true;
let differsOk = true;
for (const entry of entries) {
	if (getDisplayTitle(index, entry.path) !== entry.title) titleOk = false;
	if (getDisplayTitle(index, entry.path) === entry.basename) differsOk = false;
}
check(titleOk, "B1: getDisplayTitle возвращает title для всех 19 объектов");
check(differsOk, "B2: отображаемое имя не совпадает с именем файла");

const plainEntry = normalizeEntry("examples/README.md", fs.readFileSync(path.join(EXAMPLES, "README.md"), "utf8"));
check(plainEntry.kind === "plain" && plainEntry.frontmatter === false, `B3: README.md — plain (${plainEntry.kind})`);
const plainIndex = indexFiles([{ path: "examples/README.md", text: fs.readFileSync(path.join(EXAMPLES, "README.md"), "utf8") }]);
check(getDisplayTitle(plainIndex, "examples/README.md") === "README", "B4: файл вне модели отображается именем файла");

const noTitle = [
	"---",
	"id: 01a17d3b-9f01-7a11-8e01-1f2e3d4c5b6a",
	"type: note",
	"defined_by: 01a17d3b-6a0f-7b2c-8d4e-1a3c5e7f9b20",
	'aliases: [Без имени]',
	"layer: content",
	"status: draft",
	"owner: human",
	"---",
	"",
	"# Без имени",
	"",
].join("\n");
const noTitleEntry = normalizeEntry("notes/note_01a17d3b-9f01-7a11-8e01-1f2e3d4c5b6a.md", noTitle);
check(noTitleEntry.kind === "partial", `B5: объект без title — partial (${noTitleEntry.kind})`);
check(
	Array.isArray(noTitleEntry.missing) && noTitleEntry.missing.length === 1 && noTitleEntry.missing[0] === "title",
	`B6: missing = [title] (${JSON.stringify(noTitleEntry.missing)})`,
);
check(hasTitleError(noTitleEntry), "B7: §3.5.2 — hasTitleError = true (нарушение INV-07)");
const noTitleIndex = indexFiles([{ path: noTitleEntry.path, text: noTitle }]);
check(
	getDisplayTitle(noTitleIndex, noTitleEntry.path) === "note_01a17d3b-9f01-7a11-8e01-1f2e3d4c5b6a",
	"B8: §3.5 — отображается имя файла",
);
check(!hasTitleError(entries[0]), "B9: у корректного объекта hasTitleError = false");

// индикатор при совпадении title (§3.4): определения системного слоя и слоя наполнения
const definitionSystem = [
	"---",
	"id: 01a17d3b-9f10-7a11-8e01-1f2e3d4c5b6a",
	"type: type",
	"defined_by: 01a17d3b-0000-7000-8000-000000000001",
	"title: Определение типа Заметка",
	"aliases: [Определение типа Заметка, note]",
	"type_value: note",
	"layer: system",
	"status: accepted",
	"owner: human",
	"---",
	"",
	"# Определение типа Заметка",
	"",
].join("\n");
const instanceA = [
	"---",
	"id: 01a17d3b-9f11-7a11-8e01-1f2e3d4c5b6a",
	"type: note",
	"defined_by: 01a17d3b-9f10-7a11-8e01-1f2e3d4c5b6a",
	"title: Одно имя",
	"aliases: [Одно имя]",
	"layer: content",
	"status: accepted",
	"owner: human",
	"---",
	"",
	"# Одно имя",
	"",
].join("\n");
const instanceB = instanceA
	.replace("01a17d3b-9f11-7a11-8e01-1f2e3d4c5b6a", "01a17d3b-9f12-7a11-8e01-1f2e3d4c5b6a")
	.replace("note_01a17d3b", "note_01a17d3b");
const synthetic = indexFiles([
	{ path: "model/type_01a17d3b-9f10-7a11-8e01-1f2e3d4c5b6a.md", text: definitionSystem },
	{ path: "notes/note_01a17d3b-9f11-7a11-8e01-1f2e3d4c5b6a.md", text: instanceA },
	{ path: "notes/note_01a17d3b-9f12-7a11-8e01-1f2e3d4c5b6a.md", text: instanceB },
]);
check(synthetic.stats().objects === 3, "B10: синтетический индекс — три объекта");
const collisions = synthetic.titleCollisions();
check(collisions.size === 1 && [...collisions.values()][0].length === 2, `B11: §3.4 — одна группа совпадений (${collisions.size})`);
const indicators = collisionIndicators(synthetic);
check(
	indicators.get("notes/note_01a17d3b-9f11-7a11-8e01-1f2e3d4c5b6a.md") === "note",
	`B12: индикатор — машинный ключ определения (${indicators.get("notes/note_01a17d3b-9f11-7a11-8e01-1f2e3d4c5b6a.md")})`,
);
check(
	getTitleIndicator(index, entries[0]) === undefined,
	"B13: в examples/ индикатор не определён — определения типов вне набора (граница v1)",
);
check(index.titleCollisions().size === 0, "B14: в examples/ совпадений title нет");

// ------------------------------------------------------------------ C. видимость слоёв
section("C. Видимость слоёв (§2 контракта)");
check(
	DEFAULT_LAYER_VISIBILITY.system === false &&
		DEFAULT_LAYER_VISIBILITY.classification === true &&
		DEFAULT_LAYER_VISIBILITY.content === true,
	"C1: §2.3 — по умолчанию content и classification видимы, system скрыт",
);
check(
	isLayerVisible(DEFAULT_SETTINGS.layerVisibility, "system") === false &&
		isLayerVisible(DEFAULT_SETTINGS.layerVisibility, "content") === true,
	"C2: isLayerVisible соответствует состоянию по умолчанию",
);
const systemEntry = entries.find((entry) => entry.layer === "system");
const contentEntry = entries.find((entry) => entry.layer === "content");
const classificationEntry = entries.find((entry) => entry.layer === "classification");
check(!isEntryVisible(systemEntry, DEFAULT_LAYER_VISIBILITY), "C3: объект системного слоя скрыт по умолчанию");
check(isEntryVisible(contentEntry, DEFAULT_LAYER_VISIBILITY), "C4: объект слоя наполнения видим");
check(isEntryVisible(classificationEntry, DEFAULT_LAYER_VISIBILITY), "C5: объект слоя классификации видим");
check(isEntryVisible(plainEntry, DEFAULT_LAYER_VISIBILITY), "C6: §2.5.3 — файл вне модели не скрывается");
check(isEntryVisible(undefined, DEFAULT_LAYER_VISIBILITY), "C7: §2.5.3 — неизвестный файл не скрывается");

function visibleCount(visibility) {
	return entries.filter((entry) => isEntryVisible(entry, visibility)).length;
}
const byIdPreset = Object.fromEntries(CANONICAL_PRESETS.map((preset) => [preset.id, preset.visibility]));
check(visibleCount(byIdPreset["knowledge-only"]) === 14, `C8: пресет «Только знания» — 14 видимых (получено ${visibleCount(byIdPreset["knowledge-only"])})`);
check(visibleCount(byIdPreset["model"]) === 5, `C9: пресет «Модель» — 5 видимых (получено ${visibleCount(byIdPreset["model"])})`);
check(visibleCount(byIdPreset["all"]) === 19, `C10: пресет «Всё» — 19 видимых (получено ${visibleCount(byIdPreset["all"])})`);
check(CANONICAL_PRESETS.length === 3, "C11: три канонических пресета (§2.2)");
check(matchingPreset(DEFAULT_SETTINGS) === null, "C12: состояние по умолчанию не совпадает ни с одним пресетом");

const afterPreset = applyPreset(DEFAULT_SETTINGS, "model");
check(
	afterPreset.layerVisibility.system === true && afterPreset.layerVisibility.content === false,
	"C13: applyPreset меняет тумблеры",
);
check(afterPreset.activePreset === "model", `C14: activePreset = model (${afterPreset.activePreset})`);
check(DEFAULT_SETTINGS.layerVisibility.system === false, "C15: applyPreset не изменяет переданные настройки");
const afterToggle = setLayerVisible(afterPreset, "classification", false);
check(
	afterToggle.layerVisibility.classification === false && afterToggle.activePreset === null,
	`C16: ручной тумблер сбрасывает активный пресет, если состояние пресету не равно (${afterToggle.activePreset})`,
);
const afterToggleToPreset = setLayerVisible(afterPreset, "content", true);
check(
	afterToggleToPreset.activePreset === "all",
	`C16a: ручной тумблер, давший комбинацию пресета, помечает его активным (${afterToggleToPreset.activePreset})`,
);
const afterReset = resetToDefault(afterToggle);
check(
	afterReset.layerVisibility.system === false &&
		afterReset.layerVisibility.classification === true &&
		afterReset.layerVisibility.content === true,
	"C17: resetToDefault возвращает состояние §2.3",
);
check(applyPreset(DEFAULT_SETTINGS, "несуществующий") === DEFAULT_SETTINGS, "C18: неизвестный пресет настройки не меняет");

const normalizedEmpty = normalizeSettings({});
check(
	normalizedEmpty.layerVisibility.system === false && normalizedEmpty.customPresets.length === 0,
	"C19: normalizeSettings({}) — значения по умолчанию",
);
const normalizedGarbage = normalizeSettings("строка");
check(normalizedGarbage.layerVisibility.content === true, "C20: normalizeSettings(мусор) — значения по умолчанию");
const normalizedPartial = normalizeSettings({ layerVisibility: { system: true } });
check(
	normalizedPartial.layerVisibility.system === true && normalizedPartial.layerVisibility.content === true,
	"C21: normalizeSettings дополняет недостающие тумблеры",
);
const normalizedBad = normalizeSettings({ layerVisibility: { system: "да", content: false } });
check(
	normalizedBad.layerVisibility.system === false && normalizedBad.layerVisibility.content === false,
	"C22: недопустимое значение тумблера игнорируется",
);
const normalizedCustom = normalizeSettings({
	customPresets: [{ id: "mine", label: "Мой", visibility: { system: true, classification: false, content: true } }, null],
});
check(normalizedCustom.customPresets.length === 1, `C23: пользовательские пресеты фильтруются (${normalizedCustom.customPresets.length})`);
check(applyPreset(normalizedCustom, "mine").layerVisibility.classification === false, "C24: пользовательский пресет применяется");

// ------------------------------------------------------------------ D. подмножество YAML
section("D. Разбор frontmatter (подмножество YAML)");
const yamlSource = [
	"# комментарий верхнего уровня",
	"title: \"Обёртка: изображение #1\"   # комментарий в конце строки",
	"aliases: [Первый, 'Второй alias', \"Третий: с двоеточием\"]",
	"position: 4",
	"duration: 7.5",
	"draft: true",
	"empty:",
	"tags:",
	"  - a",
	"  - b",
	"nested:",
	"  inner: значение",
	"  list:",
	"    - 1",
	"    - 2",
	"literal: |",
	"  строка один",
	"  строка два",
	"folded: >",
	"  строка A",
	"  строка B",
	"maps:",
	"  - key: value",
	"  - key: other",
	"flow: {a: b}",
	"anchor: &ref значение",
].join("\n");
const parsed = parseYamlSubset(yamlSource);
check(parsed.data.title === "Обёртка: изображение #1", `D1: строка в двойных кавычках с «#» и «:» (${parsed.data.title})`);
check(
	Array.isArray(parsed.data.aliases) && parsed.data.aliases.length === 3 && parsed.data.aliases[1] === "Второй alias",
	`D2: инлайн-список (${JSON.stringify(parsed.data.aliases)})`,
);
check(parsed.data.position === 4 && parsed.data.duration === 7.5, "D3: целое и дробное числа");
check(parsed.data.draft === true, "D4: логическое значение");
check(parsed.data.empty === null, "D5: пустое значение — null");
check(JSON.stringify(parsed.data.tags) === JSON.stringify(["a", "b"]), `D6: блочный список (${JSON.stringify(parsed.data.tags)})`);
check(parsed.data.nested && parsed.data.nested.inner === "значение", "D7: вложенное отображение");
check(
	parsed.data.nested && JSON.stringify(parsed.data.nested.list) === JSON.stringify([1, 2]),
	`D8: список во вложенном отображении (${JSON.stringify(parsed.data.nested && parsed.data.nested.list)})`,
);
check(parsed.data.literal === "строка один\nстрока два", `D9: блочный скаляр «|» (${JSON.stringify(parsed.data.literal)})`);
check(parsed.data.folded === "строка A строка B", `D10: блочный скаляр «>» (${JSON.stringify(parsed.data.folded)})`);
check(
	Array.isArray(parsed.data.maps) && parsed.data.maps.length === 2 && parsed.data.maps[0].key === "value",
	`D11: список отображений (${JSON.stringify(parsed.data.maps)})`,
);
check(parsed.unsupported.includes("flow") && parsed.data.flow === null, `D12: поточное отображение не поддержано (${JSON.stringify(parsed.unsupported)})`);
check(parsed.unsupported.includes("anchor"), "D13: якорь не поддержан");

const split = splitFrontmatter("---\nid: x\n---\n\n# Тело\n");
check(split.frontmatter === "id: x" && split.body.startsWith("\n# Тело"), "D14: splitFrontmatter отделяет тело");
check(splitFrontmatter("# Без frontmatter\n").frontmatter === null, "D15: файл без frontmatter");
const crlf = normalizeEntry("notes/note_x.md", "---\r\ntitle: Имя\r\n---\r\n\r\n# Имя\r\n");
check(crlf.title === "Имя" && crlf.frontmatter, `D16: CRLF разбирается (${JSON.stringify(crlf.title)})`);

// ------------------------------------------------------------------ E. инкрементальное обновление
section("E. Инкрементальное обновление и нарушения");
const mutable = indexFiles(data.objects);
const target = entries.find((entry) => entry.type === "book");
const before = mutable.size;
const updatedText = data.objects.find((file) => file.path === target.path).text.replace(
	/^title: .*$/m,
	"title: Книга с новым именем",
);
mutable.update(target.path, updatedText);
check(mutable.size === before, "E1: повторная обработка файла не меняет размер индекса");
check(mutable.getByPath(target.path).title === "Книга с новым именем", "E2: update заменяет запись");
check(getDisplayTitle(mutable, target.path) === "Книга с новым именем", "E3: отображаемое имя обновилось");
check(mutable.getById(target.id).title === "Книга с новым именем", "E4: доступ по id после обновления");

mutable.remove(target.path);
check(mutable.size === before - 1, "E5: remove уменьшает индекс");
check(mutable.getByPath(target.path) === undefined, "E6: записи по пути нет");
check(mutable.getById(target.id) === undefined, "E7: записи по id нет");
check(mutable.remove(target.path) === false, "E8: повторный remove возвращает false");

const renamedPath = `moved/${target.basename}.md`;
mutable.update(renamedPath, data.objects.find((file) => file.path === target.path).text);
check(mutable.size === before && mutable.getByPath(renamedPath) !== undefined, "E9: переименование — remove + update");

const duplicates = indexFiles([
	{ path: "a/note_01a17d3b-9f20-7a11-8e01-1f2e3d4c5b6a.md", text: instanceA.replace("9f11", "9f20") },
	{ path: "b/note_01a17d3b-9f20-7a11-8e01-1f2e3d4c5b6a.md", text: instanceA.replace("9f11", "9f20") },
]);
check(JSON.stringify(duplicates.duplicateIds()) === JSON.stringify(["01a17d3b-9f20-7a11-8e01-1f2e3d4c5b6a"]), `E10: INV-02 — повтор id обнаружен (${duplicates.duplicateIds()})`);
check(
	duplicates.getById("01a17d3b-9f20-7a11-8e01-1f2e3d4c5b6a").path.startsWith("a/"),
	"E11: доступ по повторяющемуся id детерминирован (первый по сортировке путь)",
);
check(duplicates.size === 2, `E12: обе записи доступны по пути (${duplicates.size})`);

const badId = normalizeEntry("notes/note_not-a-uuid.md", instanceA.replace("01a17d3b-9f11-7a11-8e01-1f2e3d4c5b6a", "не-uuid"));
check(badId.kind === "partial" && badId.missing.includes("id"), `E13: id не в форме UUIDv7 — partial (${JSON.stringify(badId.missing)})`);
const badIdIndex = indexFiles([{ path: badId.path, text: instanceA.replace("01a17d3b-9f11-7a11-8e01-1f2e3d4c5b6a", "не-uuid") }]);
check(badIdIndex.getById("не-uuid") === undefined, "E14: в обратный индекс не-UUIDv7 не попадает");

const mutable2 = new VaultIndex();
mutable2.update("notes/note_01a17d3b-9f30-7a11-8e01-1f2e3d4c5b6a.md", instanceA.replace("9f11", "9f30"));
mutable2.clear();
check(mutable2.size === 0, "E15: clear очищает индекс (onunload)");

// ------------------------------------------------------------------ F. производные идентичности
section("F. Производные функции идентичности");
check(typePrefix("person") === "person", "F1: person → person");
check(typePrefix("literature-note") === "literature-note", "F2: literature-note без обрезки (15 символов)");
check(typePrefix("hierarchical-category") === "hierarchical-cat", `F3: обрезка до 16 (${typePrefix("hierarchical-category")})`);
check(typePrefix("book-2") === "book-2", "F4: book-2 → book-2");
check(typePrefix("Literature Note") === "literature-note", "F5: защита от ручной правки регистра и пробелов");
check(typePrefix("a__b..c//d") === "a-b-c-d", `F6: последовательности разделителей (${typePrefix("a__b..c//d")})`);
check(typePrefix("-x-") === "x", "F7: дефисы на концах удаляются");
check(typePrefix("длинное-имя-типа-превышающее-лимит") .length <= 16, "F8: результат не длиннее 16 символов");
check(layerOfType("facet-value") === "classification", "F9: facet-value → classification");
check(layerOfType("validation-rule") === "system", "F10: validation-rule → system");
check(layerOfType("field-expansion") === "system", "F11: field-expansion → system (INV-14, схема object.json)");
check(layerOfType("book") === "content", "F12: book → content");
const link = parseCanonicalLink("[[note_01a17d3b-6b10-7d52-9a34-1e7c42b8f056|Заметка]]");
check(
	link !== null && link.id === "01a17d3b-6b10-7d52-9a34-1e7c42b8f056" && link.alias === "Заметка" && link.prefix === "note",
	`F13: INV-15 — разбор канонической ссылки (${JSON.stringify(link)})`,
);
check(parseCanonicalLink("[[Пустая ссылка]]") === null, "F14: неканоническая ссылка — null");
check(parseCanonicalLink("note_01a17d3b-6b10-7d52-9a34-1e7c42b8f056") === null, "F15: значение без [[]] — null");

const relationValues = [];
for (const file of data.objects) {
	const fm = splitFrontmatter(file.text).frontmatter;
	for (const match of fm ? fm.matchAll(/\[\[[^\]]+\]\]/g) : []) {
		relationValues.push(match[0]);
	}
}
const canonical = relationValues.filter((value) => parseCanonicalLink(value) !== null);
check(canonical.length === 23, `F16: в examples/ 23 канонические ссылки (найдено ${canonical.length} из ${relationValues.length})`);
check(
	canonical.every((value) => index.getById(parseCanonicalLink(value).id) !== undefined),
	"F17: все цели канонических ссылок разрешаются индексом по id",
);

// ------------------------------------------------------------------ итог
console.log();
for (const message of notes) {
	console.log(`НАБЛЮДЕНИЕ: ${message}`);
}
for (const failure of failures) {
	console.log(`ОШИБКА: ${failure}`);
}
console.log(`Проверок пройдено: ${passed}; ошибок: ${failures.length}`);
process.exitCode = failures.length ? 1 : 0;
