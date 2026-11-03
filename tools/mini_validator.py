# -*- coding: utf-8 -*-
"""Мини-валидатор подмножества JSON Schema 2020-12 — артефакт самопроверки итерации iter-009.

В репозиторий и в коммит B не входит: исполняемый валидатор — фазы 4-5 (вне scope TASK.md iter-009).
Поддержаны: $ref (внутри файла и между файлами каталога), $defs, type, properties, required,
additionalProperties, items, minItems, minLength, pattern, enum, const, allOf, anyOf, oneOf, not,
if/then/else. Реализован только для контроля схем первой волны, а не как замена jsonschema.
"""
import io, json, re, os, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SCHEMA_DIR", "schema")
cache = {}
def load(name):
    if name not in cache:
        cache[name] = json.load(io.open(os.path.join(ROOT, name), encoding="utf-8"))
    return cache[name]

def resolve(node, base):
    """Возвращает (schema, base) после разыменования $ref (внутри файла и между файлами)."""
    seen = 0
    while isinstance(node, dict) and "$ref" in node and len(node) == 1:
        seen += 1
        if seen > 50: raise RuntimeError("цикл в $ref")
        ref = node["$ref"]
        if ref.startswith("#"):
            fname, frag = base, ref[1:]
        else:
            fname, _, frag = ref.partition("#")
        cur = load(fname)
        if frag:
            for part in frag.lstrip("/").split("/"):
                cur = cur[part]
        node, base = cur, fname
    return node, base

def merge_ref(node, base):
    """Схема может содержать $ref рядом с другими ключами (2020-12): объединяем allOf-семантикой."""
    if isinstance(node, dict) and "$ref" in node and len(node) > 1:
        rest = {k: v for k, v in node.items() if k != "$ref"}
        return {"allOf": [{"$ref": node["$ref"]}, rest]}, base
    return node, base

TYPEMAP = {"object": dict, "array": list, "string": str, "boolean": bool}

def validate(inst, schema, base, path="$", errors=None):
    if errors is None: errors = []
    schema, base = merge_ref(*resolve(schema, base))
    if not isinstance(schema, dict): return errors
    if "const" in schema and inst != schema["const"]:
        errors.append("%s: const %r != %r" % (path, schema["const"], inst))
    if "enum" in schema and inst not in schema["enum"]:
        errors.append("%s: %r не входит в enum" % (path, inst))
    t = schema.get("type")
    if t:
        ok = (isinstance(inst, TYPEMAP[t]) and not (t == "number" and isinstance(inst, bool))
              and not (t == "string" and not isinstance(inst, str))
              and not (t in ("object","array","boolean") and isinstance(inst, bool) and t != "boolean"))
        if t == "number": ok = isinstance(inst, (int, float)) and not isinstance(inst, bool)
        if t == "string": ok = isinstance(inst, str)
        if t == "object": ok = isinstance(inst, dict)
        if t == "array": ok = isinstance(inst, list)
        if t == "boolean": ok = isinstance(inst, bool)
        if not ok:
            errors.append("%s: ожидался %s, получено %r" % (path, t, inst)); return errors
    if isinstance(inst, str) and "pattern" in schema and not re.search(schema["pattern"], inst):
        errors.append("%s: %r не соответствует pattern %s" % (path, inst, schema["pattern"]))
    if isinstance(inst, str):
        if "minLength" in schema and len(inst) < schema["minLength"]: errors.append("%s: minLength" % path)
        if "maxLength" in schema and len(inst) > schema["maxLength"]: errors.append("%s: maxLength" % path)
    if isinstance(inst, list):
        if "minItems" in schema and len(inst) < schema["minItems"]: errors.append("%s: minItems" % path)
        if schema.get("uniqueItems") and len(set(map(repr, inst))) != len(inst): errors.append("%s: uniqueItems" % path)
        if "items" in schema:
            for i, el in enumerate(inst): validate(el, schema["items"], base, "%s[%d]" % (path, i), errors)
    if isinstance(inst, dict):
        for r in schema.get("required", []):
            if r not in inst: errors.append("%s: нет обязательного ключа %r" % (path, r))
        for k, sub in schema.get("properties", {}).items():
            if k in inst: validate(inst[k], sub, base, "%s.%s" % (path, k), errors)
        if "if" in schema:
            cond_err = validate(inst, schema["if"], base, path + "/if", [])
            branch = "then" if not cond_err else ("else" if "else" in schema else None)
            if branch: validate(inst, schema[branch], base, path + "/" + branch, errors)
    if "not" in schema:
        if not validate(inst, schema["not"], base, path + "/not", []):
            errors.append("%s: not — условие выполнилось, а должно нет" % path)
    for key in ("allOf", "anyOf", "oneOf"):
        if key in schema:
            subs = schema[key]; results = [validate(inst, s, base, "%s/%s[%d]" % (path, key, i), []) for i, s in enumerate(subs)]
            if key == "allOf":
                for r in results: errors.extend(r)
            elif key == "anyOf":
                if not any(len(r) == 0 for r in results):
                    errors.append("%s: anyOf не выполнен: %s" % (path, results[0][:2]))
            else:
                n = sum(1 for r in results if not r)
                if n != 1: errors.append("%s: oneOf — подходящих веток %d" % (path, n))
    return errors

def check(name, inst, schema_file, expect_ok):
    errs = validate(inst, load(schema_file), schema_file)
    errs = [e for e in errs if "/if" not in e]
    status = "OK " if (not errs) == expect_ok else "!! "
    print("%s%-46s %s" % (status, name, "валиден" if not errs else "; ".join(errs[:2])[:150]))
    return (not errs) == expect_ok
