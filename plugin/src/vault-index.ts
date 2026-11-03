/**
 * vault-index.ts — индекс объектов хранилища в памяти (фаза 4).
 *
 * Основание: TASK.md iter-014 (цель 2 — in-memory индекс: `id`, filename, `type`, `layer`,
 * `title`, path) и `docs/metamodel/10-plugin-ux-contracts.md` (поиск отображаемого имени
 * и фильтрация по слою обращаются к индексу, а не к файлам).
 *
 * Границы v1: индекс не выполняет правила валидации фазы 2 и не исправляет данные —
 * нарушение INV-02 (повтор `id`) фиксируется в `duplicateIds()`, а доступ по такому `id`
 * детерминированно возвращает запись с первым по сортировке путём. Модуль чистый: не импортирует
 * `obsidian`, поэтому полный проход по хранилищу проверяется вне приложения.
 */

import { normalizeEntry } from "./frontmatter";
import type { IndexEntry, IndexStats, ModelLayer, PathLike, ScannedFile } from "./types";
import { MODEL_LAYERS } from "./types";

/** Нормализация сравнения имён: регистр и пробельные символы не учитываются (§4.5 контракта). */
function normalizeName(value: string): string {
	return value.trim().replace(/\s+/g, " ").toLowerCase();
}

/** Индекс заметок хранилища: доступ по пути и по `id`, перечисление объектов модели. */
export class VaultIndex {
	private readonly byPath = new Map<string, IndexEntry>();
	private readonly pathsById = new Map<string, Set<string>>();

	/** Добавляет или заменяет запись индекса. */
	upsert(entry: IndexEntry): void {
		const previous = this.byPath.get(entry.path);
		if (previous) {
			this.forgetPath(previous);
		}
		this.byPath.set(entry.path, entry);
		if (entry.id) {
			let paths = this.pathsById.get(entry.id);
			if (!paths) {
				paths = new Set<string>();
				this.pathsById.set(entry.id, paths);
			}
			paths.add(entry.path);
		}
	}

	/** Разбирает текст заметки и обновляет запись индекса. */
	update(path: string, text: string): IndexEntry {
		const entry = normalizeEntry(path, text);
		this.upsert(entry);
		return entry;
	}

	/** Удаляет запись по пути (удаление или переименование файла). */
	remove(path: string): boolean {
		const entry = this.byPath.get(path);
		if (!entry) {
			return false;
		}
		this.forgetPath(entry);
		this.byPath.delete(path);
		return true;
	}

	/** Запись по пути относительно корня хранилища. */
	getByPath(path: string): IndexEntry | undefined {
		return this.byPath.get(path);
	}

	/** Запись по пути или по объекту с полем `path` (в Obsidian — `TFile`). */
	getByFile(file: PathLike | string): IndexEntry | undefined {
		return this.byPath.get(typeof file === "string" ? file : file.path);
	}

	/**
	 * Запись по `id` (INV-02). При нарушении уникальности возвращается запись с первым
	 * по сортировке путём, а `id` попадает в `duplicateIds()`.
	 */
	getById(id: string): IndexEntry | undefined {
		const paths = this.pathsById.get(id);
		if (!paths || paths.size === 0) {
			return undefined;
		}
		const first = [...paths].sort()[0];
		return this.byPath.get(first);
	}

	/** Все записи индекса в порядке сортировки путей. */
	entries(): IndexEntry[] {
		return [...this.byPath.keys()].sort().map((path) => this.byPath.get(path) as IndexEntry);
	}

	/** Только объекты модели (`kind: "object"`). */
	objects(): IndexEntry[] {
		return this.entries().filter((entry) => entry.kind === "object");
	}

	/** Объекты указанного слоя (INV-09). */
	objectsOfLayer(layer: ModelLayer): IndexEntry[] {
		return this.objects().filter((entry) => entry.layer === layer);
	}

	/** Объекты, у которых `title` или один из `aliases` совпадает с именем (§3.4, §4.5 контракта). */
	findByName(name: string): IndexEntry[] {
		const target = normalizeName(name);
		return this.objects().filter((entry) => {
			if (entry.title && normalizeName(entry.title) === target) {
				return true;
			}
			return (entry.aliases ?? []).some((alias) => normalizeName(alias) === target);
		});
	}

	/** Группы объектов с совпадающим `title` — основание индикатора из §3.4 контракта. */
	titleCollisions(): Map<string, IndexEntry[]> {
		const groups = new Map<string, IndexEntry[]>();
		for (const entry of this.objects()) {
			if (!entry.title) {
				continue;
			}
			const key = normalizeName(entry.title);
			const group = groups.get(key);
			if (group) {
				group.push(entry);
			} else {
				groups.set(key, [entry]);
			}
		}
		for (const [key, group] of groups) {
			if (group.length < 2) {
				groups.delete(key);
			}
		}
		return groups;
	}

	/** `id`, встречающиеся более чем в одном файле (нарушение INV-02). */
	duplicateIds(): string[] {
		const result: string[] = [];
		for (const [id, paths] of this.pathsById) {
			if (paths.size > 1) {
				result.push(id);
			}
		}
		return result.sort();
	}

	/** Число записей в индексе. */
	get size(): number {
		return this.byPath.size;
	}

	/** Число объектов модели. */
	get objectCount(): number {
		return this.objects().length;
	}

	/** Сводка состояния индекса. */
	stats(): IndexStats {
		const byLayer: Record<ModelLayer, number> = { system: 0, classification: 0, content: 0 };
		let objects = 0;
		let partial = 0;
		let plain = 0;
		for (const entry of this.byPath.values()) {
			if (entry.kind === "object") {
				objects++;
				if (entry.layer && MODEL_LAYERS.includes(entry.layer)) {
					byLayer[entry.layer]++;
				}
			} else if (entry.kind === "partial") {
				partial++;
			} else {
				plain++;
			}
		}
		return { files: this.byPath.size, objects, partial, plain, byLayer, duplicateIds: this.duplicateIds() };
	}

	/** Очищает индекс (вызывается в `onunload` и перед полным перестроением). */
	clear(): void {
		this.byPath.clear();
		this.pathsById.clear();
	}

	/** Убирает путь из обратного индекса `id`. */
	private forgetPath(entry: IndexEntry): void {
		if (!entry.id) {
			return;
		}
		const paths = this.pathsById.get(entry.id);
		if (!paths) {
			return;
		}
		paths.delete(entry.path);
		if (paths.size === 0) {
			this.pathsById.delete(entry.id);
		}
	}
}

/**
 * Полный проход: строит индекс по переданным файлам.
 *
 * Файлы обрабатываются в порядке сортировки путей, чтобы результат не зависел от порядка
 * выдачи файловой системы, а выбор записи при нарушении INV-02 был детерминированным.
 * Значения `id` не в форме UUIDv7 (INV-01) записью не принимаются (см. `normalizeEntry`):
 * файл остаётся доступным по пути и получает `kind: "partial"`.
 */
export function indexFiles(files: Iterable<ScannedFile>): VaultIndex {
	const index = new VaultIndex();
	const sorted = [...files].sort((a, b) => (a.path < b.path ? -1 : a.path > b.path ? 1 : 0));
	for (const file of sorted) {
		index.upsert(normalizeEntry(file.path, file.text));
	}
	return index;
}
