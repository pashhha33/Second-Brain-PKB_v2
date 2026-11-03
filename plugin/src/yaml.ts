/**
 * yaml.ts — разбор подмножества YAML (фаза 4).
 *
 * Из текста блока frontmatter получает отображение ключей и значений. Подмножество выбрано
 * по составу объектов модели: обязательные свойства (INV-01…INV-12), значения свойств ядра
 * (`docs/metamodel/07-core-properties.md`) и значения отношений — строки, числа, логические
 * значения, канонические ссылки (INV-15) и их списки.
 *
 * Поддержаны: отображения (в том числе вложенные), блочные и инлайн-списки, списки отображений
 * `- key: value`, блочные скаляры `|` и `>`, строки в кавычках с экранированием, числа,
 * логические значения, `null`, комментарии, LF и CRLF. Не поддержаны: якоря и алиасы, теги,
 * поточные отображения `{…}`, несколько документов в файле, `#` внутри блочного скаляра
 * (комментарии вырезаются до разбора). Ключи с неразобранным значением — в `unsupported`.
 *
 * Основание выбора собственного парсера вместо `parseYamlFrontmatter` из Obsidian API — DL-051:
 * модуль остаётся чистым (без импорта `obsidian`) и проверяемым вне приложения, а бандл не
 * содержит стороннего кода (`docs/PROJECT_BRIEF.md`, «Ограничения»).
 */

/** Регулярное выражение блока frontmatter: начало файла, `---`, содержимое, `---`. */
const FRONTMATTER_PATTERN = /^---\r?\n([\s\S]*?)\r?\n---[ \t]*(\r?\n|$)/;

/** Признак строки `- key: value` — элемента списка, являющегося отображением. */
const MAPPING_ITEM_PATTERN = /^(?:'[^']*'|"[^"]*"|[^:#\s][^:]*):(?:\s|$)/;

/** Строка блока: отступ, текст без комментария, номер (используется в сообщениях). */
type RawLine = { indent: number; text: string; no: number };

/** Результат разбора блока YAML. */
export interface ParsedYaml {
	/** Отображение верхнего уровня; пустое, если блок не является отображением. */
	data: Record<string, unknown>;
	/** Ключи, значение которых разобрать не удалось (неподдерживаемые конструкции). */
	unsupported: string[];
}

/** Отделяет блок frontmatter от тела заметки. */
export function splitFrontmatter(text: string): { frontmatter: string | null; body: string } {
	const match = FRONTMATTER_PATTERN.exec(text);
	if (!match) {
		return { frontmatter: null, body: text };
	}
	return { frontmatter: match[1], body: text.slice(match[0].length) };
}

/** Убирает комментарий: `#` вне кавычек, которому предшествует пробел или начало строки. */
function stripComment(line: string): string {
	let out = "";
	let quote: string | null = null;
	for (let i = 0; i < line.length; i++) {
		const ch = line[i];
		if (quote) {
			out += ch;
			if (ch === "\\" && quote === '"' && i + 1 < line.length) {
				out += line[++i];
				continue;
			}
			if (ch === quote) quote = null;
			continue;
		}
		if (ch === '"' || ch === "'") {
			quote = ch;
			out += ch;
			continue;
		}
		if (ch === "#" && (i === 0 || /\s/.test(line[i - 1]))) {
			break;
		}
		out += ch;
	}
	return out.replace(/\s+$/, "");
}

/** Экранирующие последовательности строк в двойных кавычках. */
const ESCAPES: Record<string, string> = { n: "\n", t: "\t", r: "\r", '"': '"', "\\": "\\" };

/** Раскрывает экранирующие последовательности строки в двойных кавычках. */
function unescapeDouble(value: string): string {
	return value.replace(/\\(.)/g, (_all, ch: string) => ESCAPES[ch] ?? ch);
}

/** Делит строку по запятым верхнего уровня — вне кавычек и скобок. */
function splitTopLevel(value: string): string[] {
	const parts: string[] = [];
	let buffer = "";
	let depth = 0;
	let quote: string | null = null;
	for (let i = 0; i < value.length; i++) {
		const ch = value[i];
		if (quote) {
			buffer += ch;
			if (ch === "\\" && quote === '"' && i + 1 < value.length) {
				buffer += value[++i];
				continue;
			}
			if (ch === quote) quote = null;
			continue;
		}
		if (ch === '"' || ch === "'") {
			quote = ch;
			buffer += ch;
			continue;
		}
		if (ch === "[" || ch === "{") {
			depth++;
		} else if (ch === "]" || ch === "}") {
			depth--;
		}
		if (ch === "," && depth === 0) {
			parts.push(buffer);
			buffer = "";
			continue;
		}
		buffer += ch;
	}
	if (buffer.trim()) {
		parts.push(buffer);
	}
	return parts;
}

/** Находит позицию `:`, разделяющую ключ и значение (вне кавычек и скобок). */
function findSeparator(text: string): number {
	let quote: string | null = null;
	let depth = 0;
	for (let i = 0; i < text.length; i++) {
		const ch = text[i];
		if (quote) {
			if (ch === "\\" && quote === '"' && i + 1 < text.length) {
				i++;
				continue;
			}
			if (ch === quote) quote = null;
			continue;
		}
		if (ch === '"' || ch === "'") {
			quote = ch;
			continue;
		}
		if (ch === "[" || ch === "{") {
			depth++;
			continue;
		}
		if (ch === "]" || ch === "}") {
			depth--;
			continue;
		}
		if (ch === ":" && depth === 0 && (i + 1 === text.length || /\s/.test(text[i + 1]))) {
			return i;
		}
	}
	return -1;
}

/** Снимает кавычки со строки (имя ключа или скаляр в кавычках). */
function unquoteKey(key: string): string {
	if (key.length >= 2 && key.startsWith('"') && key.endsWith('"')) {
		return unescapeDouble(key.slice(1, -1));
	}
	if (key.length >= 2 && key.startsWith("'") && key.endsWith("'")) {
		return key.slice(1, -1).replace(/''/g, "'");
	}
	return key;
}

/** Разбирает скаляр: строку в кавычках, инлайн-список, число, логическое значение, `null`. */
function parseScalar(token: string): unknown {
	const text = token.trim();
	const quoted = unquoteKey(text);
	if (quoted !== text) {
		return quoted;
	}
	if (text.startsWith("[") && text.endsWith("]")) {
		const inner = text.slice(1, -1).trim();
		if (!inner) return [];
		return splitTopLevel(inner).map((part) => parseScalar(part));
	}
	if (["", "~", "null", "Null", "NULL"].includes(text)) {
		return null;
	}
	if (["true", "True", "TRUE", "yes"].includes(text)) {
		return true;
	}
	if (["false", "False", "FALSE", "no"].includes(text)) {
		return false;
	}
	if (/^-?\d+$/.test(text)) {
		return Number.parseInt(text, 10);
	}
	if (/^-?\d+\.\d+$/.test(text)) {
		return Number.parseFloat(text);
	}
	return text;
}

/**
 * Разбирает блок YAML — подмножество, достаточное для объектов модели.
 * Разбор идёт по отступам: блок завершается строкой с меньшим отступом, чем уровень блока.
 */
export function parseYamlSubset(source: string): ParsedYaml {
	const lines: RawLine[] = [];
	source.split(/\r?\n/).forEach((raw, index) => {
		const text = stripComment(raw.replace(/\t/g, "    "));
		if (!text.trim()) return;
		lines.push({ indent: text.length - text.trimStart().length, text: text.trim(), no: index + 1 });
	});

	const unsupported: string[] = [];
	let pos = 0;

	function parseBlockScalar(style: string, parentIndent: number): string {
		const collected: string[] = [];
		let blockIndent = -1;
		while (pos < lines.length) {
			const line = lines[pos];
			if (line.indent <= parentIndent) break;
			if (blockIndent < 0) blockIndent = line.indent;
			collected.push(" ".repeat(Math.max(0, line.indent - blockIndent)) + line.text);
			pos++;
		}
		const joined = style.startsWith(">") ? collected.join(" ") : collected.join("\n");
		return joined.replace(/\s+$/, "");
	}

	function parseValue(key: string, rest: string, indent: number): unknown {
		if (rest.startsWith("|") || rest.startsWith(">")) {
			return parseBlockScalar(rest, indent);
		}
		if (rest === "") {
			const next = lines[pos];
			if (next && next.indent > indent) {
				return parseBlock(next.indent);
			}
			if (next && next.indent === indent && (next.text === "-" || next.text.startsWith("- "))) {
				return parseBlock(indent);
			}
			return null;
		}
		if (/^[{&*!]/.test(rest)) {
			unsupported.push(key);
			return null;
		}
		return parseScalar(rest);
	}

	function parseBlock(indent: number): unknown {
		let map: Record<string, unknown> | null = null;
		let seq: unknown[] | null = null;
		while (pos < lines.length) {
			const line = lines[pos];
			if (line.indent < indent) break;
			if (line.text === "-" || line.text.startsWith("- ")) {
				if (map) break;
				if (!seq) seq = [];
				if (line.text === "-") {
					pos++;
					seq.push(parseBlock(line.indent + 1));
					continue;
				}
				const item = line.text.slice(2).trim();
				if (MAPPING_ITEM_PATTERN.test(item) && findSeparator(item) >= 0) {
					lines[pos] = { indent: line.indent + 2, text: item, no: line.no };
					seq.push(parseBlock(line.indent + 2));
					continue;
				}
				pos++;
				seq.push(parseScalar(item));
				continue;
			}
			const sep = findSeparator(line.text);
			if (sep < 0) {
				unsupported.push(`строка ${line.no}`);
				pos++;
				continue;
			}
			if (!map) {
				map = {};
			}
			const key = unquoteKey(line.text.slice(0, sep).trim());
			const rest = line.text.slice(sep + 1).trim();
			pos++;
			map[key] = parseValue(key, rest, line.indent);
		}
		return seq ?? map ?? {};
	}

	const value = parseBlock(0);
	const data =
		value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
	return { data, unsupported };
}
