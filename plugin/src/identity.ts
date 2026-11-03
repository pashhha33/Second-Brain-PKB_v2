/**
 * identity.ts — производные функции идентичности объекта (фаза 4).
 *
 * Основание: `docs/metamodel/01-invariants.md` — INV-01 (формат `id`), INV-04 (`type`),
 * INV-05 (`type_prefix`), INV-06 (имя файла), INV-09 (`layer`), `docs/metamodel/09-structural-invariants.md`
 * — INV-15 (каноническая ссылка). Паттерны совпадают с `$defs` схемы `schema/object.json`;
 * норма — документы метамодели, схема и этот модуль должны оставаться согласованными (R-007).
 *
 * Модуль чистый: не импортирует `obsidian` и не обращается к хранилищу, поэтому проверяется
 * вне приложения (см. `plugin/README.md`, раздел «Проверка»).
 */

import type { ModelLayer } from "./types";

/** INV-01: UUIDv7 (RFC 9562) в канонической строчной форме — `$defs/uuidv7` схемы `object.json`. */
export const UUIDV7_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

/** INV-04, INV-13: `type` и `type_value` — ASCII kebab-case (`$defs/type-value`). */
export const TYPE_VALUE_PATTERN = /^[a-z0-9]+(-[a-z0-9]+)*$/;

/** INV-05: форма префикса — без дефиса на концах, до 16 символов (`$defs/type-prefix`). */
export const TYPE_PREFIX_PATTERN = /^[a-z0-9]([a-z0-9-]*[a-z0-9])?$/;

/**
 * INV-09: значения `type`, требующие `layer: classification`.
 * Перечень совпадает с блоком `allOf` схемы `schema/object.json`.
 */
export const CLASSIFICATION_TYPES: readonly string[] = [
	"domain",
	"hierarchical-category",
	"facet",
	"facet-value",
];

/**
 * INV-09, INV-14: значения `type`, требующие `layer: system` — шесть из десяти встроенных
 * метатипов (`docs/metamodel/03-builtin-types.md`); остальные четыре (`domain`,
 * `hierarchical-category`, `facet`, `facet-value`) требуют `layer: classification`.
 * `field-expansion` добавлен в iter-006 (DL-029) и в формулировке INV-09 не упомянут;
 * расхождение зафиксировано в ADR-009 (S3). Перечень соответствует ветви `allOf` схемы
 * `schema/object.json`; её описание говорит о «десяти встроенных метатипах» для `system` —
 * расхождение описания и перечня схемы отмечено в REPORT.md iter-014 (схема read-only).
 */
export const SYSTEM_TYPES: readonly string[] = [
	"type",
	"property",
	"relation",
	"automation",
	"validation-rule",
	"field-expansion",
];

/** Ключи frontmatter, хранящие машинный идентификатор определения системного слоя (INV-13, INV-16, INV-17). */
export const MACHINE_KEY_FIELDS: readonly string[] = [
	"type_value",
	"property_key",
	"relation_key",
	"rule_key",
];

/** INV-01: значение `id` — UUIDv7 в канонической строчной форме. */
export function isUuidV7(value: unknown): value is string {
	return typeof value === "string" && UUIDV7_PATTERN.test(value);
}

/** INV-04: значение `type` — непустая строка в ASCII kebab-case. */
export function isTypeValue(value: unknown): value is string {
	return typeof value === "string" && TYPE_VALUE_PATTERN.test(value);
}

/**
 * INV-05, DL-009: префикс имени файла, производный от `type`.
 *
 * Шаги правила: привести к нижнему регистру; заменить последовательности разделителей
 * (пробел, `_`, `.`, `/`) одним дефисом; удалить все символы, кроме `[a-z0-9-]`;
 * удалить дефисы на концах; обрезать до 16 символов и снова удалить дефис в конце.
 * Пустой результат означает невалидный `type` (INV-05, пункт 6).
 */
export function typePrefix(type: string): string {
	let result = type
		.toLowerCase()
		.replace(/[ _./]+/g, "-")
		.replace(/[^a-z0-9-]/g, "")
		.replace(/^-+/, "")
		.replace(/-+$/, "");
	if (result.length > 16) {
		result = result.slice(0, 16).replace(/-+$/, "");
	}
	return result;
}

/** INV-06: ожидаемое имя файла без пути и расширения — `{{type_prefix}}_{{id}}`. */
export function expectedBasename(type: string, id: string): string {
	return `${typePrefix(type)}_${id}`;
}

/**
 * INV-09: слой, требуемый значением `type`.
 * `domain`, `hierarchical-category`, `facet`, `facet-value` ⇒ `classification`;
 * десять встроенных метатипов ⇒ `system`; прочие значения ⇒ `content`.
 */
export function layerOfType(type: string): ModelLayer {
	if (CLASSIFICATION_TYPES.includes(type)) {
		return "classification";
	}
	if (SYSTEM_TYPES.includes(type)) {
		return "system";
	}
	return "content";
}

/** Имя файла без пути и расширения. */
export function basenameOf(path: string): string {
	const last = path.split(/[\\/]/).pop() ?? path;
	const dot = last.lastIndexOf(".");
	return dot > 0 ? last.slice(0, dot) : last;
}

/** Разобранная каноническая ссылка (INV-15). */
export interface CanonicalLink {
	/** Имя файла цели без пути и расширения: `{{type_prefix}}_{{id}}`. */
	target: string;
	/** Префикс цели. */
	prefix: string;
	/** `id` цели. */
	id: string;
	/** Alias ссылки — по INV-15 равен `title` цели. */
	alias: string;
}

/**
 * INV-15: разбор канонической внутренней ссылки `[[{{type_prefix}}_{{id}}|{{title}}]]`.
 * Возвращает `null`, если значение не является канонической ссылкой: пустые ссылки в теле
 * заметки допустимы и обрабатываются контрактом создания объекта (раздел 4 контракта, фаза 5).
 */
export function parseCanonicalLink(value: unknown): CanonicalLink | null {
	if (typeof value !== "string") {
		return null;
	}
	const match = /^\[\[([a-z0-9][a-z0-9-]{0,15})_([0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})\|(.+)\]\]$/.exec(
		value,
	);
	if (!match) {
		return null;
	}
	return { target: `${match[1]}_${match[2]}`, prefix: match[1], id: match[2], alias: match[3] };
}

/** INV-15: значение является канонической ссылкой. */
export function isCanonicalLink(value: unknown): boolean {
	return parseCanonicalLink(value) !== null;
}
