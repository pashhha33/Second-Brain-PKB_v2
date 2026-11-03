import esbuild from "esbuild";
import { builtinModules } from "node:module";
import process from "node:process";

const banner = `/*
 Second Brain PKB — каркас плагина (фаза 4).
 СГЕНЕРИРОВАННЫЙ ФАЙЛ: не править вручную.
 Исходники — plugin/src/, сборка — plugin/esbuild.config.mjs (npm run build).
 Контракты поведения — docs/metamodel/10-plugin-ux-contracts.md.
*/
`;

const production = process.argv[2] === "production";

// Всё, что предоставляет Obsidian и Electron, остаётся внешним: в бандле нет
// стороннего рантайм-кода (PROJECT_BRIEF, «Ограничения»: офлайн, без внешних зависимостей).
const external = [
	"obsidian",
	"electron",
	"@codemirror/autocomplete",
	"@codemirror/collab",
	"@codemirror/commands",
	"@codemirror/language",
	"@codemirror/lint",
	"@codemirror/search",
	"@codemirror/state",
	"@codemirror/view",
	"@lezer/common",
	"@lezer/highlight",
	"@lezer/lr",
	...builtinModules,
];

const options = {
	banner: { js: banner },
	entryPoints: ["src/main.ts"],
	bundle: true,
	external,
	format: "cjs",
	target: "es2020",
	platform: "browser",
	logLevel: "info",
	treeShaking: true,
	sourcemap: production ? false : "inline",
	minify: production,
	outfile: "main.js",
};

if (production) {
	await esbuild.build(options);
} else {
	const context = await esbuild.context(options);
	await context.watch();
}
