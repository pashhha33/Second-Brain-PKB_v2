/**
 * main.ts — точка входа плагина Second Brain PKB (фаза 4, каркас).
 *
 * Реализовано в iter-014:
 * - полный проход по `.md` хранилища при `onload` и построение in-memory индекса
 *   (доступ по `id` и по пути), обновление по событиям create / modify / delete / rename;
 * - стаб отображаемого имени `getDisplayTitle(file | path)` (§3 контракта);
 * - стаб видимости слоёв `isLayerVisible(layer)` и `isFileVisible(file | path)` с состоянием
 *   по умолчанию content + classification видимы, system скрыт (§2 контракта);
 * - панель настроек (тумблеры, три канонических пресета, сброс, перестроение индекса) и команды.
 *
 * Не реализовано (фаза 5, вне scope iter-014): подмена имени в проводнике, поиске, вкладках
 * и графе; фильтрация выдачи поиска и узлов графа по тумблерам; создание объектов из пустых
 * ссылок; исполнение 19 правил валидации; bootstrap определений системного слоя.
 *
 * Контракт поведения: `docs/metamodel/10-plugin-ux-contracts.md` (ADR-008, DL-031…DL-034).
 */

import { Notice, Plugin, TAbstractFile, TFile } from "obsidian";
import { getDisplayTitle, getTitleIndicator } from "./display-title";
import {
	applyPreset,
	CANONICAL_PRESETS,
	DEFAULT_SETTINGS,
	isEntryVisible,
	isLayerVisible,
	normalizeSettings,
	resetToDefault,
	type PluginSettings,
} from "./layer-visibility";
import { SecondBrainSettingTab } from "./settings-tab";
import type { IndexEntry, IndexStats, ModelLayer, PathLike, ScannedFile } from "./types";
import { indexFiles, VaultIndex } from "./vault-index";

const PLUGIN_NAME = "Second Brain PKB";

export default class SecondBrainPlugin extends Plugin {
	/** Настройки плагина: видимость слоёв, активный пресет, пользовательские пресеты. */
	settings: PluginSettings = { ...DEFAULT_SETTINGS };

	/** Индекс объектов хранилища в памяти. */
	index: VaultIndex = new VaultIndex();

	async onload(): Promise<void> {
		this.settings = normalizeSettings(await this.loadData());
		const stats = await this.rebuildIndex();
		this.registerVaultEvents();
		this.addSettingTab(new SecondBrainSettingTab(this.app, this));
		this.registerCommands();
		console.log(
			`${PLUGIN_NAME}: индекс построен — файлов ${stats.files}, объектов модели ${stats.objects} ` +
				`(system ${stats.byLayer.system}, classification ${stats.byLayer.classification}, ` +
				`content ${stats.byLayer.content})`,
		);
	}

	onunload(): void {
		this.index.clear();
	}

	// ---------------------------------------------------------------- API контрактов

	/**
	 * §3.1, §3.5: отображаемое имя файла — `title` объекта модели, иначе имя файла.
	 * Принимает `TFile` (структурно совместим с `PathLike`) или путь строкой.
	 */
	getDisplayTitle(file: PathLike | string): string {
		return getDisplayTitle(this.index, file);
	}

	/** §3.4: индикатор при совпадении `title` — `label` определения типа или машинный ключ. */
	getTitleIndicator(file: PathLike | string): string | undefined {
		return getTitleIndicator(this.index, this.index.getByFile(file));
	}

	/** §2.1: видим ли слой при текущем состоянии тумблеров. */
	isLayerVisible(layer: ModelLayer): boolean {
		return isLayerVisible(this.settings.layerVisibility, layer);
	}

	/** §2.5.3: видим ли файл — файлы вне модели не скрываются. */
	isFileVisible(file: PathLike | string): boolean {
		return isEntryVisible(this.index.getByFile(file), this.settings.layerVisibility);
	}

	/** Доступ к записи индекса по `id` (INV-02). */
	getById(id: string): IndexEntry | undefined {
		return this.index.getById(id);
	}

	/** Доступ к записи индекса по пути относительно корня хранилища. */
	getByPath(path: string): IndexEntry | undefined {
		return this.index.getByPath(path);
	}

	/** Сводка состояния индекса. */
	stats(): IndexStats {
		return this.index.stats();
	}

	// ---------------------------------------------------------------- настройки

	/** Записывает настройки плагина (состояние тумблеров не попадает в данные объектов, §2.1). */
	async saveSettings(): Promise<void> {
		await this.saveData(this.settings);
	}

	/** Применяет пресет видимости (§2.2) и сохраняет настройки. */
	async applyPreset(id: string): Promise<void> {
		this.settings = applyPreset(this.settings, id);
		await this.saveSettings();
	}

	// ---------------------------------------------------------------- индекс

	/**
	 * Полный проход по заметкам `.md` хранилища (TASK.md iter-014, DoD 2).
	 * Чтение через `cachedRead`: индекс строится на содержимом из кэша хранилища и не
	 * блокирует диск; порядок обхода не важен — `indexFiles` сортирует записи по пути.
	 */
	async rebuildIndex(): Promise<IndexStats> {
		const files = this.app.vault.getMarkdownFiles();
		const scanned: ScannedFile[] = [];
		for (const file of files) {
			scanned.push({ path: file.path, text: await this.app.vault.cachedRead(file) });
		}
		this.index = indexFiles(scanned);
		return this.index.stats();
	}

	/** Инкрементальное обновление индекса по событиям хранилища. */
	private registerVaultEvents(): void {
		this.registerEvent(
			this.app.vault.on("create", (file) => {
				void this.onFileChanged(file);
			}),
		);
		this.registerEvent(
			this.app.vault.on("modify", (file) => {
				void this.onFileChanged(file);
			}),
		);
		this.registerEvent(
			this.app.vault.on("delete", (file) => {
				this.onFileRemoved(file);
			}),
		);
		this.registerEvent(
			this.app.vault.on("rename", (file, oldPath) => {
				this.index.remove(oldPath);
				void this.onFileChanged(file);
			}),
		);
	}

	private async onFileChanged(file: TAbstractFile): Promise<void> {
		if (!(file instanceof TFile) || file.extension !== "md") {
			return;
		}
		this.index.update(file.path, await this.app.vault.cachedRead(file));
	}

	private onFileRemoved(file: TAbstractFile): void {
		this.index.remove(file.path);
	}

	// ---------------------------------------------------------------- команды

	private registerCommands(): void {
		this.addCommand({
			id: "rebuild-index",
			name: "Перестроить индекс объектов",
			callback: () => {
				void this.rebuildIndex().then((stats) => {
					new Notice(`${PLUGIN_NAME}: индекс перестроен — объектов модели ${stats.objects} из ${stats.files} файлов`);
				});
			},
		});

		this.addCommand({
			id: "reset-layer-visibility",
			name: "Восстановить видимость слоёв по умолчанию",
			callback: () => {
				this.settings = resetToDefault(this.settings);
				void this.saveSettings().then(() => {
					new Notice(`${PLUGIN_NAME}: видимость по умолчанию — content и classification видимы, system скрыт`);
				});
			},
		});

		for (const preset of CANONICAL_PRESETS) {
			this.addCommand({
				id: `apply-preset-${preset.id}`,
				name: `Пресет видимости: ${preset.label}`,
				callback: () => {
					void this.applyPreset(preset.id);
				},
			});
		}
	}
}
