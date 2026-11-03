/**
 * title-dom.ts — низкоуровневые операции подмены текста в элементах интерфейса Obsidian
 * (iter-015, DL-053, DL-054).
 *
 * Модуль не импортирует `obsidian` и не знает о конкретном устройстве проводника или
 * вкладок: он умеет записать текст в элемент, запомнить исходный текст и вернуть его
 * обратно. Поверхности (`explorer-title.ts`, `leaf-title.ts`) поставляют пары
 * «элемент → путь», решение о подмене принимает `display-title.ts` (§3 контракта).
 *
 * Подмена обратима: исходный текст и исходная подсказка хранятся в `data-*` атрибутах
 * элемента, поэтому выключение настройки, перезапуск плагина и `onunload` возвращают
 * интерфейс в состояние, близкое к stock Obsidian (TASK iter-015, DoD 3). Файлы не
 * переименовываются и содержимое заметок не изменяется (§3.2).
 */

/** Атрибут с исходным текстом элемента до подмены. */
export const ORIGINAL_TEXT_ATTR = "data-sbpk-original-title";

/** Атрибут с исходной подсказкой (`title`) элемента до пометки об ошибке. */
export const ORIGINAL_TOOLTIP_ATTR = "data-sbpk-original-tooltip";

/** Признак того, что текст элемента подменён плагином. */
export const PATCHED_ATTR = "data-sbpk-title";

/**
 * Класс пометки о нарушении INV-07 (§3.5.2): объект модели без `title` отображается
 * именем файла и помечается. Визуальное оформление — `plugin/styles.css`.
 */
export const ERROR_CLASS = "sbpk-title-error";

/**
 * Решение о подмене для одного пути.
 * `text: null` — поверхность остаётся в исходном состоянии (файл вне модели, подмена
 * выключена или `title` совпадает с именем файла); `error` — текст пометки о нарушении
 * INV-07, которая показывается и без подмены имени (§3.5.2).
 */
export interface TitleDecision {
	text: string | null;
	error?: string;
}

/** Функция, возвращающая решение о подмене по пути файла относительно корня хранилища. */
export type TitleResolver = (path: string) => TitleDecision;

/** Пара «элемент интерфейса → путь файла», которому элемент соответствует. */
export interface TitleTarget {
	el: HTMLElement;
	path: string;
}

/** Исход подмены для одного элемента. */
export type ApplyOutcome = "applied" | "restored" | "unchanged";

/** Сводка прохода по набору целей. */
export interface ApplyStats {
	applied: number;
	restored: number;
	unchanged: number;
}

/** Текст элемента; `null` в DOM трактуется как пустая строка. */
export function textOf(el: HTMLElement): string {
	return el.textContent ?? "";
}

/**
 * Записывает текст только если он отличается от текущего: повторные проходы не создают
 * новых мутаций DOM, поэтому наблюдатель за проводником не входит в цикл (DL-054).
 */
export function setText(el: HTMLElement, text: string): boolean {
	if (textOf(el) === text) {
		return false;
	}
	el.textContent = text;
	return true;
}

/** Подменён ли текст элемента плагином. */
export function isPatched(el: HTMLElement): boolean {
	return el.getAttribute(PATCHED_ATTR) === "1";
}

/** Запоминает исходный текст элемента перед первой подменой. */
export function markOriginal(el: HTMLElement): void {
	if (el.getAttribute(ORIGINAL_TEXT_ATTR) === null) {
		el.setAttribute(ORIGINAL_TEXT_ATTR, textOf(el));
	}
}

/** Ставит признак подмены. */
export function markPatched(el: HTMLElement): void {
	el.setAttribute(PATCHED_ATTR, "1");
}

/**
 * Возвращает элементу исходный текст и снимает признак подмены.
 * Возвращает `true`, если текст действительно восстанавливался.
 */
export function restoreElement(el: HTMLElement): boolean {
	const original = el.getAttribute(ORIGINAL_TEXT_ATTR);
	if (original === null) {
		el.removeAttribute(PATCHED_ATTR);
		return false;
	}
	const written = setText(el, original);
	el.removeAttribute(ORIGINAL_TEXT_ATTR);
	el.removeAttribute(PATCHED_ATTR);
	return written;
}

/**
 * Ставит или снимает пометку о нарушении INV-07 (§3.5.2): класс `sbpk-title-error`
 * и подсказка с текстом нарушения. Исходная подсказка элемента сохраняется и
 * возвращается при снятии пометки.
 */
export function setErrorMark(el: HTMLElement, note: string | undefined): void {
	if (note === undefined) {
		el.classList.remove(ERROR_CLASS);
		const original = el.getAttribute(ORIGINAL_TOOLTIP_ATTR);
		if (original !== null) {
			if (original === "") {
				el.removeAttribute("title");
			} else {
				el.setAttribute("title", original);
			}
			el.removeAttribute(ORIGINAL_TOOLTIP_ATTR);
		}
		return;
	}
	el.classList.add(ERROR_CLASS);
	if (el.getAttribute(ORIGINAL_TOOLTIP_ATTR) === null) {
		el.setAttribute(ORIGINAL_TOOLTIP_ATTR, el.getAttribute("title") ?? "");
	}
	if (el.getAttribute("title") !== note) {
		el.setAttribute("title", note);
	}
}

/** Подменяет текст одного элемента или возвращает его в исходное состояние. */
export function applyTarget(target: TitleTarget, resolve: TitleResolver): ApplyOutcome {
	const decision = resolve(target.path);
	if (decision.text !== null) {
		markOriginal(target.el);
		const written = setText(target.el, decision.text);
		markPatched(target.el);
		setErrorMark(target.el, decision.error);
		return written ? "applied" : "unchanged";
	}
	const restored = restoreElement(target.el);
	setErrorMark(target.el, decision.error);
	return restored ? "restored" : "unchanged";
}

/** Проход по набору целей: идемпотентен, повторный вызов без изменений даёт `unchanged`. */
export function applyTargets(targets: Iterable<TitleTarget>, resolve: TitleResolver): ApplyStats {
	const stats: ApplyStats = { applied: 0, restored: 0, unchanged: 0 };
	for (const target of targets) {
		stats[applyTarget(target, resolve)]++;
	}
	return stats;
}

/** Восстанавливает исходный текст и снимает пометки у всех переданных элементов. */
export function restoreTargets(elements: Iterable<HTMLElement>): number {
	let restored = 0;
	for (const el of elements) {
		if (restoreElement(el)) {
			restored++;
		}
		setErrorMark(el, undefined);
	}
	return restored;
}
