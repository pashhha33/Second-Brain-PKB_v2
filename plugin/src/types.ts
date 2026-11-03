/**
 * types.ts — доменные типы каркаса плагина (фаза 4).
 *
 * Основание: `docs/metamodel/01-invariants.md` (INV-01…INV-12 — обязательные свойства
 * объекта), `docs/metamodel/02-layers.md` (три слоя), `docs/metamodel/10-plugin-ux-contracts.md`
 * (отображаемое имя и видимость слоёв). Типы описывают данные, а не поведение UI:
 * контракт фиксирует наблюдаемое поведение, выбор Obsidian API остаётся за реализацией.
 */

/** Значение свойства `layer` (INV-09). */
export type ModelLayer = "system" | "classification" | "content";

/** Значение свойства `status` (INV-10). */
export type ObjectStatus = "draft" | "accepted" | "deprecated";

/** Все значения `layer` — канонический набор схемы `schema/object.json`. */
export const MODEL_LAYERS: readonly ModelLayer[] = ["system", "classification", "content"];

/** Все значения `status` — канонический набор схемы `schema/object.json`. */
export const OBJECT_STATUSES: readonly ObjectStatus[] = ["draft", "accepted", "deprecated"];

/**
 * Обязательные свойства объекта модели (INV-01…INV-12) в том виде, в каком они
 * хранятся во frontmatter: восемь ключей схемы `schema/object.json`.
 */
export const MANDATORY_KEYS = [
	"id",
	"type",
	"defined_by",
	"title",
	"aliases",
	"layer",
	"status",
	"owner",
] as const;

/** Имя одного обязательного свойства. */
export type MandatoryKey = (typeof MANDATORY_KEYS)[number];

/**
 * Род записи индекса:
 * - `object` — все восемь обязательных свойств присутствуют и имеют допустимую форму;
 * - `partial` — frontmatter есть, но состав или форма свойств неполны (файл вне модели,
 *   §2.5.3 и §3.5 контракта: такие файлы не скрываются тумблерами и отображаются именем файла);
 * - `plain` — frontmatter отсутствует (обычная заметка владельца).
 */
export type EntryKind = "object" | "partial" | "plain";

/**
 * Нормализованная запись индекса по одной заметке `.md`.
 *
 * Поля заполняются только если соответствующий ключ frontmatter присутствует и имеет
 * ожидаемую форму: каркас не додумывает значения и не выполняет правила валидации фазы 2
 * (вне scope iter-014). `missing` перечисляет обязательные ключи, которых не хватило
 * до `kind: "object"`.
 */
export interface IndexEntry {
	/** Род записи. */
	kind: EntryKind;
	/** Путь относительно корня хранилища, с расширением (`notes/book_….md`). */
	path: string;
	/** Имя файла без пути и расширения (INV-06: `{{type_prefix}}_{{id}}`). */
	basename: string;
	/** Найден ли блок YAML frontmatter. */
	frontmatter: boolean;
	/** `id` — UUIDv7 в канонической строчной форме (INV-01). */
	id?: string;
	/** `type` — значение типа в ASCII kebab-case (INV-04). */
	type?: string;
	/** Префикс имени файла, производный от `type` (INV-05). */
	typePrefix?: string;
	/** `title` — читаемое имя объекта (INV-07). */
	title?: string;
	/** `aliases` — список имён, `aliases[0] = title` (INV-08). */
	aliases?: string[];
	/** `layer` — явное значение свойства (INV-09). */
	layer?: ModelLayer;
	/** `status` — жизненный цикл объекта (INV-10). */
	status?: ObjectStatus;
	/** `owner` — владелец хранилища (INV-11). */
	owner?: string;
	/** `defined_by` — `id` определения типа в системном слое (INV-12). */
	definedBy?: string;
	/** Машинный ключ определения системного слоя: `type_value`, `property_key`, `relation_key` или `rule_key`. */
	machineKey?: string;
	/** Обязательные ключи, которых не хватило до объекта модели. */
	missing?: MandatoryKey[];
	/**
	 * Слой, требуемый значением `type` (INV-09). Заполняется при известном `type`
	 * и служит диагностикой расхождения `layer` и `type`; для фильтрации используется
	 * только явное значение `layer` (ADR-002, А1: слой — явное свойство).
	 */
	expectedLayer?: ModelLayer;
	/** Ключи frontmatter, которые парсер не разобрал (неподдерживаемые конструкции YAML). */
	unsupported?: string[];
}

/** Файл, переданный на разбор: путь и полное содержимое. */
export interface ScannedFile {
	path: string;
	text: string;
}

/** Объект, у которого есть `path` (в Obsidian — `TFile` или `TAbstractFile`). */
export interface PathLike {
	path: string;
}

/** Сводка состояния индекса — для отладки и панели настроек. */
export interface IndexStats {
	files: number;
	objects: number;
	partial: number;
	plain: number;
	byLayer: Record<ModelLayer, number>;
	duplicateIds: string[];
}
