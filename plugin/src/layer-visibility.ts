/**
 * layer-visibility.ts — видимость слоёв модели: стаб контракта §2
 * (`docs/metamodel/10-plugin-ux-contracts.md`, ADR-008, U1, DL-031).
 *
 * Контракт: три глобальных тумблера по значению `layer` (INV-09); состояние хранится
 * в настройках плагина и в данные объектов не записывается (§2.1). Состояние по умолчанию —
 * `content` и `classification` видимы, `system` скрыт (§2.3). Три канонических пресета
 * переключаются одной командой (§2.2). Файлы, не являющиеся объектами модели, ни к одному
 * слою не относятся и тумблерами не скрываются (§2.5.3).
 *
 * Границы v1: модуль хранит состояние и отвечает на вопрос о видимости, но не фильтрует
 * проводник — фильтрация поиска и графа выполняется в фазе 5 (вне scope iter-014).
 * Модуль чистый: не импортирует `obsidian`.
 *
 * Здесь же живёт единое хранилище настроек плагина `PluginSettings`: оно собирает части
 * по темам — видимость слоёв (§2) и подмену отображаемого имени (§3, iter-015, DL-053),
 * поэтому настройка подмены объявлена в `display-title.ts`, а не в этом модуле.
 */

import {
	DEFAULT_DISPLAY_TITLE_SETTINGS,
	normalizeDisplayTitleSettings,
	type DisplayTitleSettings,
} from "./display-title";
import type { IndexEntry, ModelLayer } from "./types";
import { MODEL_LAYERS } from "./types";

/** Состояние трёх тумблеров видимости (§2.1). */
export interface LayerVisibility {
	system: boolean;
	classification: boolean;
	content: boolean;
}

/** Идентификатор канонического пресета (§2.2). */
export type PresetId = "knowledge-only" | "model" | "all";

/** Пользовательский пресет: хранится в настройках плагина, объектом модели не является (§2.2). */
export interface CustomPreset {
	id: string;
	label: string;
	visibility: LayerVisibility;
}

/** Описание пресета — канонического или пользовательского. */
export interface Preset {
	id: string;
	label: string;
	visibility: LayerVisibility;
	canonical: boolean;
}

/**
 * Настройки плагина: видимость слоёв, активный пресет, пользовательские пресеты
 * и подмена отображаемого имени. Хранятся в `data.json` плагина и в данные объектов
 * не попадают (§2.1, §3; DL-031, DL-053).
 */
export interface PluginSettings {
	layerVisibility: LayerVisibility;
	/** Идентификатор пресета, применённого последним, либо `null`, если тумблеры менялись вручную. */
	activePreset: string | null;
	customPresets: CustomPreset[];
	/** §3: feature-flag «Подменять имя на title» (iter-015, DL-053). */
	displayTitle: DisplayTitleSettings;
}

/** §2.3: состояние по умолчанию — `content` и `classification` видимы, `system` скрыт. */
export const DEFAULT_LAYER_VISIBILITY: LayerVisibility = {
	system: false,
	classification: true,
	content: true,
};

/** Настройки по умолчанию при первом запуске (§2.3). */
export const DEFAULT_SETTINGS: PluginSettings = {
	layerVisibility: { ...DEFAULT_LAYER_VISIBILITY },
	activePreset: null,
	customPresets: [],
	displayTitle: { ...DEFAULT_DISPLAY_TITLE_SETTINGS },
};

/** Три канонических пресета (§2.2): доступны всегда и не удаляются. */
export const CANONICAL_PRESETS: readonly Preset[] = [
	{
		id: "knowledge-only",
		label: "Только знания",
		visibility: { system: false, classification: false, content: true },
		canonical: true,
	},
	{
		id: "model",
		label: "Модель",
		visibility: { system: true, classification: true, content: false },
		canonical: true,
	},
	{ id: "all", label: "Всё", visibility: { system: true, classification: true, content: true }, canonical: true },
];

/** Видим ли указанный слой при текущем состоянии тумблеров. */
export function isLayerVisible(visibility: LayerVisibility, layer: ModelLayer): boolean {
	return visibility[layer];
}

/**
 * Видима ли запись индекса (§2.5.3): файлы вне модели — без явного `layer` — не скрываются.
 * Скрытие слоя не является способом вывести объект из модели: для этого предназначены
 * `status: deprecated` и удаление файла владельцем (§2.5.4).
 */
export function isEntryVisible(entry: IndexEntry | undefined, visibility: LayerVisibility): boolean {
	if (!entry || !entry.layer) {
		return true;
	}
	return isLayerVisible(visibility, entry.layer);
}

/** Все пресеты — канонические и пользовательские (§2.2). */
export function allPresets(settings: PluginSettings): Preset[] {
	return [
		...CANONICAL_PRESETS,
		...settings.customPresets.map((preset) => ({
			id: preset.id,
			label: preset.label,
			visibility: preset.visibility,
			canonical: false,
		})),
	];
}

/** Пресет по идентификатору либо `undefined`. */
export function findPreset(settings: PluginSettings, id: string): Preset | undefined {
	return allPresets(settings).find((preset) => preset.id === id);
}

/** Идентификатор пресета, совпадающего с текущим состоянием тумблеров, либо `null`. */
export function matchingPreset(settings: PluginSettings): string | null {
	const found = allPresets(settings).find((preset) =>
		MODEL_LAYERS.every((layer) => preset.visibility[layer] === settings.layerVisibility[layer]),
	);
	return found ? found.id : null;
}

/** Применяет пресет (§2.2): возвращает новые настройки, не изменяя переданные. */
export function applyPreset(settings: PluginSettings, id: string): PluginSettings {
	const preset = findPreset(settings, id);
	if (!preset) {
		return settings;
	}
	return { ...settings, layerVisibility: { ...preset.visibility }, activePreset: preset.id };
}

/** Меняет один тумблер (§2.1); активный пресет сбрасывается, если состояние ему больше не равно. */
export function setLayerVisible(settings: PluginSettings, layer: ModelLayer, visible: boolean): PluginSettings {
	const next: PluginSettings = {
		...settings,
		layerVisibility: { ...settings.layerVisibility, [layer]: visible },
		activePreset: null,
	};
	next.activePreset = matchingPreset(next);
	return next;
}

/**
 * Включает или выключает подмену отображаемого имени (§3, DL-053). На активный пресет
 * видимости не влияет: это независимая настройка.
 */
export function setDisplayTitleOverride(settings: PluginSettings, override: boolean): PluginSettings {
	return { ...settings, displayTitle: { ...settings.displayTitle, override } };
}

/** Команда «восстановить видимость по умолчанию» (§2.3). */
export function resetToDefault(settings: PluginSettings): PluginSettings {
	const next: PluginSettings = {
		...settings,
		layerVisibility: { ...DEFAULT_LAYER_VISIBILITY },
		activePreset: null,
	};
	next.activePreset = matchingPreset(next);
	return next;
}

/**
 * Приводит данные, прочитанные из `loadData()`, к настройкам: недостающие поля берутся
 * из значений по умолчанию, неизвестные значения `layer` игнорируются. Миграция версий
 * не требуется: ключ `displayTitle`, добавленный в iter-015, при отсутствии заполняется
 * значением по умолчанию (подмена включена).
 */
export function normalizeSettings(loaded: unknown): PluginSettings {
	if (!loaded || typeof loaded !== "object") {
		return {
			...DEFAULT_SETTINGS,
			layerVisibility: { ...DEFAULT_LAYER_VISIBILITY },
			customPresets: [],
			displayTitle: { ...DEFAULT_DISPLAY_TITLE_SETTINGS },
		};
	}
	const source = loaded as Partial<PluginSettings>;
	const visibility: LayerVisibility = { ...DEFAULT_LAYER_VISIBILITY };
	const loadedVisibility = source.layerVisibility;
	if (loadedVisibility && typeof loadedVisibility === "object") {
		for (const layer of MODEL_LAYERS) {
			if (typeof loadedVisibility[layer] === "boolean") {
				visibility[layer] = loadedVisibility[layer];
			}
		}
	}
	const customPresets = Array.isArray(source.customPresets)
		? source.customPresets.filter(
				(preset): preset is CustomPreset =>
					!!preset &&
					typeof preset.id === "string" &&
					typeof preset.label === "string" &&
					!!preset.visibility &&
					typeof preset.visibility === "object",
			)
		: [];
	const settings: PluginSettings = {
		layerVisibility: visibility,
		activePreset: typeof source.activePreset === "string" ? source.activePreset : null,
		customPresets,
		displayTitle: normalizeDisplayTitleSettings(source.displayTitle),
	};
	if (!settings.activePreset) {
		settings.activePreset = matchingPreset(settings);
	}
	return settings;
}
