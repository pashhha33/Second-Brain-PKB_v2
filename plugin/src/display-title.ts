/**
 * display-title.ts — отображаемое имя объекта: стаб контракта §3
 * (`docs/metamodel/10-plugin-ux-contracts.md`, ADR-008, U2, DL-032).
 *
 * Контракт: во всех списках и заголовках вместо имени файла отображается `title` объекта
 * (INV-07); источник — frontmatter, а не имя файла. Файл не переименовывается (INV-06),
 * содержимое заметки подменой не изменяется. Файлы вне модели отображаются именем файла (§3.5).
 *
 * Границы: модуль возвращает строку, диагностику и решение о подмене, но сам в интерфейс
 * не пишет — подмену выполняют модули `title-dom.ts`, `explorer-title.ts`, `leaf-title.ts`
 * и `title-controller.ts` (iter-015, DL-053, DL-054). В этой версии подменяются проводник и
 * заголовки вкладок; поиск, граф, quick switcher, панели ссылок и предпросмотр отложены.
 * Модуль чистый: не импортирует `obsidian`.
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

// ---------------------------------------------------------------- подмена имени (iter-015)

/**
 * Настройка подмены отображаемого имени — feature-flag «Подменять имя на title»
 * (TASK iter-015, DL-053). Хранится в настройках плагина вместе с видимостью слоёв.
 */
export interface DisplayTitleSettings {
	/** `true` — в проводнике и заголовках вкладок вместо имени файла показывается `title`. */
	override: boolean;
}

/** Значение по умолчанию: подмена включена (TASK iter-015, пункт 2; DL-053). */
export const DEFAULT_DISPLAY_TITLE_SETTINGS: DisplayTitleSettings = { override: true };

/**
 * Приводит прочитанные из `loadData()` настройки подмены к допустимым: недостающее или
 * не-логическое значение заменяется значением по умолчанию (включено).
 */
export function normalizeDisplayTitleSettings(loaded: unknown): DisplayTitleSettings {
	if (!loaded || typeof loaded !== "object") {
		return { ...DEFAULT_DISPLAY_TITLE_SETTINGS };
	}
	const source = loaded as Partial<DisplayTitleSettings>;
	return {
		override:
			typeof source.override === "boolean" ? source.override : DEFAULT_DISPLAY_TITLE_SETTINGS.override,
	};
}

/**
 * Текст подмены для пути: `title` объекта модели либо `null`, если подмена не применяется
 * и поверхность остаётся в исходном (stock) состоянии.
 *
 * `null` возвращается, когда:
 * - подмена выключена настройкой (feature-flag, DL-053);
 * - файл не является объектом модели — `plain` или `partial` (§3.5.1: подменяются только
 *   объекты модели, файлы вне модели отображаются именем файла);
 * - объект модели не имеет `title` — нарушение INV-07 (§3.5.2: показывается имя файла
 *   и пометка об ошибке, см. `titleErrorNote`);
 * - `title` совпадает с именем файла без расширения — подмена не меняет текст, поэтому
 *   DOM не трогается (§3.4: индикатор совпадения требует реестра определений, см. DL-053).
 *
 * Файл не переименовывается и содержимое заметки не изменяется (§3.2, INV-03, INV-06).
 */
export function overrideTitleOf(
	entry: IndexEntry | undefined,
	path: string,
	settings: DisplayTitleSettings,
): string | null {
	if (!settings.override) {
		return null;
	}
	if (!entry || entry.kind !== "object") {
		return null;
	}
	const title = entry.title?.trim();
	if (!title) {
		return null;
	}
	if (title === basenameOf(path)) {
		return null;
	}
	return title;
}

/**
 * §3.5.2: текст пометки об ошибке для объекта модели без `title` (нарушение INV-07),
 * либо `undefined`, если нарушения нет. Поверхности показывают пометку классом
 * `sbpk-title-error` и подсказкой; исправление объекта — за владельцем (контроль — фаза 2).
 */
export function titleErrorNote(entry: IndexEntry | undefined, path: string): string | undefined {
	if (!hasTitleError(entry)) {
		return undefined;
	}
	return `Нарушение INV-07: у объекта модели нет title — отображается имя файла «${basenameOf(path)}»`;
}
