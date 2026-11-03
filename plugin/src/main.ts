/**
 * main.ts — точка входа плагина Second Brain PKB (фазы 4–5).
 *
 * Реализовано в iter-014:
 * - полный проход по `.md` хранилища при `onload` и построение in-memory индекса
 *   (доступ по `id` и по пути), обновление по событиям create / modify / delete / rename;
 * - отображаемое имя `getDisplayTitle(file | path)` и видимость слоёв `isLayerVisible(layer)`,
 *   `isFileVisible(file | path)` с состоянием по умолчанию content + classification видимы,
 *   system скрыт (§2 и §3 контракта);
 * - панель настроек (тумблеры, три канонических пресета, сброс, перестроение индекса) и команды.
 *
 * Реализовано в iter-015 (DL-053, DL-054):
 * - подмена отображаемого имени в проводнике файлов и в заголовках вкладок и панелей
 *   (`TitleController`), с feature-flag «Подменять имя на title» (по умолчанию включён);
 * - переприменение подмены после обновления индекса и при изменении раскладки;
 * - снятие подмены при выключении настройки и при выгрузке плагина.
 *
 * Не реализовано: подмена имени в поиске, quick switcher, графе, панелях ссылок,
 * предпросмотре и заголовке заметки (DL-053); фильтрация выдачи поиска и узлов графа
 * по тумблерам; создание объектов из пустых ссылок; исполнение 19 правил валидации;
 * bootstrap определений системного слоя.
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
	setDisplayTitleOverride as setDisplayTitleSetting,
	type PluginSettings,
} from "./layer-visibility";
import { SecondBrainSettingTab } from "./settings-tab";
import { createTitleResolver, TitleController, type TitleHost, type TitleStats } from "./title-controller";
import type { IndexEntry, IndexStats, ModelLayer, PathLike, ScannedFile } from "./types";
import { indexFiles, VaultIndex } from "./vault-index";

const PLUGIN_NAME = "Second Brain PKB";

export default class SecondBrainPlugin extends Plugin {
	/** Настройки плагина: видимость слоёв, активный пресет, пользовательские пресеты. */
	settings: PluginSettings = { ...DEFAULT_SETTINGS };

	/** Индекс объектов хранилища в памяти. */
	index: VaultIndex = new VaultIndex();

	/** Контроллер подмены отображаемого имени в интерфейсе (iter-015, DL-053). */
	private titleController: TitleController | null = null;

	async onload(): Promise<void> {
		this.settings = normalizeSettings(await this.loadData());
		const stats = await this.rebuildIndex();
		this.registerVaultEvents();
		this.registerWorkspaceEvents();
		this.addSettingTab(new SecondBrainSettingTab(this.app, this));
		this.registerCommands();
		this.titles().setEnabled(this.settings.displayTitle.override);
		console.log(
			`${PLUGIN_NAME}: индекс построен — файлов ${stats.files}, объектов модели ${stats.objects} ` +
				`(system ${stats.byLayer.system}, classification ${stats.byLayer.classification}, ` +
				`content ${stats.byLayer.content})`,
		);
	}

	onunload(): void {
		this.titleController?.detach();
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

	/** §3: включена ли подмена отображаемого имени и сколько элементов затронуто. */
	titleStats(): TitleStats {
		return this.titles().stats();
	}

	/** §3: переприменяет подмену отображаемого имени на обеих поверхностях. */
	refreshDisplayTitles(): void {
		this.titles().refresh();
	}

	/** §3: включает или выключает подмену отображаемого имени (feature-flag, DL-053). */
	async setDisplayTitleOverride(override: boolean): Promise<void> {
		this.settings = setDisplayTitleSetting(this.settings, override);
		await this.saveSettings();
		this.titles().setEnabled(override);
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
		this.titleController?.refresh();
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
		this.titleController?.refresh();
	}

	private onFileRemoved(file: TAbstractFile): void {
		this.index.remove(file.path);
		this.titleController?.refresh();
	}

	/**
	 * События рабочего пространства: при изменении раскладки и при открытии файла
	 * Obsidian перерисовывает заголовки вкладок и строки проводника, поэтому подмену
	 * нужно переприменить (TASK iter-015: устойчивость к переименованию и правке frontmatter).
	 */
	private registerWorkspaceEvents(): void {
		this.registerEvent(this.app.workspace.on("layout-change", () => this.titleController?.refresh()));
		this.registerEvent(this.app.workspace.on("active-leaf-change", () => this.titleController?.refresh()));
		this.registerEvent(this.app.workspace.on("file-open", () => this.titleController?.refresh()));
	}

	// ---------------------------------------------------------------- подмена имени

	/**
	 * Создаёт контроллер подмены при первом обращении. Резолвер строится по индексу
	 * и настройке (§3, DL-053): при выключенном feature-flag решение всегда пустое,
	 * поэтому интерфейс остаётся в состоянии, близком к stock Obsidian.
	 */
	private titles(): TitleController {
		if (this.titleController === null) {
			this.titleController = new TitleController(
				this.app as unknown as TitleHost,
				createTitleResolver(
					(path) => this.index.getByPath(path),
					() => this.settings.displayTitle,
				),
			);
		}
		return this.titleController;
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

		this.addCommand({
			id: "refresh-display-titles",
			name: "Обновить отображаемые имена",
			callback: () => {
				const stats = this.titleStats();
				this.refreshDisplayTitles();
				const after = this.titleStats();
				new Notice(
					`${PLUGIN_NAME}: подмена имени ${after.enabled ? "включена" : "выключена"} — ` +
						`элементов проводника ${after.explorerTargets}, заголовков ${after.leafTargets}` +
						(stats.enabled === after.enabled ? "" : " (состояние изменилось)"),
				);
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
