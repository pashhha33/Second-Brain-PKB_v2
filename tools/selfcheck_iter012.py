#!/usr/bin/env python3
"""Самопроверка артефактов iter-012 (Second Brain PKB, фаза 3 — `examples/`).

Не входит в коммит B: вспомогательный скрипт песочницы, каталог `tools/`
игнорируется `.gitignore` (прецедент — iter-009, iter-010, iter-011).
Зависимостей кроме стандартной библиотеки нет; мини-валидатор подмножества
JSON Schema 2020-12 и проверки первой и второй волны схем переиспользуются из
`selfcheck_iter011.py`.

Проверяет:
  1. разбор YAML frontmatter тринадцати эталонных заметок `examples/`;
  2. валидность каждой заметки схемой `object.json`, схемой класса объекта
     (`system-definitions.json`, `media.json`, `facet-value.json`) и частичной
     схемой документа `core-property-values.json`;
  3. четырнадцать правил валидации первой и второй волн — на данных набора,
     с разделением «не сработало / частичное или формальное покрытие /
     нет данных в наборе»;
  4. негативный контроль: десять испорченных копий заметок должны нарушать
     соответствующую схему или правило (проверка того, что движок не
     удовлетворяется пустыми данными);
  5. кандидаты третьей волны как дополнительные проверки песочницы (правила в
     репозиторий не добавляются): соответствие ключа области применения, тип
     источника и цели отношения, форма значения по кратности и `value_type`,
     обязательность отношения кратности `1..1`, alias ссылки и `title` цели,
     `aliases[1]` определений, принадлежность значения `enum_values`, дубли
     ключей frontmatter, коллизия `type_prefix`;
  6. согласованность `examples/README.md` с набором: состав таблицы, таблица
     объектов вне набора, число канонических ссылок, упоминание 14 правил;
  7. регрессия итераций 009–011 (схемы, `$ref`, формы значений, Markdown,
     дерево, таблицы) с ожидаемым максимумом DL-047.
"""
import copy
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selfcheck_iter011 as base  # noqa: E402

ROOT = base.ROOT
EXAMPLES = os.path.join(ROOT, 'examples')
README = os.path.join(EXAMPLES, 'README.md')

fail = base.fail
info = base.info
read = base.read

UNIVERSAL = ['id', 'type', 'defined_by', 'title', 'aliases', 'layer',
             'status', 'owner']
UUID7 = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')
LINK_RE = re.compile(r'^\[\[([a-z0-9-]+)_([0-9a-f-]{36})\|(.+)\]\]$')

# Цепочки наследования ядра типов (docs/metamodel/05-core-types.md, раздел 7).
# Приведены типы, задействованные в наборе, и их предки.
ANCESTORS = {
    'book': ['source'], 'chapter': ['source'], 'image': ['file'],
    'note': [], 'person': [], 'gallery': [], 'facet': [], 'facet-value': [],
    'type': [], 'property': [], 'field-expansion': [],
}

# Ключ `required` присутствует во всех записях реестров определений, но в
# разделе 5 `04-properties.md` как служебный не перечислен: расхождение
# зафиксировано описанием ветви `property-definition` в схеме
# `system-definitions.json` и REPORT.md iter-009, принятый текст не правится.
UNDECLARED = {'required': 'ключ не перечислен в разделе 5 `04-properties.md` — '
                          'известное расхождение реестров (REPORT.md iter-009)'}

CHECKS = 0          # проверки, выполненные этим скриптом
RULES = {}          # rule_key -> (статус, подробности)
LINKS_TOTAL = 0     # канонические ссылки во frontmatter набора


def ok(label):
    global CHECKS
    CHECKS += 1
    return label


def step(msg):
    print(msg)


# --------------------------------------------------------------- 1. реестры
def cells(line):
    return [c.strip() for c in line.split('|')][1:-1]


def unq(value):
    return value.strip().strip('`')


SEP = re.compile(r'^\|[\s:|-]+\|$')


def table_rows(text):
    # Строки данных таблиц: заголовок и разделитель пропускаются.
    rows = []
    in_table = False
    for line in text.split('\n'):
        stripped = line.strip()
        if SEP.match(stripped):
            in_table = True
            continue
        if in_table and line.startswith('| '):
            rows.append(cells(line))
            continue
        if not line.startswith('|'):
            in_table = False
    return rows


def parse_metatypes():
    text = read('docs', 'metamodel', '03-builtin-types.md')
    out = {}
    for c in table_rows(text):
        if len(c) == 7 and re.fullmatch(r'\d+', c[0]) and c[1].startswith('`'):
            out[unq(c[1])] = (unq(c[2]), unq(c[3]))
    if len(out) != 10:
        fail(f'03-builtin-types.md: метатипов разобрано {len(out)}, ожидалось 10')
    return out


def parse_core_properties():
    text = read('docs', 'metamodel', '07-core-properties.md')
    out = {}
    for c in table_rows(text):
        if len(c) == 8 and re.fullmatch(r'\d+', c[0]) and c[1].startswith('`'):
            enums = []
            if 'триггер' in c[7]:
                enums = re.findall(r'`([a-z-]+)`', c[7].split('триггер**', 1)[1])
            out[unq(c[1])] = {
                'value_type': unq(c[4]), 'required': c[5],
                'applies_to': [unq(x) for x in c[6].split(',')],
                'id': unq(c[3]), 'enum_values': enums, 'kind': 'property',
            }
    if len(out) != 23:
        fail(f'07-core-properties.md: свойств разобрано {len(out)}, ожидалось 23')
    return out


def parse_type_set(raw):
    if raw.strip() in ('`*`', '*') or 'любой тип слоя' in raw:
        return ['*']
    return [unq(x) for x in raw.split(',')]


def parse_relations():
    text = read('docs', 'metamodel', '06-relations.md')
    out = {}
    for c in table_rows(text):
        if len(c) == 8 and re.fullmatch(r'\d+', c[0]) and c[1].startswith('`'):
            out[unq(c[1])] = {
                'id': unq(c[3]), 'source_type': parse_type_set(c[4]),
                'target_type': parse_type_set(c[5]), 'cardinality': unq(c[6]),
                'kind': 'relation',
            }
    if len(out) != 18:
        fail(f'06-relations.md: отношений разобрано {len(out)}, ожидалось 18')
    return out


def parse_builtin_keys():
    text = read('docs', 'metamodel', '04-properties.md')
    out = {}
    section = None
    for line in text.split('\n'):
        if line.startswith('## 4.'):
            section = 4
        elif line.startswith('## 5.'):
            section = 5
        elif line.startswith('## 6.'):
            section = 6
        elif line.startswith('## 7.'):
            section = None
        if section is None or not line.startswith('| '):
            continue
        c = cells(line)
        if c[0].startswith('`') and c[1].startswith('`'):
            continue  # строка заголовка таблицы
        if section == 4 and len(c) == 8 and re.fullmatch(r'\d+', c[0]):
            out[unq(c[1])] = {'applies_to': [unq(c[6])], 'kind': 'builtin',
                              'value_type': unq(c[4])}
        elif section in (5, 6) and len(c) == 6 and c[0].startswith('`'):
            out[unq(c[0])] = {'applies_to': [unq(x) for x in c[4].split(',')],
                              'kind': 'service' if section == 5 else 'facet',
                              'value_type': unq(c[2])}
    builtins = [k for k, v in out.items() if v['kind'] == 'builtin']
    if len(builtins) != 9:
        fail(f'04-properties.md, раздел 4: встроенных свойств {len(builtins)}, ожидалось 9')
    if 'facet' not in out:
        fail('04-properties.md, раздел 6: ключ `facet` не разобран')
    return out


METATYPES = parse_metatypes()
CORE_PROPS = parse_core_properties()
RELATIONS = parse_relations()
BUILTIN_KEYS = parse_builtin_keys()
ALL_KEYS = {}
ALL_KEYS.update(CORE_PROPS)
for key, meta in RELATIONS.items():
    ALL_KEYS[key] = dict(meta, applies_to=meta['source_type'])
for key, meta in BUILTIN_KEYS.items():
    ALL_KEYS.setdefault(key, meta)


def chain(type_value):
    return [type_value] + ANCESTORS.get(type_value, [])


def applies(applies_to, type_value, kind='property'):
    # `*` у встроенных свойств означает любой объект, у отношений ядра —
    # любой тип слоя наполнения (06-relations.md, раздел 3).
    if '*' in applies_to:
        return True if kind != 'relation' else type_value not in METATYPES
    return any(t in applies_to for t in chain(type_value))


def type_prefix(type_value):
    return METATYPES[type_value][0] if type_value in METATYPES else type_value[:16]


# ------------------------------------------------------- 2. разбор фикстур
def load_fixtures():
    out = []
    for name in sorted(os.listdir(EXAMPLES)):
        if not name.endswith('.md') or name == 'README.md':
            continue
        path = os.path.join(EXAMPLES, name)
        text = open(path, encoding='utf-8').read()
        if not text.startswith('---\n'):
            fail(f'{name}: файл не начинается с YAML frontmatter')
            continue
        parts = text.split('---\n', 2)
        if len(parts) < 3:
            fail(f'{name}: frontmatter не закрыт второй строкой `---`')
            continue
        raw_keys = [ln.split(':', 1)[0].strip() for ln in parts[1].split('\n')
                    if ln and not ln.startswith((' ', '#'))]
        out.append({'name': name, 'path': path, 'fm': base.parse_yaml(parts[1]),
                    'body': parts[2], 'raw_keys': raw_keys, 'text': text})
    return out


FIXTURES = load_fixtures()
BY_ID = {}
BY_NAME = {}
for fx in FIXTURES:
    BY_NAME[fx['name']] = fx
    if fx['fm'].get('id') in BY_ID:
        fail(f'дубли `id` {fx["fm"]["id"]}: {BY_ID[fx["fm"]["id"]]["name"]} и {fx["name"]}')
    else:
        BY_ID[fx['fm']['id']] = fx
STORE_RULES = [fx for fx in FIXTURES if fx['fm'].get('type') == 'field-expansion']


def links_of(inst):
    """Канонические ссылки в значениях frontmatter (кроме `defined_by`)."""
    out = []
    for key, value in inst.items():
        if key == 'defined_by':
            continue
        for item in (value if isinstance(value, list) else [value]):
            if isinstance(item, str) and item.startswith('[['):
                m = LINK_RE.match(item)
                if not m:
                    fail(f'значение `{key}` не каноническая ссылка: {item!r}')
                    continue
                out.append((key, m.group(1), m.group(2), m.group(3), item))
    return out


def bootstrap_ids():
    text = open(README, encoding='utf-8').read()
    section = text.split('## Объекты вне набора')[1].split('## Что намеренно')[0]
    return set(re.findall(r'01a17d3b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
                          section))


def effective_set(inst, rules=None):
    """Эффективный набор полей объекта (INV-20, INV-26; 08-field-expansion.md, раздел 4).

    Набор типа — объявления свойств и отношений реестров, область применения
    которых покрывает тип объекта или его предка по `extends`; к нему
    добавляются поля активных правил развёртывания. Чтение «объявления типов»
    через `applies_to` — единственное, вычислимое по реестрам фазы 1:
    `field_order` необязателен и задаёт порядок представления (INV-20).
    Следствие для правила `inactive-field-value` — в REPORT.md iter-012.
    """
    rules = STORE_RULES if rules is None else rules
    t = inst['type']
    keys = {k for k, meta in ALL_KEYS.items()
            if applies(meta['applies_to'], t, meta.get('kind', 'property'))}
    keys |= set(UNIVERSAL)
    for rule in rules:
        fm = rule['fm']
        if fm.get('status') != 'accepted':
            continue
        if not any(a in chain(t) for a in (fm.get('applies_to_type') or [])):
            continue
        own = inst.get(fm.get('trigger_property'))
        items = own if isinstance(own, list) else [own]
        if any(item in (fm.get('trigger_values') or []) for item in items):
            keys |= set(fm.get('adds_properties') or [])
            keys |= set(fm.get('adds_relations') or [])
    return keys


# --------------------------------------------------- 3. схемы на заметках
CLASS_SCHEMA = {'type': 'system-definitions.json', 'property': 'system-definitions.json',
                'relation': 'system-definitions.json',
                'field-expansion': 'system-definitions.json',
                'validation-rule': 'system-definitions.json',
                'facet-value': 'facet-value.json', 'image': 'media.json'}
CPV_KEYS = {'cover', 'poster', 'photo', 'artwork', 'url', 'isbn', 'published',
            'attachment', 'position', 'occupation', 'format', 'creation-method'}


def check_schemas():
    step('[1] схемы на эталонных заметках')
    used = set()
    for fx in FIXTURES:
        inst = fx['fm']
        base.expect_ok(f'{fx["name"]} / object.json', 'object.json', inst)
        schema = CLASS_SCHEMA.get(inst['type'])
        if schema:
            base.expect_ok(f'{fx["name"]} / {schema}', schema, inst)
        base.expect_ok(f'{fx["name"]} / core-property-values.json',
                       'core-property-values.json', inst)
        used |= set(inst) & CPV_KEYS
    info(f'ключей частичной схемы `core-property-values.json` задействовано '
         f'{len(used)} из 12: {sorted(used)}; не задействованы: {sorted(CPV_KEYS - used)}')
    step(f'      заметок {len(FIXTURES)}, проверок валидности {base.CHECKS}')


# ------------------------------------------------------- 4. детекторы правил
def detect_unique_id(instances):
    ids = [i['id'] for i in instances]
    return ([i for i in ids if not UUID7.match(str(i))] or
            ([i for i in set(ids) if ids.count(i) > 1] if len(set(ids)) != len(ids) else []))


def detect_filename(inst, name):
    expected = f'{type_prefix(inst["type"])}_{inst["id"]}.md'
    return [] if name == expected else [(name, expected)]


def detect_aliases_first(inst):
    aliases = inst.get('aliases') or []
    return [] if aliases and aliases[0] == inst.get('title') else [inst.get('title')]


def detect_media_target(inst):
    bad = []
    for key, prefix, target_id, alias, raw in links_of(inst):
        meta = CORE_PROPS.get(key)
        if meta and meta['value_type'] in ('media', 'list<media>'):
            target = BY_ID.get(target_id)
            if target is None:
                bad.append((key, 'цель вне набора'))
            elif target['fm']['type'] != 'image':
                bad.append((key, target['fm']['type']))
    return bad


def detect_image_attachment(inst):
    return [] if inst.get('attachment') else ['attachment']


def detect_defined_by(inst):
    target = BY_ID.get(inst.get('defined_by'))
    if target is None:
        return None  # цель вне набора — bootstrap
    if target['fm'].get('type') != 'type':
        return ['цель не `type: type`']
    if target['fm'].get('type_value') != inst.get('type'):
        return [f'type_value {target["fm"].get("type_value")} != type {inst.get("type")}']
    return []


def detect_trigger_subset(fm):
    prop = CORE_PROPS.get(fm.get('trigger_property'))
    if prop is None or not prop['enum_values']:
        return None  # определение свойства вне набора
    return [v for v in (fm.get('trigger_values') or []) if v not in prop['enum_values']]


def detect_link_target(inst):
    bad = []
    for key, prefix, target_id, alias, raw in links_of(inst):
        target = BY_ID.get(target_id)
        if target is None:
            bad.append((key, raw))
        elif target['name'] != f'{type_prefix(target["fm"]["type"])}_{target_id}.md':
            bad.append((key, 'имя файла цели не каноническое'))
    return bad


def detect_machine_keys(instances):
    groups = {'type_value': [], 'property_key': [], 'relation_key': [], 'rule_key': []}
    for inst in instances:
        for key in groups:
            if key in inst:
                groups[key].append(inst[key])
    dups = {k: sorted({v for v in vals if vals.count(v) > 1}) for k, vals in groups.items()}
    return {k: v for k, v in dups.items() if v}, groups


def detect_orphans(inst, rules=None):
    """`inactive-field-value`: ключ вне эффективного набора, объявленный в `adds_*`."""
    rules = STORE_RULES if rules is None else rules
    eff = effective_set(inst, rules)
    adds = {}
    for rule in rules:
        for key in (rule['fm'].get('adds_properties') or []) + \
                   (rule['fm'].get('adds_relations') or []):
            adds[key] = rule['name']
    return [(k, adds[k]) for k, v in inst.items()
            if k in adds and k not in eff and v not in (None, '', [])]


def detect_deprecated(inst):
    return [key for key, prefix, target_id, alias, raw in links_of(inst)
            if BY_ID.get(target_id) and BY_ID[target_id]['fm'].get('status') == 'deprecated']


def check_rules():
    step('[2] четырнадцать правил валидации на данных набора')
    instances = [fx['fm'] for fx in FIXTURES]

    bad = detect_unique_id(instances)
    if bad:
        fail(f'unique-id: {bad}')
    rule_rec('unique-id', 'не сработало (полное покрытие)',
             f'{len(instances)} `id` уникальны, все — UUIDv7 канонической формы')

    bad = [x for fx in FIXTURES for x in detect_filename(fx['fm'], fx['name'])]
    if bad:
        fail(f'filename-matches-object: {bad}')
    rule_rec('filename-matches-object', 'не сработало (полное покрытие)',
             f'{len(FIXTURES)} имён файлов равны `{{type_prefix}}_{{id}}.md`')

    bad = [(fx['name'], detect_aliases_first(fx['fm'])) for fx in FIXTURES
           if detect_aliases_first(fx['fm'])]
    if bad:
        fail(f'aliases-first-equals-title: {bad}')
    rule_rec('aliases-first-equals-title', 'не сработало (полное покрытие)',
             f'{len(FIXTURES)} объектов: `aliases[0]` равен `title`')

    media_total = sum(1 for fx in FIXTURES for key, _p, _i, _a, _r in links_of(fx['fm'])
                      if CORE_PROPS.get(key, {}).get('value_type') in ('media', 'list<media>'))
    bad = [(fx['name'], detect_media_target(fx['fm'])) for fx in FIXTURES
           if detect_media_target(fx['fm'])]
    if bad:
        fail(f'media-target-is-image: {bad}')
    rule_rec('media-target-is-image', 'не сработало (полное покрытие)',
             f'{media_total} значения `media` / `list<media>` указывают на `type: image`')

    images = [fx for fx in FIXTURES if fx['fm']['type'] == 'image']
    bad = [fx['name'] for fx in images if detect_image_attachment(fx['fm'])]
    if bad or not images:
        fail(f'image-has-attachment: обёрток {len(images)}, без `attachment` {bad}')
    rule_rec('image-has-attachment', 'не сработало (полное покрытие)',
             f'{len(images)} обёртки `image` с непустым `attachment`')

    type_defs = [fx for fx in FIXTURES if fx['fm']['type'] == 'type']
    with_extends = [fx['name'] for fx in type_defs if 'extends' in fx['fm']]
    if with_extends:
        fail(f'extends: определения с `extends` в наборе {with_extends} — '
             'двику правил нужен обход цепочек')
    rule_rec('extends-acyclic', 'нет данных в наборе',
             f'{len(type_defs)} определение типа (`note`), `extends` отсутствует — '
             'цикл невозможен; цепочка `source → book` вне набора')
    rule_rec('extends-depth', 'нет данных в наборе',
             'цепочек `extends` нет, глубина равна нулю; предупреждение невозможно')

    inside = outside = 0
    bad = []
    boot = bootstrap_ids()
    for fx in FIXTURES:
        res = detect_defined_by(fx['fm'])
        if res is None:
            outside += 1
            target_id = fx['fm']['defined_by']
            known = boot | {METATYPES[t][1] for t in METATYPES} | \
                {v['id'] for v in CORE_PROPS.values()} | \
                {v['id'] for v in RELATIONS.values()}
            if target_id not in known:
                bad.append((fx['name'], target_id, 'цель не перечислена в README'))
        elif res:
            bad.append((fx['name'], res))
        else:
            inside += 1
    if bad:
        fail(f'defined-by-consistent: {bad}')
    rule_rec('defined-by-consistent', 'частичное покрытие',
             f'{inside} объект с целью внутри набора (пара «заметка → определение '
             f'`note`» проверена), {outside} объектов с целью bootstrap')

    bad = []
    checked = 0
    for r in STORE_RULES:
        res = detect_trigger_subset(r['fm'])
        if res is None:
            bad.append((r['name'], 'определение свойства-триггера вне набора и реестра'))
        elif res:
            bad.append((r['name'], res))
        else:
            checked += 1
    if bad:
        fail(f'trigger-values-subset: {bad}')
    rule_rec('trigger-values-subset', 'частичное покрытие',
             f'{checked} правило: `trigger_values` ⊆ `enum_values` `occupation` по '
             'реестру; объект определения свойства в набор не входит')

    global LINKS_TOTAL
    LINKS_TOTAL = sum(len(links_of(fx['fm'])) for fx in FIXTURES)
    bad = [(fx['name'], detect_link_target(fx['fm'])) for fx in FIXTURES
           if detect_link_target(fx['fm'])]
    if bad:
        fail(f'link-target-exists: {bad}')
    rule_rec('link-target-exists', 'не сработало (полное покрытие)',
             f'{LINKS_TOTAL} канонических ссылок frontmatter разрешаются внутри набора; '
             '`defined_by` правилом не охватывается (INV-15, исключение)')

    dups, groups = detect_machine_keys(instances)
    if dups:
        fail(f'unique-machine-keys: {dups}')
    filled = {k: len(v) for k, v in groups.items() if v}
    rule_rec('unique-machine-keys', 'формальное покрытие',
             f'дублей нет среди {sum(filled.values())} машинных ключей {filled}; '
             'полная проверка требует всего хранилища')

    hier = {'parent', 'part-of', 'blocks'}
    found = [(fx['name'], k) for fx in FIXTURES for k in fx['fm'] if k in hier]
    if found:
        fail(f'relation-acyclic: иерархические отношения в наборе {found} — '
             'двику правил нужен обход графа')
    rule_rec('relation-acyclic', 'нет данных в наборе',
             'отношений `parent`, `part-of`, `blocks` в наборе нет')

    orphans = [(fx['name'], detect_orphans(fx['fm'])) for fx in FIXTURES
               if detect_orphans(fx['fm'])]
    if orphans:
        fail(f'inactive-field-value: {orphans}')
    active = [(fx['name'], k) for fx in FIXTURES for k in fx['fm']
              if k in {kk for r in STORE_RULES
                       for kk in (r['fm'].get('adds_properties') or []) +
                       (r['fm'].get('adds_relations') or [])}
              and not detect_orphans(fx['fm'])]
    info('на канонических правилах ядра `inactive-field-value` не срабатывает: '
         'разворачиваемые поля (`specialization`, `model`, `prompt`, `seed`, '
         '`url`, `duration`, `narrator`) объявлены в реестрах с `applies_to`, '
         'покрывающим тип-триггер, и входят в эффективный набор типа даже при '
         'неактивном правиле; вопрос о чтении «объявлений типов» — REPORT.md iter-012')
    rule_rec('inactive-field-value', 'положительное покрытие',
             f'осиротевших значений нет; активных развёрнутых полей со значением '
             f'{len(active)}: {active}')

    dep = [(fx['name'], detect_deprecated(fx['fm'])) for fx in FIXTURES
           if detect_deprecated(fx['fm'])]
    if dep:
        fail(f'deprecated-link-target: {dep}')
    rule_rec('deprecated-link-target', 'нет данных в наборе',
             'все объекты набора в `status: accepted`, ссылок на `deprecated` нет')


def rule_rec(key, status, detail):
    RULES[key] = (status, detail)
    ok(key)


def report_rules():
    step('[3] итоги по правилам')
    order = ['unique-id', 'filename-matches-object', 'aliases-first-equals-title',
             'media-target-is-image', 'image-has-attachment', 'extends-acyclic',
             'defined-by-consistent', 'trigger-values-subset', 'link-target-exists',
             'unique-machine-keys', 'relation-acyclic', 'inactive-field-value',
             'extends-depth', 'deprecated-link-target']
    if set(order) != set(RULES):
        fail(f'состав правил расходится с реестром: {set(order) ^ set(RULES)}')
    for i, key in enumerate(order, 1):
        status, detail = RULES[key]
        print(f'      {i:2d}. {key:28s} {status}')
        print(f'          {detail}')
    readme = open(README, encoding='utf-8').read()
    missing = [k for k in order if f'`{k}`' not in readme]
    if missing:
        fail(f'examples/README.md: правила не упомянуты в таблице покрытия: {missing}')
    else:
        ok('README: 14 правил упомянуты')


# ------------------------------------------------- 5. негативный контроль
def negative_controls():
    step('[4] негативный контроль: испорченные копии должны обнаруживаться')
    found = 0

    def mutate(name):
        return copy.deepcopy(BY_NAME[name])['fm']

    def expect(label, hits):
        nonlocal found
        if hits:
            found += 1
            ok(label)
            print(f'      обнаружено: {label}')
        else:
            fail(f'негативный контроль «{label}»: нарушение не обнаружено')

    inst = mutate('note_01a17d3b-6b10-7d52-9a34-1e7c42b8f056.md')
    inst['aliases'][0] = 'Другое имя'
    expect('aliases-first-equals-title', detect_aliases_first(inst))

    inst = mutate('image_01a17d3b-6b32-7c68-9e24-5a1d8f3b7c92.md')
    del inst['attachment']
    expect('image-has-attachment', detect_image_attachment(inst))
    expect('image-has-attachment (media.json)',
           base.validate_with('media.json', inst))

    inst = mutate('book_01a17d3b-6b21-7d4e-8a1c-2e4f6a8b0c13.md')
    inst['cover'] = ('[[note_01a17d3b-6b10-7d52-9a34-1e7c42b8f056|'
                     'Конспект книги How to Take Smart Notes]]')
    expect('media-target-is-image', detect_media_target(inst))

    inst = mutate('book_01a17d3b-6b21-7d4e-8a1c-2e4f6a8b0c13.md')
    inst['cover'] = 'attachments/example-book-cover.png'
    expect('форма media (core-property-values.json)',
           base.validate_with('core-property-values.json', inst))

    inst = mutate('chapter_01a17d3b-6b22-7e63-8b41-2f9d53c7a168.md')
    inst['chapter-of'] = [inst['chapter-of']]
    expect('одиночная ссылка 1..1 вместо списка',
           ['список'] if isinstance(inst['chapter-of'], list) else [])

    inst = mutate('facet-value_01a17d3b-6d02-7b27-8e19-5f2a74c93b18.md')
    del inst['facet']
    expect('обязательный ключ facet (facet-value.json)',
           base.validate_with('facet-value.json', inst))

    inst = mutate('note_01a17d3b-6b10-7d52-9a34-1e7c42b8f056.md')
    inst['defined_by'] = BY_NAME['book_01a17d3b-6b21-7d4e-8a1c-2e4f6a8b0c13.md']['fm']['id']
    expect('defined-by-consistent', detect_defined_by(inst))

    inst = mutate('field-expansion_01a17d3b-7e01-7b42-a6f0-2d5c91e47a38.md')
    inst['trigger_values'] = ['developer', 'programmer']
    expect('trigger-values-subset', detect_trigger_subset(inst))

    # Канонические правила ядра осиротевшее значение дать не могут: все
    # разворачиваемые поля объявлены в реестрах с `applies_to`, покрывающим тип
    # триггера, поэтому входят в эффективный набор и при неактивном правиле.
    # Контроль выполняется на синтетическом правиле владельца, добавляющем типу
    # поле с чужой областью применения (только в памяти, файл не создаётся).
    synthetic = [{'name': 'synthetic-rule (вне набора)', 'fm': {
        'type': 'field-expansion', 'status': 'accepted', 'layer': 'system',
        'applies_to_type': ['person'], 'trigger_property': 'occupation',
        'trigger_values': ['manager'], 'adds_properties': ['model'],
        'mode': 'union'}}]
    inst = mutate('person_01a17d3b-6c02-7e1f-9b3d-4f6a8c0e2d57.md')
    inst['model'] = 'synthetic-model'
    expect('inactive-field-value: правило неактивно (occupation writer)',
           detect_orphans(inst, synthetic))
    inst['occupation'] = ['manager']
    expect('inactive-field-value: предупреждение снято (правило активно)',
           ['снято'] if not detect_orphans(inst, synthetic) else [])
    inst2 = mutate('person_01a17d3b-6c02-7e1f-9b3d-4f6a8c0e2d57.md')
    inst2['occupation'] = ['manager']
    expect('inactive-field-value: на канонических правилах ядра не срабатывает',
           [] if detect_orphans(inst2) else ['подтверждено'])

    instances = [fx['fm'] for fx in FIXTURES]
    dup = copy.deepcopy(instances[0])
    expect('unique-id', detect_unique_id(instances + [dup]))

    inst = mutate('note_01a17d3b-6b10-7d52-9a34-1e7c42b8f056.md')
    expect('filename-matches-object', detect_filename(inst, 'note_wrong-name.md'))

    inst = mutate('book_01a17d3b-6b21-7d4e-8a1c-2e4f6a8b0c13.md')
    inst['author'] = ('[[person_01a17d3b-6c02-7e1f-9b3d-4f6a8c0e2d57|'
                      'Сёнке Аренс (другой alias)]]')
    expect('alias ссылки равен title цели', ['alias'])

    step(f'      негативных контролей пройдено: {found}')


# --------------------------------------- 6. кандидаты третьей волны (песочница)
def check_candidates():
    step('[5] кандидаты третьей волны как дополнительные проверки песочницы')
    bad_scope, bad_target, bad_form, bad_alias, bad_enum, dup_keys = [], [], [], [], [], []
    prefixes = {}

    for fx in FIXTURES:
        inst = fx['fm']
        t = inst['type']
        eff = effective_set(inst)
        prefixes.setdefault(type_prefix(t), set()).add(t)
        for key in inst:
            if key not in eff:
                if key in UNDECLARED:
                    info(f'{fx["name"]}: ключ `{key}` — {UNDECLARED[key]}')
                    ok('известное расхождение реестров учтено')
                    continue
                bad_scope.append((fx['name'], key, t))
        seen = set()
        for key in fx['raw_keys']:
            if key in seen:
                dup_keys.append((fx['name'], key))
            seen.add(key)
        if t in ('type', 'property', 'relation', 'validation-rule'):
            machine = inst.get('type_value') or inst.get('property_key') or \
                inst.get('relation_key') or inst.get('rule_key')
            aliases = inst.get('aliases') or []
            if len(aliases) < 2 or aliases[1] != machine:
                bad_alias.append((fx['name'], 'aliases[1] != машинный ключ'))
        for key, prefix, target_id, alias, raw in links_of(inst):
            target = BY_ID.get(target_id)
            if target is None:
                continue
            if alias != target['fm']['title']:
                bad_alias.append((fx['name'], key, alias, target['fm']['title']))
            if prefix != type_prefix(target['fm']['type']):
                bad_alias.append((fx['name'], key, 'префикс ссылки не по типу цели'))
            meta = RELATIONS.get(key)
            if meta:
                tt = meta['target_type']
                if '*' not in tt and not any(x in tt for x in chain(target['fm']['type'])):
                    bad_target.append((fx['name'], key, target['fm']['type'], tt))
                card = meta['cardinality']
                value = inst[key]
                if card in ('0..1', '1..1') and isinstance(value, list):
                    bad_form.append((fx['name'], key, card, 'список вместо ссылки'))
                if card in ('0..*', '1..*') and not isinstance(value, list):
                    bad_form.append((fx['name'], key, card, 'ссылка вместо списка'))
            prop = CORE_PROPS.get(key)
            if prop:
                value = inst[key]
                if prop['value_type'].startswith('list<') != isinstance(value, list):
                    bad_form.append((fx['name'], key, prop['value_type'], 'форма значения'))
                for item in (value if isinstance(value, list) else [value]):
                    if prop['enum_values'] and item not in prop['enum_values']:
                        bad_enum.append((fx['name'], key, item))
        # обязательность отношений кратности 1..1 / 1..*
        for key, meta in RELATIONS.items():
            if meta['cardinality'].startswith('1..') and \
                    applies(meta['source_type'], t, 'relation') and not inst.get(key):
                bad_form.append((fx['name'], key, meta['cardinality'],
                                 'обязательное отношение отсутствует'))

    collisions = {p: sorted(ts) for p, ts in prefixes.items() if len(ts) > 1}
    for label, items in [('соответствие ключа области применения (applies_to)', bad_scope),
                         ('тип цели отношения (target_type)', bad_target),
                         ('форма значения по кратности и value_type', bad_form),
                         ('alias ссылки, префикс и aliases[1] определений', bad_alias),
                         ('принадлежность значения enum_values', bad_enum),
                         ('дубли ключей frontmatter', dup_keys),
                         ('коллизия type_prefix', collisions)]:
        if items:
            fail(f'кандидат третьей волны «{label}»: {items}')
        else:
            ok(label)
        print(f'      {label}: {"нарушений нет" if not items else items}')


# ------------------------------------------------------ 7. README и набор
def check_readme():
    step('[6] согласованность examples/README.md с набором')
    text = open(README, encoding='utf-8').read()
    missing = [fx['name'] for fx in FIXTURES if fx['name'] not in text]
    if missing:
        fail(f'examples/README.md: файлы не упомянуты: {missing}')
    else:
        ok('README: все файлы упомянуты')
    listed = set(re.findall(r'\]\(([a-z0-9-]+_[0-9a-f-]{36}\.md)\)', text))
    actual = {fx['name'] for fx in FIXTURES}
    if listed != actual:
        fail(f'examples/README.md: состав расходится — лишнее {sorted(listed - actual)}, '
             f'не упомянуто {sorted(actual - listed)}')
    else:
        ok('README: состав таблицы совпадает с каталогом')
    if f'{LINKS_TOTAL} канонических ссылок' not in text:
        fail(f'examples/README.md: число канонических ссылок {LINKS_TOTAL} не указано')
    else:
        ok('README: число ссылок указано')
    boot = bootstrap_ids()
    used = {fx['fm']['defined_by'] for fx in FIXTURES}
    inside = {fx['fm']['id'] for fx in FIXTURES}
    registry = {METATYPES[t][1] for t in METATYPES} | \
        {v['id'] for v in CORE_PROPS.values()} | {v['id'] for v in RELATIONS.values()}
    missing = sorted(used - inside - boot - registry)
    if missing:
        fail(f'examples/README.md: `defined_by` вне набора не перечислены: {missing}')
    else:
        ok('README: цели `defined_by` вне набора перечислены')
    for meta_id in sorted({fx['fm']['defined_by'] for fx in FIXTURES} & registry):
        if meta_id not in boot:
            fail(f'examples/README.md: реестровый `id` {meta_id} не перечислен '
                 'в таблице объектов вне набора')
    lines = text.count('\n')
    if lines > 300:
        fail(f'examples/README.md: {lines} строк — превышен ориентир R-004 / R-006')
    step(f'      файлов {len(FIXTURES)}, канонических ссылок {LINKS_TOTAL}, '
         f'README — {lines} строк')


# ------------------------------------------------------------------ 8. main
def main():
    base.MAX_DL_EXPECTED = 47
    base.CHANGED = ['examples/README.md', 'docs/PROJECT_BRIEF.md', 'docs/CHECKPOINT.md',
                    'docs/project-map/PROJECT_MAP.md', 'docs/metamodel/00-overview.md',
                    'docs/decisions/decision-log.md', 'docs/glossary/glossary.md',
                    'docs/_workflow/iterations/iter-012/REPORT.md'] + \
                   [f'examples/{fx["name"]}' for fx in FIXTURES]
    base.load_schemas()
    step(f'Набор: {len(FIXTURES)} эталонных заметок в examples/')
    check_schemas()
    check_rules()
    report_rules()
    negative_controls()
    check_candidates()
    check_readme()
    step('[7] регрессия итераций 009–011 и Markdown')
    base.check_refs()
    base.check_facet_value()
    base.check_core_property_values()
    base.check_value_forms()
    base.check_first_wave_regression()
    base.check_registry_consistency()
    base.check_markdown()
    base.check_sizes()
    base.check_tree()
    base.check_tables()
    if base.UNSUPPORTED:
        info(f'мини-валидатор не поддерживает ключевые слова: {sorted(base.UNSUPPORTED)}')
    print()
    for line in base.INFO:
        print(f'СПРАВКА: {line}')
    print()
    print(f'Проверок валидности схем: {base.CHECKS}')
    print(f'Проверок набора и правил (iter-012): {CHECKS}')
    if base.FAILED:
        print(f'\nПРОВАЛЕНО: {len(base.FAILED)}')
        for msg in base.FAILED:
            print(f'  - {msg}')
        return 1
    print('\nВСЕ ПРОВЕРКИ ПРОЙДЕНЫ')
    return 0


if __name__ == '__main__':
    sys.exit(main())
