#!/usr/bin/env python3
"""Самопроверка артефактов iter-011 (Second Brain PKB).

Не входит в коммит B: вспомогательный скрипт песочницы, каталог `tools/`
игнорируется `.gitignore` (прецедент — iter-009 `mini_validator.py`,
iter-010 `selfcheck_iter010.py`). Зависимостей кроме стандартной библиотеки
нет: `jsonschema` и `yaml` в песочнице недоступны, поэтому реализовано
подмножество JSON Schema 2020-12 и разбор простых YAML-фрагментов документов.

Проверяет:
  1. синтаксис JSON всех схем `schema/`, разрешимость всех `$ref`, отсутствие
     внешних URL кроме идентификатора версии, состав ключей верхнего уровня;
  2. мини-валидатор: поддержка ключевых слов, использованных в пяти схемах;
  3. `schema/facet-value.json` на каноническом примере `04-properties.md`,
     раздел 6, и на негативных примерах;
  4. `schema/core-property-values.json` на YAML-фрагменте
     `07-core-properties.md`, раздел 2, и на негативных примерах;
  5. пятнадцать `$defs` форм значений: позитивный и негативный пример на форму;
  6. регрессия первой волны: `object.json` и `media.json` на своих примерах;
  7. сверка схем с реестрами: 23 ключа и `value_type` из
     `07-core-properties.md`, 12 ключей схемы, соответствие `value_type` →
     `$defs`, отсутствие `enum` / наборов `enum_values` в схеме;
  8. Markdown: разрешение относительных ссылок, указатели диапазонов DL,
     состав `decision-log.md`, счётчик кандидатов третьей волны, R-002
     (H1 + вводный абзац) для нового ADR, отсутствие CJK-символов,
     объём файлов против ориентира R-004 / R-006 (~300 строк);
  9. дерево: отсутствие `iter-*.patch`, наличие `iter-*.patch` в `.gitignore`.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Ожидаемый максимальный номер записи журнала решений: 45 — состояние после
# iter-011; скрипт iter-012 повышает значение до 47 перед вызовом
# check_markdown (DL-046, DL-047), чтобы регрессия первой и второй волн
# выполнялась на актуальном дереве.
MAX_DL_EXPECTED = 45
FAILED = []
INFO = []


def fail(msg):
    FAILED.append(msg)


def info(msg):
    INFO.append(msg)


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding='utf-8') as f:
        return f.read()


# ------------------------------------------------------------------ 1. схемы
SCHEMA_DIR = os.path.join(ROOT, 'schema')
SCHEMAS = {}
VERSION_ID = '"$schema": "https://json-schema.org/draft/2020-12/schema"'
TOP_LEVEL_OK = {'$schema', '$id', 'title', 'description', '$ref', '$defs',
                'type', 'properties', 'required', 'allOf', 'anyOf', 'oneOf',
                '$comment'}


def load_schemas():
    for name in sorted(os.listdir(SCHEMA_DIR)):
        if not name.endswith('.json'):
            continue
        try:
            with open(os.path.join(SCHEMA_DIR, name), encoding='utf-8') as f:
                SCHEMAS[name] = json.load(f)
        except Exception as exc:  # noqa: BLE001
            fail(f'схема {name}: JSON не разобран — {exc}')
    for name, doc in SCHEMAS.items():
        for key in doc:
            if key not in TOP_LEVEL_OK:
                fail(f'схема {name}: неожиданный ключ верхнего уровня `{key}`')
        if doc.get('$id') != name:
            fail(f'схема {name}: $id = {doc.get("$id")!r}, ожидалось имя файла')
        if doc.get('$schema') != 'https://json-schema.org/draft/2020-12/schema':
            fail(f'схема {name}: $schema не равен идентификатору 2020-12')
        raw = read('schema', name).replace(VERSION_ID, '')
        for m in re.finditer(r'https?://[^\s"\\]+', raw):
            fail(f'схема {name}: внешний URL `{m.group(0)}`')


def resolve_pointer(doc, pointer):
    """Указатель JSON: допустимы формы '#', '#/a/b', '/a/b', ''."""
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


def collect_defs(node, out):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == '$defs' and isinstance(v, dict):
                out.update(v)
            collect_defs(v, out)
    elif isinstance(node, list):
        for v in node:
            collect_defs(v, out)


def check_refs():
    total = 0
    for name, doc in SCHEMAS.items():
        refs = []
        collect_refs(doc, refs)
        total += len(refs)
        for ref in refs:
            if ref.startswith(('http://', 'https://')):
                fail(f'схема {name}: $ref "{ref}" — внешняя ссылка')
                continue
            target, _, pointer = ref.partition('#')
            target = target or name
            if target not in SCHEMAS:
                fail(f'схема {name}: $ref "{ref}" — файл не найден')
                continue
            if resolve_pointer(SCHEMAS[target], '#' + pointer if pointer else '#') is None:
                fail(f'схема {name}: $ref "{ref}" — указатель не разрешается')
    print(f'[1] схем: {len(SCHEMAS)} ({", ".join(sorted(SCHEMAS))}); '
          f'$ref проверено: {total} — все разрешаются, внешних URL нет')
    # все $defs новых схем должны использоваться
    for name in ('facet-value.json', 'core-property-values.json'):
        defs = {}
        collect_defs(SCHEMAS[name], defs)
        refs = []
        collect_refs(SCHEMAS[name], refs)
        used = {r.partition('#')[2] for r in refs if r.startswith('#')}
        for d in sorted(defs):
            if f'/$defs/{d}' not in used:
                # определение может использоваться другой схемой — фиксируем как справку
                info(f'схема {name}: $defs/{d} не используется внутри файла')
        print(f'[1] {name}: $defs — {len(defs)}, внутренних $ref — {len(refs)}')


# ------------------------------------------------- 2. мини-валидатор 2020-12
SUPPORTED = {
    '$ref', '$defs', '$id', '$schema', '$comment', 'title', 'description',
    'type', 'enum', 'const', 'pattern', 'format', 'minLength', 'maxLength',
    'minimum', 'maximum', 'exclusiveMinimum', 'exclusiveMaximum', 'multipleOf',
    'required', 'properties', 'additionalProperties', 'patternProperties',
    'propertyNames', 'items', 'prefixItems', 'contains', 'minItems', 'maxItems',
    'uniqueItems', 'allOf', 'anyOf', 'oneOf', 'not', 'if', 'then', 'else',
    'dependentRequired', 'dependencies',
}
UNSUPPORTED = set()


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def is_integer(v):
    return (isinstance(v, int) and not isinstance(v, bool)) or \
        (isinstance(v, float) and v.is_integer())


def type_ok(v, t):
    return {
        'string': lambda x: isinstance(x, str),
        'number': is_number,
        'integer': is_integer,
        'boolean': lambda x: isinstance(x, bool),
        'array': lambda x: isinstance(x, list),
        'object': lambda x: isinstance(x, dict),
        'null': lambda x: x is None,
    }[t](v)


def resolve_ref(ref, current_file):
    target, _, pointer = ref.partition('#')
    target = target or current_file
    if target not in SCHEMAS:
        fail(f'$ref "{ref}": файл схемы не найден')
        return None, current_file
    node = resolve_pointer(SCHEMAS[target], '#' + pointer if pointer else '#')
    if node is None:
        fail(f'$ref "{ref}": указатель не разрешается')
        return None, current_file
    return node, target


def validate(inst, schema, current_file, path, errors):
    """Подмножество JSON Schema 2020-12. Возвращает None; ошибки — в errors."""
    if not isinstance(schema, dict):
        return
    for key in schema:
        if key not in SUPPORTED:
            UNSUPPORTED.add(key)
    if '$ref' in schema:
        sub, target = resolve_ref(schema['$ref'], current_file)
        if sub is not None:
            validate(inst, sub, target, path, errors)
        # в 2020-12 соседи $ref применяются вместе со ссылкой
    if 'type' in schema:
        types = schema['type'] if isinstance(schema['type'], list) else [schema['type']]
        if not any(type_ok(inst, t) for t in types):
            errors.append(f'{path}: тип {type(inst).__name__} не входит в {types}')
            return
    if 'const' in schema and inst != schema['const']:
        errors.append(f'{path}: значение {inst!r} != const {schema["const"]!r}')
    if 'enum' in schema and inst not in schema['enum']:
        errors.append(f'{path}: значение {inst!r} не входит в enum {schema["enum"]}')
    if isinstance(inst, str):
        if 'pattern' in schema and not re.search(schema['pattern'], inst):
            errors.append(f'{path}: {inst!r} не соответствует шаблону {schema["pattern"]!r}')
        if 'minLength' in schema and len(inst) < schema['minLength']:
            errors.append(f'{path}: длина строки меньше {schema["minLength"]}')
        if 'maxLength' in schema and len(inst) > schema['maxLength']:
            errors.append(f'{path}: длина строки больше {schema["maxLength"]}')
    if is_number(inst):
        if 'minimum' in schema and inst < schema['minimum']:
            errors.append(f'{path}: {inst} < minimum {schema["minimum"]}')
        if 'maximum' in schema and inst > schema['maximum']:
            errors.append(f'{path}: {inst} > maximum {schema["maximum"]}')
    if isinstance(inst, list):
        if 'minItems' in schema and len(inst) < schema['minItems']:
            errors.append(f'{path}: элементов {len(inst)} < minItems {schema["minItems"]}')
        if 'maxItems' in schema and len(inst) > schema['maxItems']:
            errors.append(f'{path}: элементов {len(inst)} > maxItems {schema["maxItems"]}')
        if schema.get('uniqueItems'):
            seen = [json.dumps(x, ensure_ascii=False, sort_keys=True) for x in inst]
            if len(set(seen)) != len(seen):
                errors.append(f'{path}: элементы не уникальны (uniqueItems)')
        if 'items' in schema and isinstance(schema['items'], dict):
            for i, item in enumerate(inst):
                validate(item, schema['items'], current_file, f'{path}[{i}]', errors)
        if 'prefixItems' in schema:
            for i, sub in enumerate(schema['prefixItems']):
                if i < len(inst):
                    validate(inst[i], sub, current_file, f'{path}[{i}]', errors)
    if isinstance(inst, dict):
        for key in schema.get('required', []):
            if key not in inst:
                errors.append(f'{path}: отсутствует обязательный ключ `{key}`')
        for key, sub in schema.get('properties', {}).items():
            if key in inst:
                validate(inst[key], sub, current_file, f'{path}.{key}', errors)
        if 'additionalProperties' in schema and schema['additionalProperties'] is False:
            allowed = set(schema.get('properties', {}))
            for key in inst:
                if key not in allowed:
                    errors.append(f'{path}: незадекларированный ключ `{key}`')
        if 'propertyNames' in schema:
            for key in inst:
                validate(key, schema['propertyNames'], current_file, f'{path}.<key {key}>', errors)
    for comb in ('allOf', 'anyOf', 'oneOf'):
        if comb in schema:
            subs = schema[comb]
            matched = []
            for i, sub in enumerate(subs):
                errs = []
                validate(inst, sub, current_file, path, errs)
                if not errs:
                    matched.append(i)
                elif comb == 'allOf':
                    errors.extend(errs)
            if comb == 'anyOf' and not matched:
                errors.append(f'{path}: ни одна ветвь anyOf не подошла')
            if comb == 'oneOf' and len(matched) != 1:
                errors.append(f'{path}: oneOf — подошло ветвей: {len(matched)} (ожидалась 1)')
    if 'not' in schema:
        errs = []
        validate(inst, schema['not'], current_file, path, errs)
        if not errs:
            errors.append(f'{path}: значение прошло проверку `not`')
    if 'if' in schema:
        errs = []
        validate(inst, schema['if'], current_file, path, errs)
        branch = 'then' if not errs else 'else'
        if branch in schema:
            validate(inst, schema[branch], current_file, path, errors)


def validate_with(schema_file, inst, pointer='#'):
    """Валидация экземпляра схемой; возвращает список ошибок."""
    errors = []
    doc = SCHEMAS[schema_file]
    if pointer != '#':
        doc = resolve_pointer(SCHEMAS[schema_file], pointer)
        if doc is None:
            fail(f'{schema_file}{pointer}: указатель не разрешается')
            return ['указатель не разрешается']
    validate(inst, doc, schema_file, '$', errors)
    return errors


CHECKS = 0


def expect_ok(name, schema_file, inst, pointer='#'):
    global CHECKS
    CHECKS += 1
    errs = validate_with(schema_file, inst, pointer)
    if errs:
        fail(f'{name}: ожидалась валидность, получены ошибки: {errs[:3]}')


def expect_bad(name, schema_file, inst, pointer='#'):
    global CHECKS
    CHECKS += 1
    errs = validate_with(schema_file, inst, pointer)
    if not errs:
        fail(f'{name}: ожидалась невалидность, ошибок нет')


# ------------------------------------------------------- 3. разбор YAML-блоков
def yaml_blocks(text):
    return re.findall(r'```yaml\n(.*?)```', text, re.S)


def strip_comment(line):
    if line.lstrip().startswith('#'):
        return ''
    m = re.search(r'\s#', line)
    return line[:m.start()] if m else line


def parse_scalar(raw):
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in '"\'':
        return s[1:-1]
    if re.fullmatch(r'-?\d+', s):
        return int(s)
    if re.fullmatch(r'-?\d+\.\d+', s):
        return float(s)
    if s == 'true':
        return True
    if s == 'false':
        return False
    if s in ('null', '~', ''):
        return None
    return s


def parse_yaml(block):
    """Одноуровневые отображения и списки скаляров — этого достаточно для
    канонических примеров документов метамодели."""
    out = {}
    key = None
    for raw_line in block.splitlines():
        line = strip_comment(raw_line).rstrip()
        if not line.strip():
            continue
        if line.startswith('  - '):
            out.setdefault(key, []).append(parse_scalar(line[4:]))
            continue
        if line.startswith(' '):
            fail(f'parse_yaml: неожиданный отступ в строке {line!r}')
            continue
        if ':' not in line:
            fail(f'parse_yaml: строка без ключа {line!r}')
            continue
        k, _, v = line.partition(':')
        key = k.strip()
        if v.strip():
            out[key] = parse_scalar(v)
        else:
            out[key] = []
    return out


def pick_block(text, marker, label):
    for block in yaml_blocks(text):
        if marker in block:
            return parse_yaml(block)
    fail(f'{label}: YAML-блок с маркером {marker!r} не найден')
    return {}


# ------------------------------------------- 4. примеры и проверки facet-value
FV_FILE = 'facet-value.json'
FV_DEF = '#/$defs/facet-value'
FACET_ID = '01a17d3b-4a28-744e-a519-67031a8e0ae5'
FV_ID = '01a17d3b-4a29-72b4-9a57-be1a133ebf6f'
METATYPE9 = '01a17d3b-4a08-7875-996d-c4af6179a249'
IMAGE_ID = '01a17d3b-6b30-7f11-9c42-6a2f7d1e5b84'
PERSON_ID = '01a17d3b-4e04-7d44-8e04-444444444444'


def check_facet_value():
    text = read('docs', 'metamodel', '04-properties.md')
    example = pick_block(text, 'type: facet-value', '04-properties.md, раздел 6')
    if example:
        expect_ok('канонический пример 04-properties.md раздел 6', FV_FILE, example)
        expect_ok('тот же пример против object.json (первая волна)', 'object.json', example)
        for key in ('id', 'type', 'defined_by', 'facet', 'title', 'aliases',
                    'layer', 'status', 'owner'):
            if key not in example:
                fail(f'пример 04-properties.md: нет ключа `{key}`')
        if example.get('type') != 'facet-value' or example.get('layer') != 'classification':
            fail('пример 04-properties.md: type / layer не соответствуют схеме')
    neg = {
        'без ключа facet': lambda d: d.pop('facet'),
        'type = facet': lambda d: d.update(type='facet'),
        'layer = content': lambda d: d.update(layer='content'),
        'facet строкой без ссылки': lambda d: d.update(facet='Формат'),
        'facet ссылкой на домен': lambda d: d.update(
            facet=f'[[domain_{FACET_ID}|Область]]'),
        'facet списком': lambda d: d.update(facet=[f'[[facet_{FACET_ID}|Формат]]']),
        'facet встраиванием файла': lambda d: d.update(facet=f'![[facet_{FACET_ID}|Формат]]'),
        'facet без alias': lambda d: d.update(facet=f'[[facet_{FACET_ID}]]'),
        'defined_by не UUIDv7': lambda d: d.update(defined_by='facet-value'),
        'id версии 4': lambda d: d.update(
            id='f47ac10b-58cc-4372-a567-0e02b2c3d479'),
        'без title': lambda d: d.pop('title'),
        'aliases пустым списком': lambda d: d.update(aliases=[]),
        'status вне набора': lambda d: d.update(status='published'),
    }
    for label, mutate in neg.items():
        obj = dict(example)
        mutate(obj)
        expect_bad(f'facet-value: {label}', FV_FILE, obj)
    # метатип 9 упомянут в описании схемы, но не зафиксирован const
    if METATYPE9 not in read('schema', FV_FILE):
        fail(f'{FV_FILE}: в описании нет id встроенного метатипа 9')
    if json.dumps(SCHEMAS[FV_FILE]).count(f'"const": "{METATYPE9}"'):
        fail(f'{FV_FILE}: defined_by зафиксирован const (ADR-010, W6)')
    defs = SCHEMAS[FV_FILE]['$defs']['facet-value']
    for key in ('type', 'layer', 'facet'):
        if key not in defs.get('required', []):
            fail(f'{FV_FILE}: `{key}` не в required')
    print(f'[3] facet-value.json: канонический пример 04-properties.md валиден, '
          f'{len(neg)} негативных примеров отвергнуты')


# ----------------------------------- 5. примеры и проверки core-property-values
CPV_FILE = 'core-property-values.json'


def check_core_property_values():
    text = read('docs', 'metamodel', '07-core-properties.md')
    frag = pick_block(text, 'cover:', '07-core-properties.md, раздел 2')
    if frag:
        expect_ok('YAML-фрагмент 07-core-properties.md раздел 2', CPV_FILE, frag)
        for key in ('cover', 'artwork', 'isbn', 'published', 'attachment'):
            if key not in frag:
                fail(f'фрагмент 07-core-properties.md: нет ключа `{key}`')
    link = f'[[image_{IMAGE_ID}|Обложка]]'
    person = f'[[person_{PERSON_ID}|Автор]]'
    pos = {
        'cover': link, 'poster': link, 'photo': link, 'artwork': [link, link],
        'url': 'https://example.org/source', 'isbn': '978-5-00000-000-0',
        'published': '2026-10-27', 'attachment': 'attachments/cover.png',
        'position': 3, 'occupation': ['developer', 'writer'],
        'format': 'ebook', 'creation-method': 'photograph',
        'specialization-note': 'значение незадекларированного ключа',
    }
    expect_ok('фрагмент из 12 ключей + посторонний ключ', CPV_FILE, pos)
    expect_ok('пустой фрагмент', CPV_FILE, {})
    neg = {
        'cover путём к файлу': ('cover', 'attachments/cover.png'),
        'cover списком': ('cover', [link]),
        'cover ссылкой не на image': ('cover', person),
        'artwork одиночной ссылкой': ('artwork', link),
        'artwork пустым списком': ('artwork', []),
        'artwork элементом не ссылкой': ('artwork', ['cover.png']),
        'url пустой строкой': ('url', '   '),
        'isbn числом': ('isbn', 9785000000000),
        'published частичной датой': ('published', '2026-10'),
        'published русской датой': ('published', '27.10.2026'),
        'attachment пустой строкой': ('attachment', '  '),
        'attachment числом': ('attachment', 42),
        'position нулём': ('position', 0),
        'position отрицательным': ('position', -2),
        'position дробным': ('position', 1.5),
        'position строкой': ('position', '3'),
        'occupation строкой': ('occupation', 'developer'),
        'occupation пустым списком': ('occupation', []),
        'occupation элементом-списком': ('occupation', [['developer']]),
        'format списком': ('format', ['ebook']),
        'format пустой строкой': ('format', ''),
        'creation-method числом': ('creation-method', 7),
    }
    for label, (key, value) in neg.items():
        frag = dict(pos)
        frag[key] = value
        expect_bad(f'core-property-values: {label}', CPV_FILE, frag)
    # наборы значений триггеров не перенесены в схему
    forbidden = []
    collect_keyword(SCHEMAS[CPV_FILE], 'enum', forbidden)
    if forbidden:
        fail(f'{CPV_FILE}: найден ключ `enum` — набор значений перенесён в схему (DL-044)')
    raw = read('schema', CPV_FILE)
    for value in ('"ebook"', '"audiobook"', '"ai-generated"', '"illustration"'):
        if value in raw:
            fail(f'{CPV_FILE}: значение {value} встречается в схеме')
    # граница формы: string не различает путь к файлу и каноническую ссылку
    expect_ok('core-property-values: attachment строкой в форме ссылки', CPV_FILE,
              {'attachment': person})
    info('`attachment` (value_type: string) схема не отличает от канонической ссылки: '
         'паттерн не вводился (DL-044), семантика ключа — 07-core-properties.md, '
         'раздел 3, пункт 1')
    print(f'[4] core-property-values.json: фрагменты документов валидны, '
          f'{len(neg)} негативных примеров отвергнуты, `enum` в схеме нет')


def collect_keyword(node, keyword, out):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == keyword:
                out.append(v)
            collect_keyword(v, keyword, out)
    elif isinstance(node, list):
        for v in node:
            collect_keyword(v, keyword, out)


# ------------------------------------------------- 6. пятнадцать форм значений
VT2DEF = {
    'string': 'string-value', 'text': 'text-value', 'number': 'number-value',
    'boolean': 'boolean-value', 'date': 'date-value', 'datetime': 'datetime-value',
    'enum': 'enum-value', 'list<string>': 'list-of-string',
    'list<enum>': 'list-of-enum', 'link': 'link-value',
    'list<link>': 'list-of-link', 'uuid': 'uuid-value',
    'media': 'media-value', 'list<media>': 'list-of-media',
}
FORM_EXAMPLES = {
    'string-value': ('https://example.org', ''),
    'text-value': ('текст запроса\nвторая строка', '   '),
    'number-value': (12.5, '12.5'),
    'integer-value': (3, 1.5),
    'boolean-value': (True, 'true'),
    'date-value': ('2026-10-27', '2026-10'),
    'datetime-value': ('2026-10-27T14:30:00+03:00', '2026-10-27T14:30:00'),
    'enum-value': ('ebook', ['ebook']),
    'list-of-string': (['python', 'sql'], []),
    'list-of-enum': (['developer'], 'developer'),
    'link-value': (f'[[person_{PERSON_ID}|Автор]]', f'person_{PERSON_ID}'),
    'list-of-link': ([f'[[person_{PERSON_ID}|Автор]]'],
                     f'[[person_{PERSON_ID}|Автор]]'),
    'uuid-value': (PERSON_ID, 'F47AC10B-58CC-4372-A567-0E02B2C3D479'),
    'list-of-media': ([f'[[image_{IMAGE_ID}|Обложка]]'], []),
}


def check_value_forms():
    defs = SCHEMAS[CPV_FILE]['$defs']
    expected = set(VT2DEF.values()) | {'integer-value'}
    if set(defs) != expected:
        fail(f'{CPV_FILE}: состав $defs {sorted(set(defs) ^ expected)} расходится с ожидаемым')
    for name in sorted(expected):
        pointer = f'#/$defs/{name}'
        if name == 'media-value':
            # форма-объединение из media.json: одиночная ссылка и список
            expect_ok(f'$defs/media-value: одиночная ссылка', 'media.json',
                      f'[[image_{IMAGE_ID}|Обложка]]', '#/$defs/media-value')
            expect_bad(f'$defs/media-value: путь к файлу', 'media.json',
                       'attachments/cover.png', '#/$defs/media-value')
            continue
        good, bad = FORM_EXAMPLES[name]
        expect_ok(f'$defs/{name}: позитивный пример', CPV_FILE, good, pointer)
        expect_bad(f'$defs/{name}: негативный пример', CPV_FILE, bad, pointer)
    # каждая из 14 value_type имеет форму
    for vt, d in VT2DEF.items():
        if d not in defs:
            fail(f'{CPV_FILE}: для value_type `{vt}` нет $defs/{d}')
    print(f'[5] форм значений: {len(defs)} $defs (14 value_type + integer-value), '
          f'позитивных и негативных примеров — {2 * (len(defs) - 1) + 2}')


# ---------------------------------------------------- 7. регрессия первой волны
def check_first_wave_regression():
    prop = {
        'id': '01a17d3b-4a21-787a-b3db-b9365bb54266', 'type': 'property',
        'defined_by': '01a17d3b-4a01-73dd-8782-259a7e45663f',
        'property_key': 'cover', 'title': 'Обложка',
        'aliases': ['Обложка', 'cover'], 'value_type': 'media',
        'required': 'conditional', 'applies_to': ['source', 'album'],
        'layer': 'system', 'status': 'accepted', 'owner': 'human',
    }
    expect_ok('object.json: определение свойства (регрессия)', 'object.json', prop)
    bad = dict(prop, layer='content')
    expect_bad('object.json: layer content у определения (INV-09)', 'object.json', bad)
    wrapper = {
        'id': IMAGE_ID, 'type': 'image',
        'defined_by': '01a17d3b-4a21-787a-b3db-b9365bb54266',
        'title': 'Обложка книги', 'aliases': ['Обложка книги'],
        'layer': 'content', 'status': 'accepted', 'owner': 'human',
        'attachment': 'attachments/cover.png',
    }
    expect_ok('media.json: обёртка image (регрессия)', 'media.json', wrapper)
    expect_bad('media.json: обёртка без attachment (INV-24)', 'media.json',
               {k: v for k, v in wrapper.items() if k != 'attachment'})
    print('[6] регрессия первой волны: object.json и media.json ведут себя как в iter-010')


# ------------------------------------------------------- 8. сверка с реестрами
CORE12 = ['cover', 'poster', 'photo', 'artwork', 'url', 'isbn', 'published',
          'attachment', 'position', 'occupation', 'format', 'creation-method']


def check_registry_consistency():
    text = read('docs', 'metamodel', '07-core-properties.md')
    rows = re.findall(
        r'^\| (\d+) \| `([a-z0-9-]+)` \| .*? \| `[0-9a-f-]{36}` \| `([a-z<>]+)` \|',
        text, re.M)
    if len(rows) != 23:
        fail(f'07-core-properties.md: разобрано строк реестра {len(rows)}, ожидалось 23')
    registry = {key: vt for _, key, vt in rows}
    props = SCHEMAS[CPV_FILE]['properties']
    if set(props) != set(CORE12):
        fail(f'{CPV_FILE}: состав ключей {sorted(set(props) ^ set(CORE12))} != 12 ожидаемых')
    for key in CORE12:
        if key not in registry:
            fail(f'{CPV_FILE}: ключ `{key}` отсутствует в реестре свойств ядра')
            continue
        vt = registry[key]
        node = props[key]
        ref = node.get('$ref') or (node.get('allOf') or [{}])[0].get('$ref', '')
        actual = ref.rpartition('/')[2]
        allowed = {VT2DEF[vt]}
        if vt == 'number':
            allowed.add('integer-value')
        if actual not in allowed:
            fail(f'{CPV_FILE}: `{key}` (value_type {vt}) ссылается на $defs/{actual}, '
                 f'ожидалось {sorted(allowed)}')
        if vt in ('media', 'list<media>', 'link', 'list<link>') and \
                not node.get('description', '').startswith('Свойство ядра'):
            fail(f'{CPV_FILE}: `{key}` — описание не начинается с номера записи реестра')
    # абзац после таблицы перечисляет все 23 ключа
    paragraph = text.split('\n\n')[3] if len(text.split('\n\n')) > 3 else ''
    for block in text.split('\n\n'):
        if 'Формы значений двенадцати ключей' in block:
            paragraph = block
    for key in registry:
        if f'`{key}`' not in paragraph:
            fail(f'07-core-properties.md: ключ `{key}` не упомянут в абзаце о схеме')
    # ключ facet в реестре свойств
    p4 = read('docs', 'metamodel', '04-properties.md')
    if '| `facet` | Фасет значения | `link` | always | `facet-value` | `1..1` |' not in p4:
        fail('04-properties.md: строка ключа `facet` не найдена или изменена')
    if '01a17d3b-4a08-7875-996d-c4af6179a249' not in p4:
        fail('04-properties.md: нет id встроенного метатипа 9')
    print(f'[7] реестр свойств ядра: 23 записи, 12 ключей схемы соответствуют '
          f'value_type реестра; строка ключа `facet` в 04-properties.md на месте')


# --------------------------------------------------------- 9. Markdown-проверки
def iter_md():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', 'tools')]
        for name in sorted(files):
            if name.endswith('.md'):
                yield os.path.join(base, name)


LINK = re.compile(r'\]\(([^)\s]+)\)')
# Плейсхолдер из таблицы отклонённой альтернативы ADR-003 (с iter-003) и его
# повторения в исторических REPORT.md: не ссылки, а иллюстрации — вне scope.
LINK_ALLOW = {'путь/файл.md'}
CHANGED = ['docs/metamodel/00-overview.md', 'docs/metamodel/01-invariants.md',
           'docs/metamodel/02-layers.md', 'docs/metamodel/03-builtin-types.md',
           'docs/metamodel/04-properties.md', 'docs/metamodel/07-core-properties.md',
           'docs/metamodel/09-structural-invariants.md',
           'docs/validation/00-validation-rules.md', 'docs/decisions/decision-log.md',
           'docs/adr/ADR-010-schema-second-wave.md', 'docs/glossary/glossary.md',
           'docs/project-map/PROJECT_MAP.md', 'docs/CHECKPOINT.md']
DL_RANGE = re.compile(r'DL-(\d{3})\s*[…-]\s*DL-(\d{3})')
DL_SINGLE = re.compile(r'DL-(\d{3})')


def check_markdown():
    dl_text = read('docs', 'decisions', 'decision-log.md')
    ids = re.findall(r'^\|\s*(DL-\d{3})\s*\|', dl_text, re.M)
    if not ids:
        ids = re.findall(r'(DL-\d{3})', dl_text)
    numbers = sorted({int(m.group(1)) for m in DL_SINGLE.finditer(dl_text)})
    if numbers != list(range(1, len(numbers) + 1)):
        gaps = [n for n in range(1, max(numbers) + 1) if n not in numbers]
        fail(f'decision-log.md: пропуски в нумерации DL: {gaps}')
    if max(numbers) != MAX_DL_EXPECTED:
        fail(f'decision-log.md: максимальный DL-{max(numbers):03d}, '
             f'ожидался DL-{MAX_DL_EXPECTED:03d}')
    all_dl = set(numbers)

    total_links = 0
    for path in iter_md():
        rel = os.path.relpath(path, ROOT)
        text = open(path, encoding='utf-8').read()
        for m in LINK.finditer(text):
            target = m.group(1)
            if target.startswith(('http://', 'https://', 'mailto:')):
                continue
            file_part = target.partition('#')[0]
            if not file_part or file_part in LINK_ALLOW:
                continue
            total_links += 1
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), file_part))
            if not os.path.exists(resolved):
                fail(f'{rel}: ссылка `{target}` не разрешается')
        for m in DL_SINGLE.finditer(text):
            if int(m.group(1)) not in all_dl:
                fail(f'{rel}: ссылка на несуществующий DL-{m.group(1)}')
        for m in DL_RANGE.finditer(text):
            lo, hi = int(m.group(1)), int(m.group(2))
            if lo > hi:
                fail(f'{rel}: диапазон DL-{lo:03d}…DL-{hi:03d} — границы перепутаны')
        cjk = re.findall(r'[\u4e00-\u9fff\u3040-\u30ff]+', text)
        if cjk:
            if rel in CHANGED:
                fail(f'{rel}: найдены CJK-символы {cjk}')
            else:
                info(f'{rel}: CJK-символы {cjk} — существует до iter-011, файл вне scope '
                     f'(предложение правки — REPORT.md iter-011)')
        lines = text.count('\n')
        if lines > 300:
            fail(f'{rel}: {lines} строк — превышен ориентир R-004 / R-006 (~300)')

    # R-002 для нового ADR
    adr = read('docs', 'adr', 'ADR-010-schema-second-wave.md')
    lines = [ln for ln in adr.split('\n')]
    if not lines[0].startswith('# '):
        fail('ADR-010: нет H1 в первой строке (R-002)')
    if not lines[1] == '' or not lines[2].strip():
        fail('ADR-010: после H1 нет вводного абзаца (R-002)')
    if 'Accepted' not in adr:
        fail('ADR-010: нет статуса Accepted')
    w = len(re.findall(r'^### W\d', adr, re.M))
    a = len(re.findall(r'^### А\d|^### A\d', adr, re.M))
    if w != 7:
        fail(f'ADR-010: решений W найдено {w}, ожидалось 7')
    if a != 6:
        fail(f'ADR-010: альтернатив А найдено {a}, ожидалось 6')

    # счётчик кандидатов третьей волны
    rules = read('docs', 'validation', '00-validation-rules.md')
    section = rules.split('## 7. Третья волна: кандидаты')[1].split('## 8.')[0]
    rows = [ln for ln in section.split('\n')
            if ln.startswith('|') and not ln.startswith('|---') and 'Кандидат' not in ln]
    if len(rows) != 19:
        fail(f'00-validation-rules.md: кандидатов третьей волны {len(rows)}, ожидалось 19')
    stale = []
    for path in iter_md():
        rel = os.path.relpath(path, ROOT)
        text = open(path, encoding='utf-8').read()
        if 'восемнадцать кандидатов' in text:
            stale.append(rel)
    expected_stale = {'docs/_workflow/iterations/iter-010/REPORT.md'}
    if set(stale) != expected_stale:
        fail(f'«восемнадцать кандидатов» встречается в: {stale} '
             f'(ожидалось {sorted(expected_stale)}: исторический REPORT.md iter-010 '
             f'не переписывается; в docs/PROJECT_BRIEF.md счётчик обновлён в iter-012)')
    else:
        info('«восемнадцать кандидатов третьей волны» осталось только в историческом '
             'REPORT.md iter-010: в docs/PROJECT_BRIEF.md счётчик обновлён в iter-012 '
             '(файл вошёл в список «Изменить» TASK.md iter-012)')
    print(f'[8] Markdown: ссылок проверено {total_links}; DL в журнале {len(numbers)} '
          f'(DL-001…DL-{max(numbers):03d}); кандидатов третьей волны {len(rows)}; '
          f'ADR-010: {w} решений, {a} альтернатив')


def check_tables():
    """Согласованное число колонок в таблицах изменённых файлов и ADR-010."""
    bad = 0
    for rel in CHANGED + ['docs/_workflow/iterations/iter-011/REPORT.md']:
        text = open(os.path.join(ROOT, rel), encoding='utf-8').read()
        block = []
        for i, line in enumerate(text.split('\n'), 1):
            if line.startswith('|'):
                block.append((i, line))
            else:
                if len(block) > 1:
                    counts = {ln.count('|') - ln.count('\\|') for _, ln in block}
                    if len(counts) != 1:
                        fail(f'{rel}: таблица в строках {block[0][0]}…{block[-1][0]} — '
                             f'разное число колонок {sorted(counts)}')
                        bad += 1
                block = []
        if len(block) > 1:
            counts = {ln.count('|') - ln.count('\\|') for _, ln in block}
            if len(counts) != 1:
                fail(f'{rel}: таблица в строках {block[0][0]}…{block[-1][0]} — '
                     f'разное число колонок {sorted(counts)}')
                bad += 1
    # нечётное число ограждённых блоков кода
    for rel in CHANGED + ['docs/_workflow/iterations/iter-011/REPORT.md']:
        text = open(os.path.join(ROOT, rel), encoding='utf-8').read()
        if text.count('```') % 2:
            fail(f'{rel}: нечётное число ограждённых блоков кода')
    print(f'[11] таблицы и блоки кода в изменённых файлах: расхождений — {bad}')


def check_sizes():
    sizes = []
    for path in iter_md():
        sizes.append((open(path, encoding='utf-8').read().count('\n'),
                      os.path.relpath(path, ROOT)))
    sizes.sort(reverse=True)
    print('[9] объём изменённых файлов (строк):')
    for rel in CHANGED:
        n = open(os.path.join(ROOT, rel), encoding='utf-8').read().count('\n')
        flag = ' — у границы R-006' if n > 250 else ''
        print(f'      {n:4d}  {rel}{flag}')
    print(f'    крупнейшие файлы проекта: ' +
          ', '.join(f'{n} {r}' for n, r in sizes[:3]))


def check_tree():
    patches = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d != '.git']
        for name in files:
            if re.fullmatch(r'iter-\d{3}\.patch', name):
                patches.append(os.path.relpath(os.path.join(base, name), ROOT))
    if patches:
        fail(f'в дереве найдены патч-артефакты: {patches}')
    gi = read('.gitignore')
    if 'iter-*.patch' not in gi:
        fail('.gitignore: нет строки iter-*.patch')
    if 'tools/' not in gi:
        info('.gitignore: каталог tools/ не игнорируется')
    print('[10] дерево: iter-*.patch нет; .gitignore содержит iter-*.patch и tools/')


def main():
    load_schemas()
    check_refs()
    check_facet_value()
    check_core_property_values()
    check_value_forms()
    check_first_wave_regression()
    check_registry_consistency()
    check_markdown()
    check_sizes()
    check_tree()
    check_tables()
    if UNSUPPORTED:
        info(f'мини-валидатор не поддерживает ключевые слова (не встретились в '
             f'проверенных ветвях): {sorted(UNSUPPORTED)}')
    print()
    for line in INFO:
        print(f'СПРАВКА: {line}')
    print()
    print(f'Проверок валидности выполнено: {CHECKS}')
    if FAILED:
        print(f'\nПРОВАЛЕНО: {len(FAILED)}')
        for msg in FAILED:
            print(f'  - {msg}')
        return 1
    print('\nВСЕ ПРОВЕРКИ ПРОЙДЕНЫ')
    return 0


if __name__ == '__main__':
    sys.exit(main())
