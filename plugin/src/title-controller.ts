/**
 * title-controller.ts — координация подмены отображаемого имени в интерфейсе Obsidian
 * (iter-015, DL-053, DL-054).
 *
 * Контроллер владеет двумя поверхностями этой версии — проводником файлов (`explorer-title.ts`)
 * и заголовками вкладок и панелей (`leaf-title.ts`) — и отвечает на три вызова точки
 * входа: включить или выключить подмену по настройке, переприменить её после обновления
 * индекса и снять при выгрузке плагина. Решения о подмене принимаются в чистом модуле
 * `display-title.ts` (§3 контракта), поэтому контроллер не знает ни об индексе,
 * ни о настройках — он получает функцию-резолвер.
 *
 * Отложенные поверхности (§3.1, пункт 2): результаты поиска, quick switcher, подписи
 * узлов графа, панели обратных и исходящих ссылок, всплывающий предпросмотр, поле
 * значения свойства-ссылки и заголовок заметки — DL-053.
 *
 * Модуль не импортирует `obsidian` в рантайме (только типы), поэтому проверяется
 * вне приложения (`tools/title-leaf-harness.cjs`, группа I).
 */

import type { DisplayTitleSettings } from "./display-title";
import { overrideTitleOf, titleErrorNote } from "./display-title";
import { ExplorerTitlePatcher, FILE_EXPLORER_VIEW_TYPE } from "./explorer-title";
import { refreshLeaves, restoreLeaves, wrappedCount, type LeafLike } from "./leaf-title";
import type { TitleDecision, TitleResolver, TitleTarget } from "./title-dom";
import type { IndexEntry } from "./types";

/** Запись индекса в том объёме, в каком её использует резолвер. */
export type IndexEntryLike = IndexEntry;

/** Минимальный срез рабочего пространства Obsidian, нужный контроллеру. */
export interface WorkspaceHost {
	getLeavesOfType(viewType: string): unknown[];
	iterateAllLeaves(callback: (leaf: unknown) => void): void;
}

/** Приложение Obsidian в том объёме, в каком его использует контроллер. */
export interface TitleHost {
	workspace: WorkspaceHost;
}

/** Сводка состояния подмены — для панели настроек и диагностики. */
export interface TitleStats {
	enabled: boolean;
	explorerTargets: number;
	explorerObservers: number;
	leafTargets: number;
	wrappedViews: number;
}

/**
 * Строит резолвер подмены по источникам данных: записи индекса и настройке (§3, DL-053).
 * Логика вынесена из точки входа, чтобы решение о подмене проверялось вне приложения
 * (`tools/title-logic-harness.cjs`, группа G).
 */
export function createTitleResolver(
	getEntry: (path: string) => IndexEntryLike | undefined,
	getSettings: () => DisplayTitleSettings,
): TitleResolver {
	return (path: string): TitleDecision => {
		const settings = getSettings();
		if (!settings.override) {
			return { text: null };
		}
		const entry = getEntry(path);
		return {
			text: overrideTitleOf(entry, path, settings),
			error: titleErrorNote(entry, path),
		};
	};
}

/**
 * Контроллер подмены. Жизненный цикл: `setEnabled(true)` при загрузке плагина,
 * `refresh()` после обновления индекса и при изменении раскладки, `detach()` при
 * выгрузке и при выключении настройки.
 */
export class TitleController {
	private readonly host: TitleHost;

	private readonly resolve: TitleResolver;

	private readonly explorer: ExplorerTitlePatcher;

	private enabled = false;

	private leafTargets: TitleTarget[] = [];

	constructor(host: TitleHost, resolve: TitleResolver) {
		this.host = host;
		this.resolve = resolve;
		this.explorer = new ExplorerTitlePatcher(resolve, () => this.explorerViews());
	}

	/** Включена ли подмена настройкой плагина. */
	isEnabled(): boolean {
		return this.enabled;
	}

	/**
	 * Включает или выключает подмену (feature-flag «Подменять имя на title», DL-053).
	 * Выключение возвращает интерфейсу исходные имена файлов (TASK iter-015, DoD 3).
	 */
	setEnabled(enabled: boolean): void {
		if (enabled === this.enabled) {
			this.refresh();
			return;
		}
		if (enabled) {
			this.enabled = true;
			this.refresh();
			return;
		}
		this.detach();
	}

	/** Переприменяет подмену: после обновления индекса, изменения раскладки, переименования. */
	refresh(): void {
		if (!this.enabled) {
			return;
		}
		this.explorer.refresh();
		const result = refreshLeaves(this.leaves(), this.resolve);
		this.leafTargets = result.targets;
	}

	/** Снимает подмену со всех поверхностей и останавливает наблюдателей. */
	detach(): void {
		this.explorer.detach();
		restoreLeaves(this.leafTargets);
		this.leafTargets = [];
		this.enabled = false;
	}

	/** Сводка состояния подмены: сколько элементов и представлений затронуто. */
	stats(): TitleStats {
		const explorer = this.explorer.stats();
		return {
			enabled: this.enabled,
			explorerTargets: explorer.targets,
			explorerObservers: explorer.observers,
			leafTargets: this.leafTargets.length,
			wrappedViews: wrappedCount(),
		};
	}

	/** Представления проводника файлов, открытые в рабочем пространстве. */
	private explorerViews(): unknown[] {
		const leaves = this.host.workspace.getLeavesOfType(FILE_EXPLORER_VIEW_TYPE);
		const views: unknown[] = [];
		for (const leaf of Array.isArray(leaves) ? leaves : []) {
			const view = (leaf as { view?: unknown } | null)?.view;
			if (view) {
				views.push(view);
			}
		}
		return views;
	}

	/** Все листы рабочего пространства: вкладки, панели, pop-out окна. */
	private leaves(): LeafLike[] {
		const found: LeafLike[] = [];
		this.host.workspace.iterateAllLeaves((leaf) => {
			if (leaf && typeof leaf === "object") {
				found.push(leaf as LeafLike);
			}
		});
		return found;
	}
}
