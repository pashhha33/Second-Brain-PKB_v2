/**
 * settings-tab.ts — панель настроек плагина (фазы 4–5).
 *
 * Хранит состояние трёх тумблеров видимости слоёв (§2.1 контракта), три канонических
 * пресета (§2.2) и feature-flag подмены отображаемого имени (§3, iter-015, DL-053);
 * состояние записывается в настройки плагина и в данные объектов не попадает.
 * Редактирование пользовательских пресетов и фильтрация поверхностей — фаза 5.
 */

import { App, PluginSettingTab, Setting } from "obsidian";
import type SecondBrainPlugin from "./main";
import { CANONICAL_PRESETS, DEFAULT_LAYER_VISIBILITY, resetToDefault, setLayerVisible } from "./layer-visibility";
import type { ModelLayer } from "./types";

/** Подписи слоёв и их назначение (§2.3 контракта, `docs/metamodel/02-layers.md`). */
const LAYER_LABELS: Record<ModelLayer, { name: string; description: string }> = {
	system: {
		name: "Системный слой (system)",
		description: "Определения типов, свойств, отношений, правил развёртывания и валидации. По умолчанию скрыт.",
	},
	classification: {
		name: "Слой классификации (classification)",
		description: "Домены, узлы иерархических категорий, фасеты и значения фасетов.",
	},
	content: {
		name: "Слой наполнения (content)",
		description: "Знания предметной области — экземпляры пользовательских типов.",
	},
};

export class SecondBrainSettingTab extends PluginSettingTab {
	private readonly plugin: SecondBrainPlugin;

	constructor(app: App, plugin: SecondBrainPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const { containerEl } = this;
		containerEl.empty();

		containerEl.createEl("h2", { text: "Second Brain PKB (фазы 4–5)" });
		containerEl.createEl("p", {
			text:
				"Индекс объектов модели по frontmatter, отображаемое имя по title в проводнике и заголовках " +
				"вкладок, видимость слоёв. Подмена имени в поиске, графе, quick switcher и панелях ссылок, " +
				"создание объектов из пустых ссылок и исполнение правил валидации — фаза 5. " +
				"Контракт: docs/metamodel/10-plugin-ux-contracts.md.",
		});

		const stats = this.plugin.index.stats();
		new Setting(containerEl)
			.setName("Индекс хранилища")
			.setDesc(
				`Файлов: ${stats.files}; объектов модели: ${stats.objects} ` +
					`(system ${stats.byLayer.system}, classification ${stats.byLayer.classification}, ` +
					`content ${stats.byLayer.content}); вне модели: ${stats.partial + stats.plain}` +
					(stats.duplicateIds.length ? `; повторов id: ${stats.duplicateIds.length}` : ""),
			)
			.addButton((button) =>
				button.setButtonText("Перестроить").onClick(() => {
					void this.plugin.rebuildIndex().then(() => this.display());
				}),
			);

		containerEl.createEl("h3", { text: "Отображаемое имя" });
		const titleStats = this.plugin.titleStats();
		new Setting(containerEl)
			.setName("Подменять имя на title")
			.setDesc(
				"В проводнике файлов и в заголовках вкладок вместо имени файла type_prefix_id показывается " +
					"title объекта (§3 контракта). Файл не переименовывается, содержимое заметки не изменяется. " +
					"Поиск, граф, quick switcher, панели ссылок и заголовок заметки в этой версии не подменяются.",
			)
			.addToggle((toggle) =>
				toggle.setValue(this.plugin.settings.displayTitle.override).onChange((value) => {
					void this.plugin.setDisplayTitleOverride(value).then(() => this.display());
				}),
			);

		new Setting(containerEl)
			.setName("Состояние подмены")
			.setDesc(
				titleStats.enabled
					? `Включена: элементов проводника ${titleStats.explorerTargets} ` +
						`(наблюдателей ${titleStats.explorerObservers}), заголовков ${titleStats.leafTargets}, ` +
						`обёрток getDisplayText ${titleStats.wrappedViews}.`
					: "Выключена: проводник и вкладки показывают имена файлов, как в Obsidian без плагина.",
			)
			.addButton((button) =>
				button.setButtonText("Обновить").onClick(() => {
					this.plugin.refreshDisplayTitles();
					this.display();
				}),
			);

		containerEl.createEl("h3", { text: "Видимость слоёв" });
		for (const layer of ["system", "classification", "content"] as ModelLayer[]) {
			const label = LAYER_LABELS[layer];
			new Setting(containerEl)
				.setName(label.name)
				.setDesc(label.description)
				.addToggle((toggle) =>
					toggle.setValue(this.plugin.settings.layerVisibility[layer]).onChange((value) => {
						this.plugin.settings = setLayerVisible(this.plugin.settings, layer, value);
						void this.plugin.saveSettings();
					}),
				);
		}

		containerEl.createEl("h3", { text: "Пресеты" });
		const presetSetting = new Setting(containerEl).setDesc(
			"Три канонических пресета доступны всегда и не удаляются (§2.2). Пользовательские пресеты — фаза 5.",
		);
		for (const preset of CANONICAL_PRESETS) {
			presetSetting.addButton((button) =>
				button
					.setButtonText(preset.label)
					.setTooltip(
						`system: ${preset.visibility.system ? "видим" : "скрыт"}, ` +
							`classification: ${preset.visibility.classification ? "видим" : "скрыт"}, ` +
							`content: ${preset.visibility.content ? "видим" : "скрыт"}`,
					)
					.onClick(() => {
						void this.plugin.applyPreset(preset.id).then(() => this.display());
					}),
			);
		}

		new Setting(containerEl)
			.setName("Восстановить видимость по умолчанию")
			.setDesc(
				`content и classification видимы, system скрыт (§2.3). Значения по умолчанию: ` +
					`system ${DEFAULT_LAYER_VISIBILITY.system}, classification ${DEFAULT_LAYER_VISIBILITY.classification}, ` +
					`content ${DEFAULT_LAYER_VISIBILITY.content}.`,
			)
			.addButton((button) =>
				button.setButtonText("Сбросить").onClick(() => {
					this.plugin.settings = resetToDefault(this.plugin.settings);
					void this.plugin.saveSettings().then(() => this.display());
				}),
			);
	}
}
