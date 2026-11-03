/**
 * explorer-title.ts — подмена отображаемого имени в проводнике файлов (§3.1, пункт 2;
 * iter-015, DL-053, DL-054).
 *
 * Публичного API для текста элемента проводника нет, поэтому текст записывается напрямую
 * в элемент списка, а повторное применение выполняет наблюдатель за поддеревом: Obsidian
 * перерисовывает строки при прокрутке, сортировке, переименовании и смене темы.
 *
 * Элементы берутся из внутреннего представления проводника (`fileItems` — Obsidian до 1.7,
 * `treeView.itemMap` / `treeView.items` — новее), а при их отсутствии — из DOM по атрибуту
 * `data-path`. Обращения к внутренним полям защищены проверками: при изменении разметки
 * подмена молча отключится, плагин продолжит работать (DL-054). Модуль не импортирует
 * `obsidian` и проверяется вне приложения (`tools/title-surface-harness.cjs`, группа H).
 */

import type { TitleResolver, TitleTarget } from "./title-dom";
import { applyTargets, restoreTargets, type ApplyStats } from "./title-dom";

/** Задержка антидребезга наблюдателя: перерисовка проводника идёт пачками мутаций. */
const REFRESH_DELAY_MS = 120;

/** Селектор строки файла в проводнике (классическая разметка). */
export const NAV_FILE_TITLE_SELECTOR = ".nav-file-title";

/** Селектор строки файла в представлениях на дереве (разметка Obsidian 1.4+). */
export const TREE_ITEM_SELECTOR = ".tree-item-self";

/** Селекторы элемента с текстом имени внутри строки файла. */
export const TITLE_CONTENT_SELECTORS: readonly string[] = [".nav-file-title-content", ".tree-item-inner"];

/** Атрибут строки проводника с путём файла относительно корня хранилища. */
export const PATH_ATTR = "data-path";

/** Тип представления проводника во внутреннем API Obsidian. */
export const FILE_EXPLORER_VIEW_TYPE = "file-explorer";

/** Элемент списка проводника (`FileExplorerItem`), duck-typed. */
export interface ExplorerItemLike {
	file?: { path?: string } | null;
	titleEl?: HTMLElement | null;
	titleInnerEl?: HTMLElement | null;
	selfEl?: HTMLElement | null;
}

/** Представление проводника (`FileExplorerView`), duck-typed. */
export interface ExplorerViewLike {
	fileItems?: Record<string, ExplorerItemLike> | null;
	treeView?: ExplorerTreeViewLike | null;
	containerEl?: HTMLElement | null;
}

/** Дерево элементов проводника в новых версиях Obsidian, duck-typed. */
export interface ExplorerTreeViewLike {
	itemMap?: Record<string, ExplorerItemLike> | null;
	items?: ArrayLike<ExplorerItemLike> | null;
}

/** Поставщик представлений проводника: контроллер передаёт сюда `getLeavesOfType`. */
export type ViewsProvider = () => unknown[];

/** Сводка состояния патчера проводника. */
export interface ExplorerStats {
	views: number;
	observers: number;
	targets: number;
}

function isElement(value: unknown): value is HTMLElement {
	return typeof value === "object" && value !== null && typeof (value as HTMLElement).getAttribute === "function";
}

/** Путь файла элемента проводника; `null`, если путь неизвестен. */
export function pathOfItem(item: ExplorerItemLike | null | undefined): string | null {
	const path = item?.file?.path;
	return typeof path === "string" && path.length > 0 ? path : null;
}

/**
 * Элемент, в который записывается имя: внутренний элемент с текстом, если он есть,
 * иначе сама строка списка. Запись в строку целиком сломала бы значок файла, поэтому
 * при отсутствии внутреннего элемента текст не подменяется.
 */
export function titleElementOf(item: ExplorerItemLike | null | undefined): HTMLElement | null {
	if (!item) {
		return null;
	}
	if (isElement(item.titleInnerEl)) {
		return item.titleInnerEl;
	}
	const titleEl = isElement(item.titleEl) ? item.titleEl : isElement(item.selfEl) ? item.selfEl : null;
	if (!titleEl) {
		return null;
	}
	for (const selector of TITLE_CONTENT_SELECTORS) {
		const inner = titleEl.querySelector<HTMLElement>(selector);
		if (isElement(inner)) {
			return inner;
		}
	}
	return null;
}

/** Элементы из карты «путь → элемент» (`fileItems` или `treeView.itemMap`). */
export function itemsFromMap(map: Record<string, ExplorerItemLike> | null | undefined): ExplorerItemLike[] {
	if (!map || typeof map !== "object") {
		return [];
	}
	const items: ExplorerItemLike[] = [];
	for (const key of Object.keys(map)) {
		const item = map[key];
		if (item && typeof item === "object") {
			items.push(item);
		}
	}
	return items;
}

/**
 * Элементы из DOM проводника: строки файла с атрибутом `data-path`. Используется как
 * запасной путь, когда внутреннее представление недоступно или ещё не заполнено.
 */
export function collectDomItems(root: HTMLElement | null | undefined): ExplorerItemLike[] {
	if (!isElement(root)) {
		return [];
	}
	const items: ExplorerItemLike[] = [];
	const seen = new Set<HTMLElement>();
	for (const selector of [NAV_FILE_TITLE_SELECTOR, TREE_ITEM_SELECTOR]) {
		const found = root.querySelectorAll<HTMLElement>(selector);
		for (let i = 0; i < found.length; i++) {
			const el = found[i];
			if (!isElement(el) || seen.has(el)) {
				continue;
			}
			const path = el.getAttribute(PATH_ATTR);
			if (!path) {
				continue;
			}
			seen.add(el);
			items.push({ file: { path }, titleEl: el });
		}
	}
	return items;
}

/** Является ли значение представлением проводника. */
export function isExplorerView(value: unknown): value is ExplorerViewLike {
	if (typeof value !== "object" || value === null) {
		return false;
	}
	const view = value as ExplorerViewLike;
	return view.fileItems != null || view.treeView != null || isElement(view.containerEl);
}

/**
 * Элементы проводника из всех доступных источников: внутреннее представление (карта или
 * список), затем DOM.
 */
export function collectItems(view: unknown): ExplorerItemLike[] {
	if (!isExplorerView(view)) {
		return [];
	}
	let items = itemsFromMap(view.fileItems);
	const tree = view.treeView;
	if (items.length === 0 && tree) {
		items = itemsFromMap(tree.itemMap);
		if (items.length === 0 && tree.items) {
			for (let i = 0; i < tree.items.length; i++) {
				const item = tree.items[i];
				if (item && typeof item === "object") {
					items.push(item);
				}
			}
		}
	}
	if (items.length === 0) {
		items = collectDomItems(view.containerEl);
	}
	return items;
}

/** Цели подмены для одного представления проводника. */
export function collectTargets(view: unknown): TitleTarget[] {
	const targets: TitleTarget[] = [];
	const seen = new Set<HTMLElement>();
	for (const item of collectItems(view)) {
		const path = pathOfItem(item);
		const el = titleElementOf(item);
		if (!path || !el || seen.has(el)) {
			continue;
		}
		seen.add(el);
		targets.push({ el, path });
	}
	return targets;
}

/**
 * Патчер проводника: наблюдатели за поддеревом каждого представления и подмена при
 * перерисовке. Список представлений запрашивается на каждом проходе, поэтому закрытие и
 * повторное открытие проводника не требует переподключения.
 */
export class ExplorerTitlePatcher {
	private readonly resolve: TitleResolver;

	private readonly viewsProvider: ViewsProvider;

	private readonly observers = new Map<HTMLElement, MutationObserver>();

	private targets: TitleTarget[] = [];

	private timer: ReturnType<typeof setTimeout> | null = null;

	constructor(resolve: TitleResolver, viewsProvider: ViewsProvider) {
		this.resolve = resolve;
		this.viewsProvider = viewsProvider;
	}

	/** Представления проводника, найденные в рабочем пространстве. */
	private views(): ExplorerViewLike[] {
		const found = this.viewsProvider();
		const views: ExplorerViewLike[] = [];
		for (const view of Array.isArray(found) ? found : []) {
			if (isExplorerView(view)) {
				views.push(view);
			}
		}
		return views;
	}

	/** Применяет подмену ко всем найденным представлениям; идемпотентно. */
	refresh(): ApplyStats {
		const views = this.views();
		this.targets = [];
		for (const view of views) {
			this.observe(view.containerEl);
			for (const target of collectTargets(view)) {
				this.targets.push(target);
			}
		}
		this.pruneObservers(views);
		return applyTargets(this.targets, this.resolve);
	}

	/** Восстанавливает исходные имена, останавливает наблюдателей. */
	detach(): number {
		if (this.timer !== null) {
			clearTimeout(this.timer);
			this.timer = null;
		}
		for (const observer of this.observers.values()) {
			observer.disconnect();
		}
		this.observers.clear();
		const restored = restoreTargets(this.targets.map((target) => target.el));
		this.targets = [];
		return restored;
	}

	stats(): ExplorerStats {
		return { views: this.views().length, observers: this.observers.size, targets: this.targets.length };
	}

	/** Наблюдатель за поддеревом проводника: перерисовка строки возвращает stock-имя. */
	private observe(root: HTMLElement | null | undefined): void {
		if (!isElement(root) || this.observers.has(root) || typeof MutationObserver === "undefined") {
			return;
		}
		const observer = new MutationObserver(() => this.schedule());
		observer.observe(root, { childList: true, subtree: true, characterData: true });
		this.observers.set(root, observer);
	}

	/** Снимает наблюдателей с представлений, которых больше нет в рабочем пространстве. */
	private pruneObservers(views: ExplorerViewLike[]): void {
		const alive = new Set<HTMLElement>();
		for (const view of views) {
			if (isElement(view.containerEl)) {
				alive.add(view.containerEl);
			}
		}
		for (const root of Array.from(this.observers.keys())) {
			if (!alive.has(root)) {
				this.observers.get(root)?.disconnect();
				this.observers.delete(root);
			}
		}
	}

	/** Откладывает повторный проход, чтобы не применять подмену на каждой мутации. */
	private schedule(): void {
		if (this.timer !== null) {
			return;
		}
		this.timer = setTimeout(() => {
			this.timer = null;
			this.refresh();
		}, REFRESH_DELAY_MS);
	}
}
