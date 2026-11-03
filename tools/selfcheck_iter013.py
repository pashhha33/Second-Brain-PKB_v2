#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Самопроверка iter-013: третья волна правил валидации и расширение набора examples/.

Проверяет в песочнице (без jsonschema и yaml — только stdlib):
  A. 19 эталонных заметок examples/ против пяти схем schema/ (мини-валидатор JSON Schema);
  B. 19 правил валидации (8 + 6 + 5) на данных набора, реестры типов/свойств/отношений
     разбираются из таблиц документации, а не задаются вручную;
  C. пять объектов правил из docs/validation/03-third-wave-rules.md против ветви
     validation-rule-object схемы system-definitions.json;
  D. сквозные счётчики и ссылки в обновлённых документах (реестр 00, README examples,
     PROJECT_MAP, PROJECT_BRIEF, CHECKPOINT, glossary, decision-log, 00-overview).

Запуск:  python3 tools/selfcheck_iter013.py   (из корня песочницы)
Код возврата 0 — все проверки пройдены.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAIL = []
WARN = []
SUMMARY = []
PASS = [0]
SECT = {}
CUR = ["A"]


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


def rel(path):
    return os.path.relpath(path, ROOT)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------- YAML subset


def _scalar(tok):
    tok = tok.strip()
    if tok.startswith('"') and tok.endswith('"') and len(tok) >= 2:
        return tok[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if tok.startswith("'") and tok.endswith("'") and len(tok) >= 2:
        return tok[1:-1].replace("''", "'")
    if tok.startswith("[") and tok.endswith("]"):
        inner = tok[1:-1].strip()
        if not inner:
            return []
        return [_scalar(p) for p in _split_inline(inner)]
    low = tok.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "~", ""):
        return None
    if re.fullmatch(r"-?\d+", tok):
        return int(tok)
    if re.fullmatch(r"-?\d+\.\d+", tok):
        return float(tok)
    return tok


def _split_inline(s):
    out, buf, depth, quote = [], "", 0, None
    for ch in s:
        if quote:
            buf += ch
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            buf += ch
        elif ch in "[{":
            depth += 1
            buf += ch
        elif ch in "]}":
            depth -= 1
            buf += ch
        elif ch == "," and depth == 0:
            out.append(buf)
            buf = ""
        else:
            buf += ch
    if buf.strip():
        out.append(buf)
    return out


def _strip_comment(line):
    out, quote = "", None
    i = 0
    while i < len(line):
        ch = line[i]
        if quote:
            out += ch
            if ch == quote and not (quote == '"' and i and line[i - 1] == "\\"):
                quote = None
        elif ch in "\"'":
            quote = ch
            out += ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        else:
            out += ch
        i += 1
    return out.rstrip()


def parse_yaml(text):
    """Подмножество YAML: отображения, блочные и инлайн-списки, скаляры, комментарии."""
    lines = []
    for raw in text.splitlines():
        line = _strip_comment(raw.replace("\t", "    "))
        if not line.strip():
            continue
        lines.append((len(line) - len(line.lstrip(" ")), line.strip()))
    pos = [0]

    def parse_block(indent):
        result = None
        while pos[0] < len(lines):
            ind, content = lines[pos[0]]
            if ind < indent:
                break
            if content.startswith("- "):
                if result is None:
                    result = []
                pos[0] += 1
                item = content[2:].strip()
                if ":" in item and not item.startswith(("[", '"', "'")):
                    # элемент-отображение в списке (в наборе не используется)
                    sub = {item.split(":", 1)[0].strip(): _scalar(item.split(":", 1)[1])}
                    result.append(sub)
                else:
                    result.append(_scalar(item))
                continue
            if content == "-":
                pos[0] += 1
                result = result if result is not None else []
                result.append(parse_block(ind + 1))
                continue
            if ":" not in content:
                pos[0] += 1
                continue
            key, _, val = content.partition(":")
            key = key.strip()
            val = val.strip()
            if result is None:
                result = {}
            pos[0] += 1
            if val == "":
                if pos[0] < len(lines) and lines[pos[0]][0] > ind:
                    result[key] = parse_block(lines[pos[0]][0])
                elif pos[0] < len(lines) and lines[pos[0]][0] == ind and lines[pos[0]][1].startswith("- "):
                    result[key] = parse_block(ind)
                else:
                    result[key] = None
            else:
                result[key] = _scalar(val)
        return result

    data = parse_block(0)
    return data if isinstance(data, dict) else {}


def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return None, text
    return parse_yaml(m.group(1)), m.group(2)


# ------------------------------------------------------- мини-валидатор схем

SCHEMAS = {}


def load_schema(name):
    if name not in SCHEMAS:
        SCHEMAS[name] = json.load(open(os.path.join(ROOT, "schema", name), encoding="utf-8"))
    return SCHEMAS[name]


def resolve_ref(schema_name, ref):
    if ref.startswith("#"):
        doc, frag = schema_name, ref[1:]
    else:
        doc, _, frag = ref.partition("#")
        frag = frag or "#"
    node = load_schema(doc)
    if frag in ("", "#", "/"):
        return doc, node
    for part in frag.strip("/").split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if part not in node:
            raise KeyError("%s: нет %s в %s" % (ref, part, doc))
        node = node[part]
    return doc, node


def type_ok(value, t):
    if t == "object":
        return isinstance(value, dict)
    if t == "array":
        return isinstance(value, list)
    if t == "string":
        return isinstance(value, str)
    if t == "boolean":
        return isinstance(value, bool)
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if t == "null":
        return value is None
    raise KeyError(t)


def validate(value, schema, schema_name, path, errors):
    if not isinstance(schema, dict):
        return
    if "$ref" in schema:
        ref_name, node = resolve_ref(schema_name, schema["$ref"])
        rest = {k: v for k, v in schema.items() if k not in ("$ref", "description")}
        validate(value, node, ref_name, path, errors)
        if rest:
            validate(value, rest, schema_name, path, errors)
        return
    if "const" in schema and value != schema["const"]:
        errors.append("%s: %r != const %r" % (path, value, schema["const"]))
    if "enum" in schema and value not in schema["enum"]:
        errors.append("%s: %r не в enum %r" % (path, value, schema["enum"]))
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(type_ok(value, t) for t in types):
            errors.append("%s: тип %r не соответствует %r" % (path, type(value).__name__, types))
            return
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append("%s: %r не соответствует паттерну %s" % (path, value, schema["pattern"]))
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append("%s: короче minLength" % path)
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append("%s: длиннее maxLength" % path)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append("%s: %r < minimum %r" % (path, value, schema["minimum"]))
        if "maximum" in schema and value > schema["maximum"]:
            errors.append("%s: %r > maximum %r" % (path, value, schema["maximum"]))
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append("%s: элементов %d < minItems %d" % (path, len(value), schema["minItems"]))
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append("%s: элементов больше maxItems" % path)
        if schema.get("uniqueItems"):
            flat = [json.dumps(v, ensure_ascii=False, sort_keys=True) for v in value]
            if len(set(flat)) != len(flat):
                errors.append("%s: список с повторами при uniqueItems" % path)
        if "items" in schema:
            for i, item in enumerate(value):
                validate(item, schema["items"], schema_name, "%s[%d]" % (path, i), errors)
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value or value[key] is None or value[key] == "" or value[key] == []:
                errors.append("%s: нет обязательного ключа %s" % (path, key))
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                validate(value[key], sub, schema_name, "%s.%s" % (path, key), errors)
        if "propertyNames" in schema:
            for key in value:
                validate(key, schema["propertyNames"], schema_name, "%s.key(%s)" % (path, key), errors)
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}))
            for key in value:
                if key not in allowed:
                    errors.append("%s: запрещённый ключ %s" % (path, key))
    for comb in ("allOf",):
        for i, sub in enumerate(schema.get(comb, [])):
            validate(value, sub, schema_name, "%s/%s[%d]" % (path, comb, i), errors)
    for comb in ("oneOf", "anyOf"):
        subs = schema.get(comb, [])
        if not subs:
            continue
        good = 0
        for sub in subs:
            sub_errors = []
            validate(value, sub, schema_name, path, sub_errors)
            if not sub_errors:
                good += 1
        if comb == "oneOf" and good != 1:
            errors.append("%s: oneOf — подходящих ветвей %d (нужно 1)" % (path, good))
        if comb == "anyOf" and good == 0:
            errors.append("%s: anyOf — ни одна ветвь не подходит" % path)
    if "not" in schema:
        sub_errors = []
        validate(value, schema["not"], schema_name, path, sub_errors)
        if not sub_errors:
            errors.append("%s: значение не должно проходить not" % path)
    if "if" in schema:
        sub_errors = []
        validate(value, schema["if"], schema_name, path, sub_errors)
        if not sub_errors and "then" in schema:
            validate(value, schema["then"], schema_name, path, errors)
        elif sub_errors and "else" in schema:
            validate(value, schema["else"], schema_name, path, errors)


def schema_errors(value, schema_file, subschema=None):
    doc = load_schema(schema_file)
    if subschema:
        doc = doc["$defs"][subschema]
    errors = []
    validate(value, doc, schema_file, "$", errors)
    return errors


# ------------------------------------------------------------------ реестры

UUID7 = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
CANON = re.compile(r"^\[\[([a-z0-9\-]{1,16})_([0-9a-f\-]{36})\|(.+)\]\]$")


def md_table_rows(text):
    rows = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows


def backticked(cell):
    return re.findall(r"`([^`]+)`", cell)


def load_types():
    """type_value -> {layer, extends, prefix}."""
    types = {}
    core = read(os.path.join(ROOT, "docs/metamodel/05-core-types.md"))
    for row in md_table_rows(core):
        if len(row) < 5:
            continue
        keys = backticked(row[0])
        if not keys or not re.fullmatch(r"[a-z0-9\-]+", keys[0]):
            continue
        tv = keys[0]
        if tv in ("type_value", "type_prefix"):
            continue
        ext = backticked(row[3])
        types[tv] = {"layer": "content", "extends": ext[0] if ext else None}
    builtin = read(os.path.join(ROOT, "docs/metamodel/03-builtin-types.md"))
    for row in md_table_rows(builtin):
        if len(row) < 7 or not row[0].isdigit():
            continue
        name = backticked(row[1])
        prefix = backticked(row[2])
        layer = row[6].strip().lower()
        if name and layer in ("system", "classification", "content"):
            types[name[0]] = {
                "layer": layer,
                "extends": None,
                "prefix": prefix[0] if prefix else name[0],
                "metatype_id": backticked(row[3])[0] if backticked(row[3]) else None,
            }
    return types


def load_properties():
    props = {}
    text = read(os.path.join(ROOT, "docs/metamodel/07-core-properties.md"))
    for row in md_table_rows(text):
        if len(row) < 8 or not row[0].isdigit():
            continue
        key = backticked(row[1])
        if not key:
            continue
        enum_values = backticked(row[7]) if "триггер" in row[7] else []
        props[key[0]] = {
            "id": backticked(row[3])[0],
            "value_type": backticked(row[4])[0],
            "required": row[5].strip(),
            "applies_to": backticked(row[6]),
            "enum_values": enum_values,
            "is_trigger": "триггер" in row[7],
        }
    return props


def load_relations():
    rels = {}
    text = read(os.path.join(ROOT, "docs/metamodel/06-relations.md"))
    for row in md_table_rows(text):
        if len(row) < 8 or not row[0].isdigit():
            continue
        key = backticked(row[1])
        if not key:
            continue
        def domain(cell):
            if "любой тип" in cell:
                return ["*"]
            return backticked(cell)

        rels[key[0]] = {
            "id": backticked(row[3])[0],
            "source_type": domain(row[4]),
            "target_type": domain(row[5]),
            "cardinality": backticked(row[6])[0],
        }
    return rels


TYPES = load_types()
PROPS = load_properties()
RELS = load_relations()


def type_prefix(tv):
    if tv in TYPES and "prefix" in TYPES[tv]:
        return TYPES[tv]["prefix"]
    return tv[:16]


def ancestors(tv):
    """Тип и все его предки по extends (цепочка из реестра)."""
    seen, cur = [], tv
    while cur and cur in TYPES and cur not in seen:
        seen.append(cur)
        cur = TYPES[cur].get("extends")
    if cur and cur not in seen:
        seen.append(cur)
    return seen


# ------------------------------------------------------------- набор examples

EXAMPLES_DIR = os.path.join(ROOT, "examples")
NOTES = []
for fname in sorted(os.listdir(EXAMPLES_DIR)):
    if not fname.endswith(".md") or fname == "README.md":
        continue
    path = os.path.join(EXAMPLES_DIR, fname)
    fm, body = split_frontmatter(read(path))
    NOTES.append({"file": fname, "path": path, "fm": fm, "body": body})
BY_ID = {}
BY_FILE = {}
for n in NOTES:
    BY_ID[n["fm"].get("id")] = n
    stem = n["file"][:-3]
    BY_FILE[stem] = n


def links_of(fm):
    """Все канонические ссылки frontmatter: (key, target_stem, alias, is_defined_by)."""
    out = []
    for key, value in fm.items():
        if key == "defined_by":
            out.append((key, None, str(value), True))
            continue
        items = value if isinstance(value, list) else [value]
        for item in items:
            if isinstance(item, str):
                for raw in re.findall(r"\[\[[^\]]+\]\]", item):
                    m = CANON.fullmatch(raw)
                    if m:
                        out.append((key, "%s_%s" % (m.group(1), m.group(2)), m.group(3), False))
    return out


def media_keys(tv):
    """Ключи свойств media/list<media>, применимые к типу (по реестру)."""
    chain = ancestors(tv)
    return {k for k, v in PROPS.items()
            if v["value_type"] in ("media", "list<media>")
            and any(a == "*" or a in chain for a in v["applies_to"])}


# ============================================================== A. схемы

print("=== A. Схемы: 19 эталонных заметок ===")
CUR[0] = "A"
check(len(NOTES) == 19, "в examples/ ровно 19 заметок (найдено %d)" % len(NOTES))

for n in NOTES:
    fm, name = n["fm"], n["file"]
    errs = schema_errors(fm, "object.json")
    tv = fm.get("type")
    if tv == "image":
        errs += schema_errors(fm, "media.json", "image-wrapper")
    elif tv == "facet-value":
        errs += schema_errors(fm, "facet-value.json")
    elif tv in ("type", "property", "relation", "field-expansion", "validation-rule"):
        errs += schema_errors(fm, "system-definitions.json")
    if fm.get("layer") == "content":
        errs += schema_errors(fm, "core-property-values.json")
    check(not errs, "%s: схемы (%s)" % (name, "; ".join(errs[:3]) if errs else "ok"))

# значения свойств вне 12 ключей схемы — только допустимые по applies_to
SERVICE = {"id", "type", "defined_by", "title", "aliases", "layer", "status", "owner"}
for n in NOTES:
    fm, tv = n["fm"], n["fm"].get("type")
    if fm.get("layer") != "content":
        continue
    chain = ancestors(tv)
    for key in fm:
        if key in SERVICE or key not in PROPS:
            continue
        applies = PROPS[key]["applies_to"]
        check(any(a == "*" or a in chain for a in applies),
              "%s: ключ %s применим к %s (applies_to=%s)" % (n["file"], key, tv, applies))

# ============================================================== B. правила

print("=== B. Правила валидации 1…19 на данных набора ===")
CUR[0] = "B"


def rule(num, key, problems, note=""):
    SUMMARY.append("правило %2d %-30s %s%s" % (num, key, "ОК" if not problems else "СРАБОТАЛО", note))
    check(not problems, "правило %d %s%s" % (num, key, "" if not problems else ": " + "; ".join(problems[:3])))


# 1 unique-id
ids = [n["fm"].get("id") for n in NOTES]
dupes = {i for i in ids if ids.count(i) > 1}
rule(1, "unique-id", ["дубль id %s" % d for d in sorted(dupes)])
check(all(isinstance(i, str) and UUID7.match(i) for i in ids), "все id — UUIDv7 канонической формы")

# 2 filename-matches-object
bad = []
for n in NOTES:
    fm = n["fm"]
    expect = "%s_%s.md" % (type_prefix(fm.get("type")), fm.get("id"))
    if n["file"] != expect:
        bad.append("%s != %s" % (n["file"], expect))
rule(2, "filename-matches-object", bad)

# 3 aliases-first-equals-title
bad = [n["file"] for n in NOTES
       if not (isinstance(n["fm"].get("aliases"), list) and n["fm"]["aliases"]
               and str(n["fm"]["aliases"][0]).strip() == str(n["fm"].get("title")).strip())]
rule(3, "aliases-first-equals-title", bad)

# 4 media-target-is-image
bad = []
for n in NOTES:
    for key in media_keys(n["fm"].get("type")):
        if key not in n["fm"]:
            continue
        values = n["fm"][key] if isinstance(n["fm"][key], list) else [n["fm"][key]]
        for v in values:
            m = CANON.fullmatch(str(v))
            if not m:
                bad.append("%s.%s: не каноническая ссылка (%r)" % (n["file"], key, v))
                continue
            stem = "%s_%s" % (m.group(1), m.group(2))
            target = BY_FILE.get(stem)
            if target is None:
                bad.append("%s.%s: цель %s вне набора" % (n["file"], key, stem))
            elif target["fm"].get("type") != "image":
                bad.append("%s.%s: цель %s имеет type %s" % (n["file"], key, stem, target["fm"].get("type")))
rule(4, "media-target-is-image", bad)

# 5 image-has-attachment
bad = [n["file"] for n in NOTES
       if n["fm"].get("type") == "image" and not str(n["fm"].get("attachment") or "").strip()]
rule(5, "image-has-attachment", bad)

# 6 extends-acyclic (+ 13 extends-depth) — по реестру ядра, определение в наборе одно
bad = []
for tv in TYPES:
    seen, cur, depth = [], tv, 0
    while cur:
        if cur in seen:
            bad.append("цикл у %s" % tv)
            break
        seen.append(cur)
        cur = TYPES.get(cur, {}).get("extends")
        depth += 1
    if depth - 1 > 5:
        bad.append("глубина %s = %d" % (tv, depth - 1))
rule(6, "extends-acyclic (реестр ядра)", bad)
rule(13, "extends-depth (реестр ядра)", [])

# 7 defined-by-consistent
bad, skipped = [], 0
for n in NOTES:
    target = BY_ID.get(n["fm"].get("defined_by"))
    if target is None:
        skipped += 1
        continue
    if target["fm"].get("type") != "type" or target["fm"].get("layer") != "system":
        bad.append("%s: цель defined_by не определение типа" % n["file"])
    elif target["fm"].get("type_value") != n["fm"].get("type"):
        bad.append("%s: type_value цели != type" % n["file"])
rule(7, "defined-by-consistent", bad, note=" (вне набора: %d)" % skipped)

# 8 trigger-values-subset
bad = []
for n in NOTES:
    if n["fm"].get("type") != "field-expansion":
        continue
    tp = n["fm"].get("trigger_property")
    prop = PROPS.get(tp)
    if prop is None:
        bad.append("%s: нет свойства %s" % (n["file"], tp))
        continue
    if prop["value_type"] not in ("enum", "list<enum>"):
        bad.append("%s: value_type %s" % (n["file"], prop["value_type"]))
    values = n["fm"].get("trigger_values") or []
    values = values if isinstance(values, list) else [values]
    if not values:
        bad.append("%s: пустой trigger_values" % n["file"])
    unknown = [v for v in values if v not in prop["enum_values"]]
    if unknown:
        bad.append("%s: %s вне enum_values %s" % (n["file"], unknown, tp))
rule(8, "trigger-values-subset", bad)

# 9 link-target-exists
bad, total_links = [], 0
for n in NOTES:
    for key, stem, alias, is_db in links_of(n["fm"]):
        if is_db:
            continue
        total_links += 1
        target = BY_FILE.get(stem)
        if target is None:
            bad.append("%s.%s -> %s (вне набора)" % (n["file"], key, stem))
            continue
        if str(target["fm"].get("title")) != str(alias):
            bad.append("%s.%s: alias %r != title цели %r" % (n["file"], key, alias, target["fm"].get("title")))
        if target["fm"].get("id") not in stem:
            bad.append("%s.%s: id цели не совпадает" % (n["file"], key))
rule(9, "link-target-exists", bad, note=" (%d ссылок в наборе)" % total_links)

# 10 unique-machine-keys
bad = []
for keyname, tv in (("type_value", "type"), ("property_key", "property"),
                    ("relation_key", "relation"), ("rule_key", "validation-rule")):
    values = [n["fm"].get(keyname) for n in NOTES if n["fm"].get("type") == tv]
    values = [v for v in values if v]
    dupes = {v for v in values if values.count(v) > 1}
    if dupes:
        bad.append("%s: %s" % (keyname, sorted(dupes)))
rule(10, "unique-machine-keys (в наборе)", bad)

# 11 relation-acyclic
ACYCLIC = ("parent", "part-of", "blocks")
graph = {}
for n in NOTES:
    for key in ACYCLIC:
        if key in n["fm"]:
            for _, stem, _, _ in links_of({key: n["fm"][key]}):
                graph.setdefault(n["fm"]["id"], []).append(stem.split("_", 1)[1])
bad = []
for start in graph:
    stack, seen = [start], set()
    while stack:
        cur = stack.pop()
        if cur in seen:
            bad.append("цикл от %s" % start)
            break
        seen.add(cur)
        stack.extend(graph.get(cur, []))
rule(11, "relation-acyclic", bad, note=" (ключей parent/part-of/blocks в наборе: %d)" % len(graph))

# 12 inactive-field-value
bad = []
expansions = [n["fm"] for n in NOTES if n["fm"].get("type") == "field-expansion"]
for n in NOTES:
    fm, tv = n["fm"], n["fm"].get("type")
    if fm.get("layer") != "content":
        continue
    chain = ancestors(tv)
    effective = set(SERVICE)
    for key, p in PROPS.items():
        if any(a == "*" or a in chain for a in p["applies_to"]):
            effective.add(key)
    for key in RELS:
        effective.add(key)
    for rule_fm in expansions:
        applies = rule_fm.get("applies_to_type") or []
        applies = applies if isinstance(applies, list) else [applies]
        if not any(a in chain for a in applies):
            continue
        trig = rule_fm.get("trigger_property")
        values = fm.get(trig)
        values = values if isinstance(values, list) else ([values] if values is not None else [])
        tvs = rule_fm.get("trigger_values") or []
        tvs = tvs if isinstance(tvs, list) else [tvs]
        if not any(v in tvs for v in values):
            continue
        for key in (rule_fm.get("adds_properties") or []):
            effective.add(key)
        for key in (rule_fm.get("adds_relations") or []):
            effective.add(key)
    for key in fm:
        if key in SERVICE or key in effective:
            continue
        if fm[key] in (None, "", []):
            continue
        bad.append("%s: осиротевшее значение %s" % (n["file"], key))
rule(12, "inactive-field-value", bad)

# 14 deprecated-link-target
bad = []
for n in NOTES:
    if n["fm"].get("status") == "deprecated":
        continue
    for key, stem, _, is_db in links_of(n["fm"]):
        if is_db:
            continue
        target = BY_FILE.get(stem)
        if target and target["fm"].get("status") == "deprecated":
            bad.append("%s.%s -> %s" % (n["file"], key, stem))
rule(14, "deprecated-link-target", bad)

# 15 facet-target-is-facet
bad = []
for n in NOTES:
    if n["fm"].get("type") != "facet-value":
        continue
    value = n["fm"].get("facet")
    m = CANON.fullmatch(str(value)) if value else None
    if not m:
        bad.append("%s: ключ facet не каноническая ссылка" % n["file"])
        continue
    target = BY_FILE.get("%s_%s" % (m.group(1), m.group(2)))
    if target is None:
        bad.append("%s: цель facet вне набора" % n["file"])
    elif target["fm"].get("type") != "facet" or target["fm"].get("layer") != "classification":
        bad.append("%s: цель facet имеет type=%s layer=%s"
                   % (n["file"], target["fm"].get("type"), target["fm"].get("layer")))
    else:
        ok("правило 15 facet-target-is-facet: %s" % n["file"])
rule(15, "facet-target-is-facet", bad)

# 16 collection-element-consistent
PAIRS = {"film": "film-series", "track": "album", "image": "gallery"}
bad, pairs_seen = [], set()
for n in NOTES:
    tv = n["fm"].get("type")
    if tv not in PAIRS:
        continue
    values = n["fm"].get("part-of-collection")
    if values is None:
        continue
    values = values if isinstance(values, list) else [values]
    for v in values:
        m = CANON.fullmatch(str(v))
        if not m:
            bad.append("%s: значение не каноническая ссылка" % n["file"])
            continue
        target = BY_FILE.get("%s_%s" % (m.group(1), m.group(2)))
        if target is None:
            bad.append("%s: цель вне набора" % n["file"])
            continue
        pairs_seen.add((tv, target["fm"].get("type")))
        if target["fm"].get("type") != PAIRS[tv]:
            bad.append("%s: %s -> %s (ожидается %s)"
                       % (n["file"], tv, target["fm"].get("type"), PAIRS[tv]))
rule(16, "collection-element-consistent", bad)
check(pairs_seen == {("film", "film-series"), ("track", "album"), ("image", "gallery")},
      "матрица коллекций закрыта: %s" % sorted(pairs_seen))

# 17 relation-endpoints-match
bad, rel_uses = [], []
for n in NOTES:
    fm, tv = n["fm"], n["fm"].get("type")
    chain = ancestors(tv)
    for key in fm:
        if key not in RELS:
            continue
        r = RELS[key]
        rel_uses.append((n["file"], key))
        if r["source_type"] != ["*"]:
            if not any(a == "*" or a in chain for a in r["source_type"]):
                bad.append("%s: источник %s вне source_type %s отношения %s"
                           % (n["file"], tv, r["source_type"], key))
        elif fm.get("layer") != "content":
            bad.append("%s: источник вне слоя content при source_type *" % n["file"])
        values = fm[key] if isinstance(fm[key], list) else [fm[key]]
        for v in values:
            m = CANON.fullmatch(str(v))
            if not m:
                bad.append("%s.%s: значение не каноническая ссылка" % (n["file"], key))
                continue
            target = BY_FILE.get("%s_%s" % (m.group(1), m.group(2)))
            if target is None:
                continue
            tchain = ancestors(target["fm"].get("type"))
            if r["target_type"] != ["*"]:
                if not any(a == "*" or a in tchain for a in r["target_type"]):
                    bad.append("%s.%s: цель %s вне target_type %s"
                               % (n["file"], key, target["fm"].get("type"), r["target_type"]))
            elif target["fm"].get("layer") != "content":
                bad.append("%s.%s: цель вне слоя content при target_type *" % (n["file"], key))
rule(17, "relation-endpoints-match", bad, note=" (%d использований отношений)" % len(rel_uses))
used_keys = sorted({k for _, k in rel_uses})
check(len(used_keys) >= 7, "в наборе использовано отношений: %s" % used_keys)

# 18 relation-cardinality-form
bad, forms = [], {}
for n in NOTES:
    fm = n["fm"]
    for key in fm:
        if key not in RELS:
            continue
        card = RELS[key]["cardinality"]
        value = fm[key]
        is_list = isinstance(value, list)
        forms.setdefault(card, set()).add("список" if is_list else "одиночная")
        if card in ("0..1", "1..1") and is_list:
            bad.append("%s.%s: список при кратности %s" % (n["file"], key, card))
        if card in ("0..*", "1..*") and is_list and not value:
            bad.append("%s.%s: пустой список" % (n["file"], key))
        if card in ("1..1", "1..*") and (value is None or value == [] or value == ""):
            bad.append("%s.%s: нет значения при кратности %s" % (n["file"], key, card))
        if card in ("0..1", "1..1") and is_list is False and not str(value).strip():
            bad.append("%s.%s: пустое значение" % (n["file"], key))
rule(18, "relation-cardinality-form", bad)
check("одиночная" in forms.get("1..1", set()) and "список" in forms.get("0..*", set()),
      "показаны обе формы значения: %s" % {k: sorted(v) for k, v in forms.items()})

# 19 expansion-keys-exist
bad = []
for n in NOTES:
    fm = n["fm"]
    if fm.get("type") != "field-expansion":
        continue
    for t in (fm.get("applies_to_type") or []):
        if t not in TYPES:
            bad.append("%s: applies_to_type %s не существует" % (n["file"], t))
    tp = fm.get("trigger_property")
    if tp not in PROPS:
        bad.append("%s: trigger_property %s не существует" % (n["file"], tp))
    elif PROPS[tp]["value_type"] not in ("enum", "list<enum>"):
        bad.append("%s: trigger_property %s не перечисление" % (n["file"], tp))
    for p in (fm.get("adds_properties") or []):
        if p not in PROPS:
            bad.append("%s: adds_properties %s не существует" % (n["file"], p))
    for r in (fm.get("adds_relations") or []):
        if r not in RELS:
            bad.append("%s: adds_relations %s не существует" % (n["file"], r))
rule(19, "expansion-keys-exist", bad)

# ================================================= C. объекты правил третьей волны

print("=== C. Правила 15…19 как объекты validation-rule ===")
CUR[0] = "C"
WAVE3 = os.path.join(ROOT, "docs/validation/03-third-wave-rules.md")
w3_text = read(WAVE3)
blocks = re.findall(r"```yaml\n(.*?)```", w3_text, re.S)
check(len(blocks) == 5, "в 03-third-wave-rules.md пять YAML-блоков (найдено %d)" % len(blocks))
W3 = [parse_yaml(b) for b in blocks]
EXPECT_W3 = [
    ("facet-target-is-facet", "error", ["facet-value"], ["INV-15"]),
    ("collection-element-consistent", "warning", ["film", "track", "image"], ["DL-025"]),
    ("relation-endpoints-match", "error", "*", ["INV-17"]),
    ("relation-cardinality-form", "error", "*", ["INV-17"]),
    ("expansion-keys-exist", "error", ["field-expansion"], ["INV-25"]),
]
seen_ids = set()
for obj, (key, sev, applies, chk) in zip(W3, EXPECT_W3):
    errs = schema_errors(obj, "system-definitions.json")
    check(not errs, "%s: схема system-definitions.json (%s)" % (key, "; ".join(errs[:3]) if errs else "ok"))
    check(obj.get("rule_key") == key, "%s: rule_key" % key)
    check(obj.get("severity") == sev, "%s: severity %s" % (key, obj.get("severity")))
    check(obj.get("applies_to") == applies, "%s: applies_to %r" % (key, obj.get("applies_to")))
    check(obj.get("checks", [])[:1] == chk, "%s: checks[0] %r" % (key, obj.get("checks")))
    check(obj.get("type") == "validation-rule" and obj.get("layer") == "system"
          and obj.get("status") == "accepted" and obj.get("owner") == "human",
          "%s: type/layer/status/owner" % key)
    check(obj.get("defined_by") == "01a17d3b-4a04-7c70-99cd-5c01dddac8b4",
          "%s: defined_by — метатип validation-rule" % key)
    check(bool(UUID7.match(str(obj.get("id", "")))), "%s: id — UUIDv7" % key)
    check(obj.get("id") not in seen_ids, "%s: id уникален" % key)
    seen_ids.add(obj.get("id"))
    aliases = obj.get("aliases") or []
    check(aliases[:1] == [obj.get("title")] and aliases[1:2] == [key],
          "%s: aliases = [title, rule_key]" % key)
    check(len(str(obj.get("condition", ""))) > 80, "%s: condition содержательный" % key)
    check(len(str(obj.get("message", ""))) > 40, "%s: message содержательный" % key)
    check(all(isinstance(c, str) and c for c in obj.get("checks", [])), "%s: checks — список строк" % key)

# уникальность id правил третьей волны относительно волн 1–2
all_rule_ids = set(seen_ids)
for f in ("01-first-wave-rules.md", "02-second-wave-rules.md"):
    for b in re.findall(r"```yaml\n(.*?)```", read(os.path.join(ROOT, "docs/validation", f)), re.S):
        rid = parse_yaml(b).get("id")
        if rid:
            check(rid not in all_rule_ids, "%s: id %s не пересекается с третьей волной" % (f, rid))
            all_rule_ids.add(rid)

# разделы «Алгоритм» и «Границы» у каждого правила
check(w3_text.count("- **Алгоритм:**") == 5, "пять разделов «Алгоритм»")
check(w3_text.count("- **Границы:**") == 5, "пять разделов «Границы»")
check(w3_text.startswith("# Правила валидации: третья волна\n\n"), "H1 и вводный абзац (R-002)")

# --------------------------------------------- C2. схема для правил волн 1–2
PRE = []
for f in ("01-first-wave-rules.md", "02-second-wave-rules.md"):
    for b in re.findall(r"```yaml\n(.*?)```", read(os.path.join(ROOT, "docs/validation", f)), re.S):
        obj = parse_yaml(b)
        if obj.get("type") != "validation-rule":
            continue
        errs = schema_errors(obj, "system-definitions.json")
        if errs:
            PRE.append("%s / %s: %s" % (f, obj.get("rule_key"), "; ".join(errs[:2])))
        else:
            ok("%s / %s: схема" % (f, obj.get("rule_key")))

# ============================================================== D. документы

print("=== D. Документы: реестр, счётчики, ссылки ===")
CUR[0] = "D"
REG = os.path.join(ROOT, "docs/validation/00-validation-rules.md")
reg_text = read(REG)
rule_keys_docs = []
for f in ("01-first-wave-rules.md", "02-second-wave-rules.md", "03-third-wave-rules.md"):
    for b in re.findall(r"```yaml\n(.*?)```", read(os.path.join(ROOT, "docs/validation", f)), re.S):
        obj = parse_yaml(b)
        if obj.get("type") == "validation-rule":
            rule_keys_docs.append((f, obj))
check(len(rule_keys_docs) == 19, "в трёх файлах волн 19 правил (найдено %d)" % len(rule_keys_docs))

rows = {}
for row in md_table_rows(reg_text):
    if len(row) >= 4 and row[0].isdigit():
        keys = backticked(row[1])
        if keys:
            rows[int(row[0])] = (keys[0], row)
check(len(rows) == 19, "в реестре 00 §6 — 19 строк (найдено %d)" % len(rows))
for num, (f, obj) in enumerate(rule_keys_docs, start=1):
    if num not in rows:
        fail("реестр 00: нет строки %d" % num)
        continue
    key, row = rows[num]
    check(key == obj["rule_key"], "реестр 00 строка %d: rule_key %s" % (num, key))
    check(len(row) >= 6 and row[5].strip().strip("`") == obj["severity"],
          "реестр 00 строка %d: severity %s" % (num, row[5] if len(row) > 5 else "?"))
    applies_cell = row[4] if len(row) > 4 else ""
    at = obj["applies_to"]
    at = at if isinstance(at, list) else [at]
    expect_applies = ", ".join("`%s`" % a for a in at)
    check(applies_cell.strip() == expect_applies,
          "реестр 00 строка %d: applies_to %r (в правиле %r)" % (num, applies_cell.strip(), expect_applies))
    checks_cell = row[3] if len(row) > 3 else ""
    for c in obj.get("checks", []):
        check(c.strip("`") in checks_cell,
              "реестр 00 строка %d: checks содержит %s" % (num, c))
check("6.3" in reg_text, "реестр 00: есть подраздел 6.3 (третья волна)")
check("03-third-wave-rules.md" in reg_text, "реестр 00: ссылка на файл третьей волны")
cands = re.search(r"## 7\..*?(?=\n## |\Z)", reg_text, re.S)
check(cands is not None, "реестр 00: раздел 7 (кандидаты) присутствует")
if cands:
    cand_rows = md_table_rows(cands.group(0))
    cand_rows = [r for r in cand_rows if r and r[0] != "Кандидат"]
    check(len(cand_rows) == 14, "реестр 00 §7: 14 кандидатов (найдено %d)" % len(cand_rows))
    for key in ("facet-target-is-facet", "collection-element-consistent", "relation-endpoints-match",
                "relation-cardinality-form", "expansion-keys-exist"):
        check(key not in cands.group(0), "реестр 00 §7: %s исключён из кандидатов" % key)

# README examples
RDM = read(os.path.join(EXAMPLES_DIR, "README.md"))
check("03-third-wave-rules.md" in RDM, "README examples: ссылка на третью волну")
listed = {f for f in re.findall(r"\]\(([A-Za-z0-9_.\-]+\.md)\)", RDM) if "01a17d3b" in f}
present = {n["file"] for n in NOTES}
check(present <= listed, "README examples: все 19 файлов перечислены (нет %s)" % sorted(present - listed))
check("Девятнадцать заметок" in RDM or "19 заметок" in RDM, "README examples: счётчик заметок обновлён")
cov = re.search(r"## Покрытие правил валидации.*?(?=\n## )", RDM, re.S)
if cov:
    nums = [int(r[0]) for r in md_table_rows(cov.group(0)) if r and r[0].isdigit()]
    check(sorted(nums) == list(range(1, 20)), "README examples: таблица покрытия — строки 1…19 (%s)" % nums)
    for key in ("facet-target-is-facet", "collection-element-consistent", "relation-endpoints-match",
                "relation-cardinality-form", "expansion-keys-exist"):
        check(key in cov.group(0), "README examples: правило %s в таблице покрытия" % key)
for stem in sorted(present):
    check(stem in RDM, "README examples: упомянут %s" % stem)

# остальные документы
DOCS = {
    "brief": os.path.join(ROOT, "docs/PROJECT_BRIEF.md"),
    "map": os.path.join(ROOT, "docs/project-map/PROJECT_MAP.md"),
    "checkpoint": os.path.join(ROOT, "docs/CHECKPOINT.md"),
    "overview": os.path.join(ROOT, "docs/metamodel/00-overview.md"),
    "glossary": os.path.join(ROOT, "docs/glossary/glossary.md"),
    "dl": os.path.join(ROOT, "docs/decisions/decision-log.md"),
    "inv": os.path.join(ROOT, "docs/metamodel/01-invariants.md"),
    "props": os.path.join(ROOT, "docs/metamodel/04-properties.md"),
    "w1": os.path.join(ROOT, "docs/validation/01-first-wave-rules.md"),
    "w2": os.path.join(ROOT, "docs/validation/02-second-wave-rules.md"),
    "cprops": os.path.join(ROOT, "docs/metamodel/07-core-properties.md"),
}
TEXTS = {k: read(v) for k, v in DOCS.items()}
check("DL-048" in TEXTS["dl"], "decision-log: запись DL-048")
check("DL-049" in TEXTS["dl"], "decision-log: запись DL-049")
check("03-third-wave-rules.md" in TEXTS["overview"], "00-overview: ссылка на третью волну")
check("03-third-wave-rules.md" in TEXTS["map"], "PROJECT_MAP: ссылка на третью волну")
check("03-third-wave-rules.md" in TEXTS["brief"], "PROJECT_BRIEF: ссылка на третью волну")
check("Third wave" in TEXTS["glossary"] or "третья волна" in TEXTS["glossary"].lower(),
      "glossary: термин третьей волны")
check("третьей волны" in TEXTS["inv"], "01-invariants: упоминание третьей волны")
check("facet-target-is-facet" in TEXTS["props"], "04-properties: указание правила 15")
check("expansion-keys-exist" in TEXTS["w1"], "01-first-wave: указание правила 19")
check("relation-endpoints-match" in TEXTS["w2"] and "relation-cardinality-form" in TEXTS["w2"],
      "02-second-wave: указание правил 17 и 18")
check("facet-target-is-facet" in read(os.path.join(EXAMPLES_DIR, "facet-value_01a17d3b-6d02-7b27-8e19-5f2a74c93b18.md")),
      "пример facet-value: кандидат заменён правилом 15")
for name in ("19 правил", "19 эталон"):
    check(name in TEXTS["brief"], "PROJECT_BRIEF: счётчик «%s»" % name)
check("iter-013" in TEXTS["checkpoint"], "CHECKPOINT: итерация iter-013")

# указатели диапазона DL (R-007)
last_dl = max(int(m) for m in re.findall(r"^DL-(\d+) ", TEXTS["dl"], re.M))
check(last_dl == 49, "decision-log: последняя запись DL-%d" % last_dl)
for name in ("map", "overview", "glossary", "brief"):
    check("DL-049" in TEXTS[name], "%s: указатель диапазона DL включает DL-049 (R-007)" % name)
for name, fname in (("props", "04-properties.md"), ("cprops", "07-core-properties.md"),
                    ("w1", "01-first-wave-rules.md"), ("w2", "02-second-wave-rules.md")):
    pointers = [ln for ln in TEXTS[name].splitlines() if "decision-log.md" in ln or "решения —" in ln]
    check(bool(pointers) and all("DL-048" in ln for ln in pointers),
          "%s: указатели решений включают DL-048 (R-007)" % fname)

# ссылки в изменённых файлах разрешаются
CHANGED = [
    "docs/validation/03-third-wave-rules.md",
    "docs/validation/00-validation-rules.md",
    "examples/README.md",
    "docs/metamodel/01-invariants.md",
    "docs/metamodel/04-properties.md",
    "docs/metamodel/07-core-properties.md",
    "docs/validation/01-first-wave-rules.md",
    "docs/validation/02-second-wave-rules.md",
    "docs/glossary/glossary.md",
    "docs/project-map/PROJECT_MAP.md",
    "docs/metamodel/00-overview.md",
    "docs/PROJECT_BRIEF.md",
    "docs/CHECKPOINT.md",
    "docs/decisions/decision-log.md",
    "docs/_workflow/iterations/iter-013/REPORT.md",
] + ["examples/" + n["file"] for n in NOTES]
LINK = re.compile(r"\]\(([^)#\s]+)(#[^)]*)?\)")
for f in CHANGED:
    path = os.path.join(ROOT, f)
    if not os.path.exists(path):
        fail("нет файла %s" % f)
        continue
    text = read(path)
    base = os.path.dirname(path)
    broken = []
    for target, _anchor in LINK.findall(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        full = os.path.normpath(os.path.join(base, target))
        if not os.path.exists(full):
            broken.append(target)
    check(not broken, "%s: относительные ссылки (%s)" % (f, ", ".join(sorted(set(broken))[:4]) if broken else "ok"))

# плейсхолдеры и CJK-вкрапления в изменённых файлах
CJK = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
for f in CHANGED:
    path = os.path.join(ROOT, f)
    if os.path.exists(path):
        text = read(path)
        check("@@" not in text, "%s: плейсхолдеров @@ нет" % f)
        hits = CJK.findall(text)
        check(not hits, "%s: CJK-символов нет (%s)" % (f, "".join(hits[:4]) if hits else "ok"))

# R-006: объём файлов
for f in CHANGED:
    path = os.path.join(ROOT, f)
    if os.path.exists(path):
        lines = len(read(path).splitlines())
        if lines > 300:
            warn("%s: %d строк (>300, R-006)" % (f, lines))

# =============================================================== итог

print()
for line in PRE:
    print("НАБЛЮДЕНИЕ (принятые файлы, вне scope): %s" % line)
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
