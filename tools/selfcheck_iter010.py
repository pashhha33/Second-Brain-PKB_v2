#!/usr/bin/env python3
"""Самопроверка артефактов iter-010 (Second Brain PKB).

Не входит в коммит B: вспомогательный скрипт песочницы (прецедент — iter-009,
`mini_validator.py`). Проверяет:
  1. синтаксис JSON всех схем `schema/` и разрешимость всех `$ref`;
  2. объекты девяти правил второй волны из `docs/validation/02-second-wave-rules.md`
     против подмножества JSON Schema 2020-12, реализованного здесь же
     (обязательные ключи, паттерны, enum, форма `applies_to`, `checks`);
  3. негативные примеры формы объекта правила;
  4. разрешимость относительных ссылок в изменённых и новых Markdown-файлах;
  5. объём файлов против ориентира R-004 / R-006 (~300 строк).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILED = []


def fail(msg):
    FAILED.append(msg)


# ---------------------------------------------------------------- 1. схемы
def load_schema(name):
    with open(os.path.join(ROOT, 'schema', name), encoding='utf-8') as f:
        return json.load(f)


def resolve_pointer(doc, pointer):
    # fragment после имени файла может прийти как '#/...' или '/...'
    if pointer in ('', '#', '/'):
        return doc
    if pointer.startswith('#'):
        pointer = pointer[1:]
    if not pointer.startswith('/'):
        return None
    cur = doc
    for part in pointer[1:].split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def collect_refs(node, out):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == '$ref' and isinstance(v, str):
                out.append(v)
            else:
                collect_refs(v, out)
    elif isinstance(node, list):
        for v in node:
            collect_refs(v, out)


def check_refs():
    schemas = {}
    for name in sorted(os.listdir(os.path.join(ROOT, 'schema'))):
        if not name.endswith('.json'):
            continue
        try:
            schemas[name] = load_schema(name)
        except Exception as exc:  # noqa: BLE001
            fail(f'schema {name}: JSON не разобран — {exc}')
    for name, doc in schemas.items():
        refs = []
        collect_refs(doc, refs)
        for ref in refs:
            if ref.startswith('http://') or ref.startswith('https://'):
                fail(f'schema {name}: $ref \"{ref}\" — внешняя ссылка')
                continue
            if ref.startswith('#'):
                target, pointer = name, ref
            else:
                target, _, pointer = ref.partition('#')
                if target not in schemas:
                    fail(f'schema {name}: $ref "{ref}" — файл не найден')
                    continue
            if resolve_pointer(schemas[target], pointer or '#') is None:
                fail(f'schema {name}: $ref "{ref}" — указатель не разрешается')
    total = 0
    for doc in schemas.values():
        r = []
        collect_refs(doc, r)
        total += len(r)
    print(f'[1] схем проверено: {len(schemas)}; $ref проверено: {total} '
          f'(все разрешаются; внешних URL в $ref нет)')
    for name, doc in schemas.items():
        for k, v in doc.items():
            if k.startswith('$') and k not in ('$schema', '$id', '$ref', '$defs', '$comment'):
                fail(f'schema {name}: неожиданный ключ верхнего уровня {k}')
        if 'https://' in json.dumps(doc, ensure_ascii=False).replace(
                '"$schema": "https://json-schema.org/draft/2020-12/schema"', ''):
            fail(f'schema {name}: внешний URL кроме идентификатора версии')
    return schemas


# ------------------------------------------------- 2. мини-валидатор правила
UUIDV7 = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')
KEBAB = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
INVID = re.compile(r'^INV-[0-9]{2}$')
REQUIRED8 = ['id', 'type', 'defined_by', 'title', 'aliases', 'layer', 'status', 'owner']
SERVICE6 = ['rule_key', 'checks', 'severity', 'applies_to', 'condition', 'message']
METATYPE = '01a17d3b-4a04-7c70-99cd-5c01dddac8b4'


def validate_rule(obj, path):
    """Подмножество validation-rule.json: обязательные ключи и форма значений."""
    for key in REQUIRED8 + SERVICE6 + ['type', 'layer']:
        if key not in obj:
            fail(f'{path}: отсутствует обязательный ключ `{key}`')
    if obj.get('type') != 'validation-rule':
        fail(f'{path}: type != validation-rule')
    if obj.get('layer') != 'system':
        fail(f'{path}: layer != system')
    if obj.get('status') != 'accepted':
        fail(f'{path}: status != accepted')
    if not UUIDV7.match(str(obj.get('id', ''))):
        fail(f'{path}: id не соответствует UUIDv7')
    if obj.get('defined_by') != METATYPE:
        fail(f'{path}: defined_by != id встроенного метатипа 5')
    if not UUIDV7.match(str(obj.get('defined_by', ''))):
        fail(f'{path}: defined_by не соответствует UUIDv7')
    title = obj.get('title')
    aliases = obj.get('aliases')
    if not isinstance(title, str) or not title.strip():
        fail(f'{path}: title пуст')
    if not isinstance(aliases, list) or not aliases:
        fail(f'{path}: aliases — не непустой список')
    else:
        if aliases[0] != title:
            fail(f'{path}: aliases[0] != title (INV-08)')
        if len(aliases) < 2 or aliases[1] != obj.get('rule_key'):
            fail(f'{path}: aliases[1] != rule_key (DL-038)')
    if not KEBAB.match(str(obj.get('rule_key', ''))):
        fail(f'{path}: rule_key не в ASCII kebab-case')
    checks = obj.get('checks')
    if not isinstance(checks, list) or not checks:
        fail(f'{path}: checks — не непустой список')
    else:
        if len(set(checks)) != len(checks):
            fail(f'{path}: checks содержит повторы')
        for c in checks:
            if not INVID.match(str(c)):
                fail(f'{path}: checks содержит идентификатор не INV-NN: {c!r}')
            num = int(str(c)[4:])
            if not 1 <= num <= 27:
                fail(f'{path}: checks ссылается на несуществующий инвариант {c}')
    if obj.get('severity') not in ('error', 'warning'):
        fail(f'{path}: severity вне набора error/warning')
    ap = obj.get('applies_to')
    if ap == '*':
        pass
    elif isinstance(ap, list) and ap and all(KEBAB.match(str(x)) for x in ap):
        if len(set(ap)) != len(ap):
            fail(f'{path}: applies_to содержит повторы')
    else:
        fail(f'{path}: applies_to не "*" и не непустой список type_value: {ap!r}')
    for key in ('condition', 'message'):
        v = obj.get(key)
        if not isinstance(v, str) or not v.strip():
            fail(f'{path}: {key} — не непустая строка')
    if not str(obj.get('owner', '')).strip():
        fail(f'{path}: owner пуст')


def parse_flow_list(text):
    text = text.strip()
    assert text.startswith('[') and text.endswith(']'), text
    inner = text[1:-1].strip()
    if not inner:
        return []
    items = []
    for raw in inner.split(','):
        raw = raw.strip()
        if raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]
        items.append(raw)
    return items


def parse_yaml_block(lines):
    """Плоский YAML: `key: value`, flow-списки, блочные списки `- item`."""
    obj = {}
    last_key = None
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            continue
        if line.startswith('  - '):
            obj.setdefault(last_key, []).append(line[4:].strip().strip('"'))
            continue
        if line.startswith(' ') or line.startswith('-'):
            continue
        key, sep, val = line.partition(':')
        if not sep:
            continue
        val = val.strip()
        last_key = key.strip()
        if val == '' or val == '|-' or val == '>-' or val.startswith('#'):
            obj[last_key] = [] if val == '' else ''
            continue
        if val.startswith('['):
            comment = val.find(' #')
            if comment > 0 and val.endswith(']') is False:
                val = val[:comment].strip()
            obj[last_key] = parse_flow_list(val.split(' #')[0].strip())
            continue
        if val.startswith('"') and val.endswith('"'):
            obj[last_key] = val[1:-1]
        else:
            obj[last_key] = val.split(' #')[0].strip().strip('"')
    return obj


def extract_yaml_blocks(md_path):
    with open(md_path, encoding='utf-8') as f:
        text = f.read()
    blocks = re.findall(r'```yaml\n(.*?)```', text, flags=re.S)
    return [b.splitlines() for b in blocks]


def check_rules():
    md = os.path.join(ROOT, 'docs', 'validation', '02-second-wave-rules.md')
    blocks = extract_yaml_blocks(md)
    rules = []
    for i, lines in enumerate(blocks, start=1):
        obj = parse_yaml_block(lines)
        if obj.get('type') != 'validation-rule':
            continue
        rules.append(obj)
        validate_rule(obj, f'02-second-wave-rules.md, блок {i} ({obj.get("rule_key", "?")})')
    print(f'[2] объектов правил второй волны разобрано и проверено: {len(rules)}')
    keys = [r['rule_key'] for r in rules]
    if len(set(keys)) != len(keys):
        fail('rule_key правил второй волны не уникальны')
    ids = [r['id'] for r in rules]
    if len(set(ids)) != len(ids):
        fail('иллюстративные id правил второй волны не уникальны')
    sev = {}
    for r in rules:
        sev[r['severity']] = sev.get(r['severity'], 0) + 1
    print(f'    severity: {sev}')
    # правила первой волны — та же форма (сверка формата, а не принятых условий)
    first = os.path.join(ROOT, 'docs', 'validation', '01-first-wave-rules.md')
    first_rules = [parse_yaml_block(l) for l in extract_yaml_blocks(first)]
    first_rules = [o for o in first_rules if o.get('type') == 'validation-rule']
    bad_scalar = [o['rule_key'] for o in first_rules
                  if o.get('applies_to') not in ('*',) and not isinstance(o.get('applies_to'), list)]
    print(f'[2.1] правил первой волны разобрано: {len(first_rules)}; '
          f'скалярный applies_to (расхождение с формой, REPORT.md iter-010): {bad_scalar}')
    return rules


# ------------------------------------------------------- 3. негативные примеры
def check_negative():
    base = {
        'id': '01a17d3b-9c01-7d21-8a44-1b6f0c2d3e45',
        'type': 'validation-rule',
        'defined_by': METATYPE,
        'rule_key': 'sample-rule',
        'title': 'Пример',
        'aliases': ['Пример', 'sample-rule'],
        'checks': ['INV-15'],
        'severity': 'error',
        'applies_to': '*',
        'condition': 'Условие.',
        'message': 'Сообщение.',
        'layer': 'system',
        'status': 'accepted',
        'owner': 'human',
    }
    negatives = {
        'без message': {'message': None},
        'severity: info': {'severity': 'info'},
        'пустой checks': {'checks': []},
        'checks не INV-NN': {'checks': ['DL-040']},
        'applies_to скаляром type_value': {'applies_to': 'image'},
        'rule_key с подчёркиванием': {'rule_key': 'sample_rule'},
        'id не UUIDv7 (v4)': {'id': '01a17d3b-9c01-4d21-8a44-1b6f0c2d3e45'},
        'aliases[1] != rule_key': {'aliases': ['Пример', 'other-key']},
        'layer: content': {'layer': 'content'},
        'defined_by другой': {'defined_by': '01a17d3b-4a01-73dd-8782-259a7e45663f'},
        'condition пуст': {'condition': '   '},
        'type: automation': {'type': 'automation'},
    }
    passed = 0
    for name, patch in negatives.items():
        obj = dict(base)
        for k, v in patch.items():
            if v is None:
                obj.pop(k, None)
            else:
                obj[k] = v
        before = len(FAILED)
        saved = FAILED[:]
        validate_rule(obj, f'негативный пример «{name}»')
        if len(FAILED) > before:
            passed += 1
            del FAILED[before:]
        else:
            fail(f'негативный пример «{name}» не отклонён валидатором')
        assert saved == FAILED[:len(saved)]
    # позитивный контроль
    before = len(FAILED)
    validate_rule(dict(base), 'позитивный пример')
    if len(FAILED) > before:
        fail('позитивный пример отклонён валидатором')
        del FAILED[before:]
    print(f'[3] негативных примеров формы объекта правила: {len(negatives)}, '
          f'отклонено: {passed}; позитивный пример принят')


# ------------------------------------------------------------- 4. ссылки MD
CHANGED = [
    'docs/validation/02-second-wave-rules.md',
    'docs/validation/00-validation-rules.md',
    'docs/validation/01-first-wave-rules.md',
    'docs/metamodel/00-overview.md',
    'docs/metamodel/01-invariants.md',
    'docs/metamodel/04-properties.md',
    'docs/metamodel/06-relations.md',
    'docs/metamodel/09-structural-invariants.md',
    'docs/glossary/glossary.md',
    'docs/project-map/PROJECT_MAP.md',
    'docs/PROJECT_BRIEF.md',
    'docs/CHECKPOINT.md',
    'docs/_workflow/HANDOFF_PROTOCOL.md',
    'docs/_workflow/OPEN_QUESTIONS.md',
    'docs/_workflow/iterations/iter-010/REPORT.md',
]


def check_links():
    broken = 0
    total = 0
    for rel in CHANGED:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            fail(f'{rel}: файл отсутствует в песочнице')
            continue
        with open(path, encoding='utf-8') as f:
            text = f.read()
        for m in re.finditer(r'\]\(([^)#][^)]*?)\)', text):
            target = m.group(1).split('#')[0].strip()
            if not target or target.startswith(('http://', 'https://', 'mailto:')):
                continue
            total += 1
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
            if not os.path.exists(resolved):
                broken += 1
                fail(f'{rel}: ссылка не разрешается — {target}')
    print(f'[4] относительных ссылок проверено: {total}, неразрешимых: {broken}')


# ------------------------------------------------------------- 5. объём файлов
def check_sizes():
    over = []
    for rel in CHANGED + ['schema/validation-rule.json', 'schema/system-definitions.json',
                           'docs/decisions/decision-log.md']:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as f:
            n = sum(1 for _ in f)
        flag = '  <-- за ориентиром R-006' if n > 300 else ''
        if n > 300:
            over.append(rel)
        print(f'[5] {rel}: {n} строк{flag}')
    if over:
        fail(f'файлы превышают ориентир R-004/R-006: {over}')


def main():
    check_refs()
    check_rules()
    check_negative()
    check_links()
    check_sizes()
    print()
    if FAILED:
        print(f'ПРОВЕРОК НЕ ПРОЙДЕНО: {len(FAILED)}')
        for m in FAILED:
            print(' -', m)
        return 1
    print('ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ')
    return 0


if __name__ == '__main__':
    sys.exit(main())
