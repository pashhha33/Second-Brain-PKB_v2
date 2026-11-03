/**
 * leaf-title.ts — подмена отображаемого имени в заголовках вкладок и заголовке панели
 * (§3.1, пункт 2: «заголовок вкладки»; iter-015, DL-053, DL-054).
 *
 * Два способа, оба минимальные:
 * 1. Обёртка над `getDisplayText()` конкретного экземпляра представления — Obsidian сам
 *    берёт из неё текст вкладки при перерисовке. Прототипы не подменяются, поэтому
 *    остальные представления и другие плагины не затрагиваются (DL-054).
 * 2. Запись текста в DOM сразу: элемент заголовка вкладки (`.workspace-tab-header-inner-title`)
 *    и заголовок панели (`.view-header-title`). Заголовок вкладки ищется по индексу листа
 *    среди соседей по группе — это единственная доступная связь, поэтому при изменении
 *    разметки способ 2 отключается, а способ 1 продолжает работать.
 *
 * Не подменяется `.inline-title`: этот элемент редактируется и его изменение
 *    переименовывает файл, что нарушает §3.2 (файл не переименовывается).
 *
 * Модуль не импортирует `obsidian` в рантайме (только типы), поэтому проверяется
 * вне приложения (`tools/title-leaf-harness.cjs`, группа I).
 */

import type { TitleResolver, TitleTarget } from "./title-dom";
import { applyTargets, restoreTargets } from "./title-dom";

/** Контейнер заголовков вкладок группы. */
export const TAB_HEADER_CONTAINER_SELECTOR = ".workspace-tab-header-container";

/** Заголовок одной вкладки. */
export const TAB_HEADER_SELECTOR = ".workspace-tab-header";

/** Элемент с текстом в заголовке вкладки. */
export const TAB_TITLE_SELECTOR = ".workspace-tab-header-inner-title";

/** Заголовок панели (лист) с именем файла. */
export const PANE_TITLE_SELECTOR = ".view-header-title";

/** Представление листа (`View` / `FileView`), duck-typed. */
export interface LeafViewLike {
	file?: { path?: string } | null;
	getDisplayText?: () => string;
}

/** Лист рабочего пространства (`WorkspaceLeaf`), duck-typed. */
export interface LeafLike {
	containerEl?: HTMLElement | null;
	view?: LeafViewLike | null;
}

const originals = new Map<LeafViewLike, () => string>();

/** Путь файла листа; `null`, если лист не показывает файл. */
export function leafPathOf(leaf: LeafLike | null | undefined): string | null {
	const path = leaf?.view?.file?.path;
	return typeof path === "string" && path.length > 0 ? path : null;
}

function isElement(value: unknown): value is HTMLElement {
	return typeof value === "object" && value !== null && typeof (value as HTMLElement).querySelector === "function";
}

/**
 * Заголовок вкладки для листа: листы и заголовки идут в одном порядке внутри группы,
 * поэтому связь устанавливается по индексу листа среди соседей (DL-054).
 */
export function tabHeaderOf(leaf: LeafLike | null | undefined): HTMLElement | null {
	const container = leaf?.containerEl;
	if (!isElement(container)) {
		return null;
	}
	const tabContainer = container.parentElement;
	const tabs = tabContainer?.parentElement ?? null;
	if (!tabContainer || !isElement(tabs)) {
		return null;
	}
	const headerContainer = tabs.querySelector<HTMLElement>(TAB_HEADER_CONTAINER_SELECTOR);
	if (!isElement(headerContainer)) {
		return null;
	}
	const headers = headerContainer.querySelectorAll<HTMLElement>(TAB_HEADER_SELECTOR);
	const leaves = tabContainer.children;
	let index = -1;
	for (let i = 0; i < leaves.length; i++) {
		if (leaves[i] === container) {
			index = i;
			break;
		}
	}
	if (index < 0 || index >= headers.length) {
		return null;
	}
	const header = headers[index];
	return isElement(header) ? header : null;
}

/** Элемент с текстом внутри заголовка вкладки; при отсутствии — сам заголовок. */
export function tabTitleElementOf(header: HTMLElement | null): HTMLElement | null {
	if (!isElement(header)) {
		return null;
	}
	const inner = header.querySelector<HTMLElement>(TAB_TITLE_SELECTOR);
	return isElement(inner) ? inner : header;
}

/** Заголовок панели листа, если он есть в разметке. */
export function paneTitleElementOf(leaf: LeafLike | null | undefined): HTMLElement | null {
	const container = leaf?.containerEl;
	if (!isElement(container)) {
		return null;
	}
	const title = container.querySelector<HTMLElement>(PANE_TITLE_SELECTOR);
	return isElement(title) ? title : null;
}

/** Цели подмены для одного листа: текст вкладки и заголовок панели. */
export function collectTargets(leaf: LeafLike | null | undefined): TitleTarget[] {
	const path = leafPathOf(leaf);
	if (!path) {
		return [];
	}
	const targets: TitleTarget[] = [];
	const seen = new Set<HTMLElement>();
	for (const el of [tabTitleElementOf(tabHeaderOf(leaf)), paneTitleElementOf(leaf)]) {
		if (el && !seen.has(el)) {
			seen.add(el);
			targets.push({ el, path });
		}
	}
	return targets;
}

/**
 * Оборачивает `getDisplayText()` представления листа: Obsidian берёт из неё текст
 * вкладки при перерисовке, поэтому подмена сохраняется после смены файла в листе.
 * Повторный вызов для того же представления ничего не меняет.
 */
export function wrapDisplayText(leaf: LeafLike | null | undefined, resolve: TitleResolver): boolean {
	const view = leaf?.view;
	if (!view || typeof view.getDisplayText !== "function" || originals.has(view)) {
		return false;
	}
	const original = view.getDisplayText.bind(view) as () => string;
	originals.set(view, original);
	view.getDisplayText = (): string => {
		const path = leafPathOf(leaf);
		if (path === null) {
			return original();
		}
		return resolve(path).text ?? original();
	};
	return true;
}

/** Снимает обёртку с представления листа, возвращая исходный `getDisplayText`. */
export function unwrapDisplayText(leaf: LeafLike | null | undefined): boolean {
	const view = leaf?.view;
	if (!view) {
		return false;
	}
	const original = originals.get(view);
	if (original === undefined) {
		return false;
	}
	view.getDisplayText = original;
	originals.delete(view);
	return true;
}

/** Число представлений с активной обёрткой — для диагностики и панели настроек. */
export function wrappedCount(): number {
	return originals.size;
}

/** Снимает обёртки со всех представлений, которые обёрнуты этим плагином. */
export function unwrapAll(): number {
	let count = 0;
	for (const [view, original] of Array.from(originals.entries())) {
		view.getDisplayText = original;
		originals.delete(view);
		count++;
	}
	return count;
}

/**
 * Проход по всем листам рабочего пространства: ставит обёртки `getDisplayText`
 * и применяет подмену к заголовкам, которые уже есть в DOM.
 */
export function refreshLeaves(
	leaves: Iterable<LeafLike>,
	resolve: TitleResolver,
): { wrapped: number; targets: TitleTarget[] } {
	let wrapped = 0;
	const targets: TitleTarget[] = [];
	for (const leaf of leaves) {
		if (wrapDisplayText(leaf, resolve)) {
			wrapped++;
		}
		for (const target of collectTargets(leaf)) {
			targets.push(target);
		}
	}
	applyTargets(targets, resolve);
	return { wrapped, targets };
}

/** Восстанавливает заголовки листов и снимает обёртки `getDisplayText`. */
export function restoreLeaves(targets: Iterable<TitleTarget>): { restored: number; unwrapped: number } {
	const elements: HTMLElement[] = [];
	for (const target of targets) {
		elements.push(target.el);
	}
	return { restored: restoreTargets(elements), unwrapped: unwrapAll() };
}
