/**
 * display-title.ts — отображаемое имя объекта: стаб контракта §3
 * (`docs/metamodel/10-plugin-ux-contracts.md`, ADR-008, U2, DL-032).
 *
 * Контракт: во всех списках и заголовках вместо имени файла отображается `title` объекта
 * (INV-07); источник — frontmatter, а не имя файла. Файл не переименовывается (INV-06),
 * содержимое заметки подменой не изменяется. Файлы вне модели отображаются именем файла (§3.5).
 *
 * Границы v1: модуль возвращает строку и диагностику, но не подменяет имя в проводнике,
 * поиске, вкладках и графе — monkey-patch поверхностей выполняется в фазе 5
 * (вне scope iter-014). Модуль чистый: не импортирует `obsidian`.
 */

import { basenameOf } from "./identity";
import type { IndexEntry, PathLike } from "./types";
import type { VaultIndex } from "./vault-index";

/**
 * Отображаемое имя записи индекса (§3.1, §3.5):
 * `title` объекта модели, иначе имя файла без пути и расширения.
 */
export function displayTitleOf(entry: IndexEntry | undefined, path?: string): string {
	if (entry?.kind === "object" && entry.title) {
		return entry.title;
	}
	if (entry) {
		return entry.basename;
	}
	return path ? basenameOf(path) : "";
}

/**
 * Отображаемое имя файла: `getDisplayTitle(file | path) → string`.
 * Принимает путь либо объект с полем `path` (в Obsidian — `TFile`).
 */
export function getDisplayTitle(index: VaultIndex, file: PathLike | string): string {
	const path = typeof file === "string" ? file : file.path;
	return displayTitleOf(index.getByPath(path), path);
}

/**
 * §3.5.2: файл является объектом модели, но `title` отсутствует или пуст — нарушение INV-07.
 * Отображается имя файла и пометка об ошибке; объект подлежит исправлению (контроль — фаза 2).
 * Признак: не хватает единственного обязательного свойства — `title`.
 */
export function hasTitleError(entry: IndexEntry | undefined): boolean {
	return (
		entry !== undefined &&
		entry.kind === "partial" &&
		entry.missing !== undefined &&
		entry.missing.length === 1 &&
		entry.missing[0] === "title"
	);
}

/**
 * §3.4: индикатор при совпадении `title` у нескольких объектов — `label` определения типа
 * (`label` = `title` определения, DL-021), а для определений системного слоя — машинный ключ
 * (`type_value`, `property_key`, `relation_key`, `rule_key`).
 *
 * Граница v1: возвращает `undefined`, если определение не найдено в индексе — до bootstrap
 * (фазы 4–5) определения типов в хранилище владельца отсутствуют.
 */
export function getTitleIndicator(index: VaultIndex, entry: IndexEntry | undefined): string | undefined {
	if (!entry?.definedBy) {
		return undefined;
	}
	const definition = index.getById(entry.definedBy);
	if (!definition) {
		return undefined;
	}
	if (definition.layer === "system") {
		return definition.machineKey ?? definition.title;
	}
	return definition.title;
}

/**
 * §3.4: группы объектов с совпадающим `title` и индикатор для каждой записи группы.
 * Вызовы подмены имени в поверхностях (фаза 5) используют этот перечень, чтобы показывать
 * индикатор только там, где имя неоднозначно.
 */
export function collisionIndicators(index: VaultIndex): Map<string, string | undefined> {
	const result = new Map<string, string | undefined>();
	for (const group of index.titleCollisions().values()) {
		for (const entry of group) {
			result.set(entry.path, getTitleIndicator(index, entry));
		}
	}
	return result;
}
