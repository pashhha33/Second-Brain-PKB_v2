#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Самопроверка iter-014: минимальный каркас Obsidian-плагина в plugin/.

Проверяет в песочнице (только stdlib + node/npm):
  A. Состав каркаса и конфиги (manifest, package, tsconfig, esbuild, versions, src/);
  B. Сборка: `npm run build` без ошибок TypeScript, бандл main.js создан;
  C. Офлайн-харнесс: `node tools/plugin_harness.cjs` — 104 проверки, 0 ошибок;
  D. Объём файлов по R-006 (~300 строк);
  E. Diff песочницы с эталонным деревом a66e605: изменён только ожидаемый набор файлов;
  F. Язык артефактов: нет CJK-вкраплений, идентификаторы кода ASCII;
  G. Согласованность указателей и счётчиков в изменённых документах (R-007);
  H. Контракты в коде: значения по умолчанию видимости слоёв, пресеты, машинный ключ,
     состав системного слоя, команды плагина.

Запуск:  python3 tools/selfcheck_iter014.py   (из корня песочницы)
Код возврата 0 — все проверки пройдены.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATTIC = os.path.join(os.path.dirname(ROOT), "attic", "head-a66e605")

FAIL = []
WARN = []
SUMMARY = []
PASS = [0]
SECT = {}
CUR = ["A"]

SRC = {
    "types.ts": 117,
    "identity.ts": 152,
    "yaml.ts": 291,
    "frontmatter.ts": 150,
    "vault-index.ts": 214,
    "display-title.ts": 91,
    "layer-visibility.ts": 195,
    "main.ts": 201,
    "settings-tab.ts": 112,
}
DOC_CHANGED = [
    "docs/CHECKPOINT.md",
    "docs/PROJECT_BRIEF.md",
    "docs/decisions/decision-log.md",
    "docs/glossary/glossary.md",
    "docs/metamodel/00-overview.md",
    "docs/project-map/PROJECT_MAP.md",
]
CJK = re.compile("[\u3040-\u30ff\u4e00-\u9fff]")


def section(name):
    CUR[0] = name


def ok(msg):
    PASS[0] += 1
    SECT[CUR[0]] = SECT.get(CUR[0], 0) + 1


def fail(msg):
    FAIL.append(msg)


def warn(msg):
    WARN.append(msg)


def check(cond, msg):
    if cond:
        ok(msg)
    else:
        fail(msg)
    return bool(cond)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def lines(path):
    return len(read(path).splitlines())


def pj(*parts):
    return os.path.join(ROOT, *parts)


# =========================================================== A. состав каркаса

section("A")
print("=== A. Состав каркаса и конфиги ===")
for name in ["manifest.json", "package.json", "tsconfig.json", "esbuild.config.mjs",
             "versions.json", "README.md", ".gitkeep"]:
    check(os.path.isfile(pj("plugin", name)), "plugin/%s существует" % name)
for name in sorted(SRC):
    check(os.path.isfile(pj("plugin", "src", name)), "plugin/src/%s существует" % name)
check(not os.path.exists(pj("plugin", "styles.css")), "plugin/styles.css не создан (стилей нет)")

manifest = json.loads(read(pj("plugin", "manifest.json")))
package = json.loads(read(pj("plugin", "package.json")))
tsconfig_raw = read(pj("plugin", "tsconfig.json"))
versions = json.loads(read(pj("plugin", "versions.json")))
esbuild = read(pj("plugin", "esbuild.config.mjs"))

for key in ["id", "name", "version", "minAppVersion", "description", "author", "isDesktopOnly"]:
    check(key in manifest, "manifest.json: ключ %s" % key)
check(manifest["id"] == "second-brain-pkb", "manifest.json: id = second-brain-pkb")
check(manifest["minAppVersion"] == "1.5.0", "manifest.json: minAppVersion = 1.5.0")
check(versions.get(manifest["version"]) == manifest["minAppVersion"],
      "versions.json: %s -> %s" % (manifest["version"], manifest["minAppVersion"]))
check(package.get("private") is True, "package.json: private = true")
check(package.get("main") == "main.js", "package.json: main = main.js")
check(package["version"] == manifest["version"], "package.json: version совпадает с manifest")
for script in ["build", "dev", "typecheck"]:
    check(script in package.get("scripts", {}), "package.json: скрипт %s" % script)
check("dependencies" not in package, "package.json: рантайм-зависимостей нет")
for dep in ["typescript", "esbuild", "obsidian"]:
    check(dep in package.get("devDependencies", {}), "package.json: devDependency %s" % dep)
co = json.loads(re.sub(r"//.*", "", tsconfig_raw))["compilerOptions"]
check(co.get("strict") is True, "tsconfig.json: strict")
check(co.get("noEmit") is True, "tsconfig.json: noEmit (типизация отдельно от сборки)")
check(co.get("types") == [], "tsconfig.json: types = [] (@types/node не требуется)")
check('"src/**/*.ts"' in tsconfig_raw, "tsconfig.json: include = src/**/*.ts")
check('"src/main.ts"' in esbuild, "esbuild: точка входа src/main.ts")
check('"main.js"' in esbuild, "esbuild: outfile main.js")
check('"cjs"' in esbuild, "esbuild: format cjs")
for ext in ["obsidian", "electron", "@codemirror/state", "@lezer/common"]:
    check('"%s"' % ext in esbuild, "esbuild: %s в external" % ext)

gitignore = read(pj(".gitignore"))
for pat in ["node_modules/", "plugin/main.js", "tools/"]:
    check(pat in gitignore, ".gitignore: %s (в коммит не входит)" % pat)

# ============================================================== B. сборка

section("B")
print("=== B. Сборка (npm run build) ===")
build = subprocess.run(["npm", "run", "build"], cwd=pj("plugin"),
                       capture_output=True, text=True, timeout=600)
check(build.returncode == 0, "npm run build: код возврата 0")
if build.returncode != 0:
    fail("npm run build: stderr — %s" % build.stderr[-400:])
bundle = pj("plugin", "main.js")
check(os.path.isfile(bundle), "plugin/main.js создан")
if os.path.isfile(bundle):
    size = os.path.getsize(bundle)
    check(size > 10000, "plugin/main.js: размер %d байт (>10 КБ)" % size)
    head = read(bundle)[:400]
    check("СГЕНЕРИРОВАННЫЙ ФАЙЛ" in head, "plugin/main.js: баннер о генерации")
    check("require(\"obsidian\")" in read(bundle), "plugin/main.js: obsidian остался внешним")
    SUMMARY.append("сборка: main.js %d байт, ошибок TypeScript нет" % size)

# ========================================================= C. харнесс

section("C")
print("=== C. Офлайн-харнесс ===")
harness = subprocess.run(["node", "tools/plugin_harness.cjs"], cwd=ROOT,
                         capture_output=True, text=True, timeout=300)
check(harness.returncode == 0, "plugin_harness.cjs: код возврата 0")
m = re.search(r"Проверок пройдено: (\d+); ошибок: (\d+)", harness.stdout)
check(bool(m), "plugin_harness.cjs: строка итога найдена")
if m:
    check(int(m.group(1)) == 104, "харнесс: 104 проверки (факт %s)" % m.group(1))
    check(int(m.group(2)) == 0, "харнесс: 0 ошибок (факт %s)" % m.group(2))
    SUMMARY.append("харнесс: %s проверок, %s ошибок" % (m.group(1), m.group(2)))
for grp in ["A. Индекс по 19 эталонным заметкам", "B. Отображаемое имя",
            "C. Видимость слоёв", "D. Разбор frontmatter",
            "E. Инкрементальное обновление", "F. Производные функции идентичности"]:
    check(grp in harness.stdout, "харнесс: группа %s" % grp)

# ========================================================= D. объём файлов

section("D")
print("=== D. Объём файлов (R-006) ===")
maxsrc = 0
for name in sorted(SRC):
    n = lines(pj("plugin", "src", name))
    check(n <= 300, "plugin/src/%s: %d строк (<=300)" % (name, n))
    check(n == SRC[name], "plugin/src/%s: %d строк (счётчик в отчёте)" % (name, n))
    maxsrc = max(maxsrc, n)
if maxsrc > 280:
    warn("plugin/src/yaml.ts: %d строк — приближается к границе R-006" % maxsrc)
for doc in DOC_CHANGED + ["plugin/README.md"]:
    n = lines(pj(*doc.split("/")))
    check(n <= 300, "%s: %d строк (<=300)" % (doc, n))
    SUMMARY.append("%s: %d строк" % (doc, n))

# ========================================================= E. diff с a66e605

section("E")
print("=== E. Diff песочницы с эталонным деревом a66e605 ===")
SKIP_DIRS = {"node_modules", ".git", "tools", "__pycache__", "build", "dist"}
SKIP_FILES = {"main.js", "package-lock.json"}


def tree(base):
    out = {}
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if f in SKIP_FILES:
                continue
            full = os.path.join(dirpath, f)
            out[os.path.relpath(full, base)] = full
    return out


check(os.path.isdir(ATTIC), "эталонное дерево attic/head-a66e605 найдено")
old = tree(ATTIC)
new = tree(ROOT)
added = sorted(set(new) - set(old))
removed = sorted(set(old) - set(new))
changed = sorted(p for p in set(old) & set(new) if read(old[p]) != read(new[p]))

expected_added = sorted(
    ["plugin/" + n for n in ["README.md", "manifest.json", "package.json", "tsconfig.json",
                             "esbuild.config.mjs", "versions.json"]]
    + ["plugin/src/" + n for n in SRC]
    + ["docs/_workflow/iterations/iter-014/REPORT.md"]
)
check(added == expected_added, "добавлены только файлы каркаса и REPORT.md (%d)" % len(added))
if added != expected_added:
    fail("добавлено сверх ожидания: %s" % [a for a in added if a not in expected_added])
    fail("не добавлено: %s" % [a for a in expected_added if a not in added])
check(changed == sorted(DOC_CHANGED), "изменены только шесть служебных документов")
if changed != sorted(DOC_CHANGED):
    fail("изменено сверх ожидания: %s" % [c for c in changed if c not in DOC_CHANGED])
check(removed == [], "файлы репозитория не удалялись")
check("plugin/.gitkeep" in new and "plugin/.gitkeep" in old
      and read(old["plugin/.gitkeep"]) == read(new["plugin/.gitkeep"]),
      "plugin/.gitkeep сохранён без изменений")
for frozen in ["schema", "examples", "docs/adr", "docs/validation", "scripts"]:
    touched = [p for p in changed + added + removed if p.startswith(frozen + "/")]
    check(not touched, "%s/ не изменялся" % frozen)
metamodel = [p for p in changed if p.startswith("docs/metamodel/")]
check(metamodel == ["docs/metamodel/00-overview.md"],
      "в docs/metamodel/ изменён только 00-overview.md")
SUMMARY.append("diff: добавлено %d, изменено %d, удалено %d" % (len(added), len(changed), len(removed)))

# ========================================================= F. язык артефактов

section("F")
print("=== F. Язык артефактов ===")
for doc in DOC_CHANGED + ["plugin/README.md", "docs/_workflow/iterations/iter-014/REPORT.md"]:
    if not check(os.path.isfile(pj(*doc.split("/"))), "%s: файл существует" % doc):
        continue
    bad = [i + 1 for i, l in enumerate(read(pj(*doc.split("/"))).splitlines()) if CJK.search(l)]
    check(not bad, "%s: нет CJK-вкраплений" % doc)
    if bad:
        warn("%s: CJK в строках %s" % (doc, bad[:5]))
for name in sorted(SRC) + ["../esbuild.config.mjs"]:
    path = pj("plugin", "src", name) if not name.startswith("..") else pj("plugin", name.lstrip("./"))
    bad = [i + 1 for i, l in enumerate(read(path).splitlines()) if CJK.search(l)]
    check(not bad, "plugin/src/%s: нет CJK-вкраплений" % name)
ident = re.compile(r"export (?:default )?(?:abstract )?(?:class|function|const|interface|type)\s+(\w+)")
nonascii = []
for name in sorted(SRC):
    for m in ident.finditer(read(pj("plugin", "src", name))):
        if not m.group(1).isascii():
            nonascii.append(m.group(1))
check(not nonascii, "экспортируемые идентификаторы — ASCII")

# ========================================================= G. документы

section("G")
print("=== G. Указатели и счётчики в документах (R-007) ===")
dlog = read(pj("docs", "decisions", "decision-log.md"))
ids = re.findall(r"^(DL-\d+) \(iter-", dlog, re.M)
check(len(ids) == 52, "decision-log: 52 записи (факт %d)" % len(ids))
check(ids[-1] == "DL-052", "decision-log: последняя запись DL-052")
for dl in ["DL-050", "DL-051", "DL-052"]:
    check(dl in ids, "decision-log: запись %s" % dl)

pmap = read(pj("docs", "project-map", "PROJECT_MAP.md"))
check("DL-001…DL-052" in pmap, "PROJECT_MAP: указатель DL-001…DL-052")
check("| 4 | Каркас плагина | в работе (iter-014)" in pmap, "PROJECT_MAP: фаза 4 — в работе")
check("| Каркас плагина |" in pmap, "PROJECT_MAP: строка артефакта «Каркас плагина»")
check("с iter-014 каркас" in pmap, "PROJECT_MAP: описание plugin/ обновлено")

ovw = read(pj("docs", "metamodel", "00-overview.md"))
check("DL-001…DL-052" in ovw and "DL-006…DL-052" in ovw, "00-overview: указатели DL-052")
check("Фаза 4 начата в iter-014" in ovw, "00-overview: старт фазы 4")
check("18. **Каркас плагина**" in ovw, "00-overview: пункт 18 порядка появления")
check("| Каркас плагина (фаза 4) |" in ovw, "00-overview: строка артефакта")
check("iter-014: DL-050…DL-052" in ovw, "00-overview: строка журнала решений")

gl = read(pj("docs", "glossary", "glossary.md"))
for term in ["Plugin skeleton", "Vault index", "YAML subset parser", "Unsupported value",
             "Frontmatter normalization", "Display title stub", "Machine key",
             "Layer visibility stub"]:
    check("**%s**" % term in gl, "glossary: термин %s" % term)
check("DL-001…DL-052" in gl, "glossary: указатель DL-001…DL-052")
check("plugin/README.md" in gl, "glossary: ссылка на plugin/README.md")

brief = read(pj("docs", "PROJECT_BRIEF.md"))
check("в работе (iter-014" in brief, "PROJECT_BRIEF: фаза 4 — в работе")
check("DL-050" in brief and "DL-052" in brief, "PROJECT_BRIEF: ссылки на DL-050…DL-052")

chk = read(pj("docs", "CHECKPOINT.md"))
check("Что готово (iter-014)" in chk, "CHECKPOINT: раздел «Что готово (iter-014)»")
check("104 проверки" in chk, "CHECKPOINT: счётчик проверок харнесса")
check("DL-001…DL-052" in chk, "CHECKPOINT: указатель DL-001…DL-052")

rme = read(pj("plugin", "README.md"))
check("npm run build" in rme, "plugin/README: команда сборки")
check(".obsidian/plugins" in rme, "plugin/README: установка в хранилище")
check("## Что не реализовано (фаза 5)" in rme, "plugin/README: ограничения v1")
check("10-plugin-ux-contracts.md" in rme, "plugin/README: ссылка на контракт")
check("examples/README.md" in rme, "plugin/README: ссылка «проверено на examples»")

# ========================================================= H. контракты в коде

section("H")
print("=== H. Контракты в коде ===")
lv = read(pj("plugin", "src", "layer-visibility.ts"))
dflt = re.search(r"DEFAULT_LAYER_VISIBILITY[^=]*=\s*\{(.*?)\}", lv, re.S).group(1)
check(re.search(r"content:\s*true", dflt) is not None, "default: content видим (§2.3)")
check(re.search(r"classification:\s*true", dflt) is not None, "default: classification видим (§2.3)")
check(re.search(r"system:\s*false", dflt) is not None, "default: system скрыт (§2.3)")
for pid in ["knowledge-only", "model", "all"]:
    check('"%s"' % pid in lv, "пресет %s (§2.2)" % pid)
check("export function isLayerVisible" in lv, "API: isLayerVisible(layer)")
check("layerVisibility" in lv and "customPresets" in lv, "настройки: состояние в data.json плагина")

dt = read(pj("plugin", "src", "display-title.ts"))
check("export function getDisplayTitle" in dt, "API: getDisplayTitle(file | path)")
check("basename" in dt, "getDisplayTitle: откат к имени файла (§3.5)")
check("export function getTitleIndicator" in dt, "API: getTitleIndicator (§3.4)")

idt = read(pj("plugin", "src", "identity.ts"))
mk = re.search(r"MACHINE_KEY_FIELDS[^=]*=\s*\[(.*?)\]", idt, re.S).group(1)
order = re.findall(r'"([a-z_]+)"', mk)
check(order == ["type_value", "property_key", "relation_key", "rule_key"],
      "машинный ключ: порядок %s" % order)
sysblk = re.search(r"SYSTEM_TYPES[^=]*=\s*\[(.*?)\]", idt, re.S).group(1)
systypes = re.findall(r'"([a-z-]+)"', sysblk)
check(len(systypes) == 6 and "field-expansion" in systypes,
      "системный слой: 6 значений type, включая field-expansion")
clblk = re.search(r"CLASSIFICATION_TYPES[^=]*=\s*\[(.*?)\]", idt, re.S).group(1)
cltypes = re.findall(r'"([a-z-]+)"', clblk)
check(cltypes == ["domain", "hierarchical-category", "facet", "facet-value"],
      "слой классификации: 4 значения type")
check("INV-09" in idt, "identity.ts: примечание о расхождении с текстом INV-09")
check("export function layerOfType" in idt and "export function expectedBasename" in idt,
      "identity.ts: layerOfType и expectedBasename (INV-05, INV-06, INV-09)")

main = read(pj("plugin", "src", "main.ts"))
check("export default class SecondBrainPlugin extends Plugin" in main, "main.ts: класс Plugin")
check("async onload" in main and "onunload" in main, "main.ts: onload и onunload")
for ev in ['"create"', '"modify"', '"delete"', '"rename"']:
    check(ev in main, "main.ts: событие хранилища %s" % ev)
check("getMarkdownFiles" in main, "main.ts: полный проход по .md при загрузке")
for cmd in ["rebuild-index", "reset-layer-visibility", "apply-preset-"]:
    check(cmd in main, "main.ts: команда %s" % cmd)
check("addSettingTab" in main, "main.ts: вкладка настроек")

vi = read(pj("plugin", "src", "vault-index.ts"))
for api in ["getById", "duplicateIds", "stats", "clear", "remove"]:
    check(api in vi, "vault-index.ts: метод %s" % api)
fm = read(pj("plugin", "src", "frontmatter.ts"))
check("export function normalizeEntry" in fm, "frontmatter.ts: normalizeEntry")
for key in ["id", "type", "title", "aliases", "layer", "status", "owner"]:
    check('"%s"' % key in fm, "frontmatter.ts: минимум INV — ключ %s" % key)
ym = read(pj("plugin", "src", "yaml.ts"))
check("export function parseYamlSubset" in ym and "export function splitFrontmatter" in ym,
      "yaml.ts: parseYamlSubset и splitFrontmatter")
check("unsupported" in ym, "yaml.ts: неразобранные ключи — в unsupported")

# ============================================================== итог

print()
for line in SUMMARY:
    print("  " + line)
for w in WARN:
    print("ПРЕДУПРЕЖДЕНИЕ: %s" % w)
for f in FAIL:
    print("ОШИБКА: %s" % f)
for k in sorted(SECT):
    print("  секция %s: %d проверок" % (k, SECT[k]))
print("Проверок пройдено: %d; предупреждений: %d; ошибок: %d" % (PASS[0], len(WARN), len(FAIL)))
sys.exit(1 if FAIL else 0)
