/**
 * frontmatter.ts — нормализация записи индекса по frontmatter заметки (фаза 4).
 *
 * Назначение: из текста заметки `.md` получить запись индекса с обязательными свойствами
 * объекта модели (INV-01…INV-12) либо зафиксировать, что файл объектом модели не является
 * (§2.5.3 и §3.5 контракта `docs/metamodel/10-plugin-ux-contracts.md`).
 *
 * Границы v1: согласованность значений между собой не проверяется — равенство `aliases[0]`
 * и `title` (INV-08), соответствие `layer` значению `type` (INV-09), имя файла (INV-06)
 * и прочие ограничения остаются правилами валидации фазы 2 (`docs/validation/`), исполнение
 * которых в рантайме вне scope iter-014. Запись хранит производные поля (`typePrefix`,
 * `expectedLayer`, `machineKey`) как материал для этих проверок в фазе 5.
 *
 * Разбор YAML — [`./yaml.ts`](./yaml.ts); модуль чистый и не импортирует `obsidian`.
 */

import { basenameOf, isTypeValue, isUuidV7, layerOfType, MACHINE_KEY_FIELDS, typePrefix } from "./identity";
import {
	MANDATORY_KEYS,
	MODEL_LAYERS,
	OBJECT_STATUSES,
	type IndexEntry,
	type MandatoryKey,
	type ModelLayer,
	type ObjectStatus,
} from "./types";
import { parseYamlSubset, splitFrontmatter } from "./yaml";

/** Непустая строка после удаления пробелов по краям (INV-07, INV-11) либо `undefined`. */
function nonBlankString(value: unknown): string | undefined {
	if (typeof value !== "string") {
		return undefined;
	}
	const trimmed = value.trim();
	return trimmed ? trimmed : undefined;
}

/** Непустой список строк (INV-08) либо `undefined`. */
function stringList(value: unknown): string[] | undefined {
	if (!Array.isArray(value)) {
		return undefined;
	}
	const items = value.filter((item): item is string => typeof item === "string" && item.trim().length > 0);
	return items.length ? items.map((item) => item.trim()) : undefined;
}

/** Значение из закрытого набора (INV-09, INV-10) либо `undefined`. */
function enumValue<T extends string>(value: unknown, allowed: readonly T[]): T | undefined {
	return typeof value === "string" && allowed.includes(value as T) ? (value as T) : undefined;
}

/** Машинный ключ определения системного слоя (INV-13, INV-16, INV-17) либо `undefined`. */
function machineKeyOf(raw: Record<string, unknown>): string | undefined {
	for (const field of MACHINE_KEY_FIELDS) {
		const value = nonBlankString(raw[field]);
		if (value !== undefined) {
			return value;
		}
	}
	return undefined;
}

/**
 * Нормализует разобранный frontmatter в запись индекса.
 *
 * Род записи: `object` — все восемь обязательных свойств присутствуют и имеют форму,
 * требуемую схемой `schema/object.json`; иначе `partial` с перечнем недостающих ключей
 * в `missing`. Значение ключа недопустимой формы считается отсутствующим: например, `id`
 * не в форме UUIDv7 (INV-01) или `layer` вне набора трёх значений (INV-09).
 */
export function normalizeFrontmatter(
	path: string,
	raw: Record<string, unknown>,
	unsupported: readonly string[] = [],
): IndexEntry {
	const id = isUuidV7(raw["id"]) ? raw["id"] : undefined;
	const type = isTypeValue(raw["type"]) ? raw["type"] : undefined;
	const definedBy = isUuidV7(raw["defined_by"]) ? raw["defined_by"] : undefined;
	const title = nonBlankString(raw["title"]);
	const aliases = stringList(raw["aliases"]);
	const layer = enumValue<ModelLayer>(raw["layer"], MODEL_LAYERS);
	const status = enumValue<ObjectStatus>(raw["status"], OBJECT_STATUSES);
	const owner = nonBlankString(raw["owner"]);

	const present: Record<MandatoryKey, boolean> = {
		id: id !== undefined,
		type: type !== undefined,
		defined_by: definedBy !== undefined,
		title: title !== undefined,
		aliases: aliases !== undefined,
		layer: layer !== undefined,
		status: status !== undefined,
		owner: owner !== undefined,
	};
	const missing = MANDATORY_KEYS.filter((key) => !present[key]);

	const entry: IndexEntry = {
		kind: missing.length === 0 ? "object" : "partial",
		path,
		basename: basenameOf(path),
		frontmatter: true,
	};
	if (id !== undefined) {
		entry.id = id;
	}
	if (type !== undefined) {
		entry.type = type;
		entry.typePrefix = typePrefix(type);
		entry.expectedLayer = layerOfType(type);
	}
	if (definedBy !== undefined) {
		entry.definedBy = definedBy;
	}
	if (title !== undefined) {
		entry.title = title;
	}
	if (aliases !== undefined) {
		entry.aliases = aliases;
	}
	if (layer !== undefined) {
		entry.layer = layer;
	}
	if (status !== undefined) {
		entry.status = status;
	}
	if (owner !== undefined) {
		entry.owner = owner;
	}
	const machineKey = machineKeyOf(raw);
	if (machineKey !== undefined) {
		entry.machineKey = machineKey;
	}
	if (missing.length) {
		entry.missing = missing;
	}
	if (unsupported.length) {
		entry.unsupported = [...unsupported];
	}
	return entry;
}

/** Разбирает текст заметки `.md` и возвращает запись индекса. */
export function normalizeEntry(path: string, text: string): IndexEntry {
	const { frontmatter } = splitFrontmatter(text);
	if (frontmatter === null) {
		return { kind: "plain", path, basename: basenameOf(path), frontmatter: false };
	}
	const { data, unsupported } = parseYamlSubset(frontmatter);
	return normalizeFrontmatter(path, data, unsupported);
}
