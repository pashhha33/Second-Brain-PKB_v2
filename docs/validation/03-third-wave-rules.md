# Правила валидации: третья волна

Описания пяти правил третьей волны (iter-013): четыре межобъектные проверки с `severity: error` и одно предупреждение. Формат объекта и состав ключей — [`00-validation-rules.md`](00-validation-rules.md), раздел 3; граница «схема — правило» — [`../adr/ADR-009-phase2-schemas.md`](../adr/ADR-009-phase2-schemas.md) (S1); состав волны, выбор `severity` и отклонённые альтернативы — DL-048. Правила первой волны — [`01-first-wave-rules.md`](01-first-wave-rules.md), второй — [`02-second-wave-rules.md`](02-second-wave-rules.md).

`id` правил иллюстративные: у правил валидации фиксированных `id` нет, они выдаются при создании объекта (DL-038). Все правила волны — `status: accepted`, `layer: system`, `owner: human`, `defined_by` — встроенный метатип `validation-rule` (запись 5 [`../metamodel/03-builtin-types.md`](../metamodel/03-builtin-types.md)).

Общее свойство пяти правил: каждое требует другого объекта (определения отношения, свойства, типа или цели ссылки), поэтому ни одно не выражается схемой (ADR-009, S1.2). Нумерация в реестре сквозная — 15…19 ([`00-validation-rules.md`](00-validation-rules.md), раздел 6.3).

## 1. `facet-target-is-facet` — цель ключа `facet` является фасетом

```yaml
id: 01a17d3b-9c01-7a11-8e01-1f2e3d4c5b6a
type: validation-rule
defined_by: 01a17d3b-4a04-7c70-99cd-5c01dddac8b4
rule_key: facet-target-is-facet
title: Цель ключа facet является фасетом
aliases: [Цель ключа facet является фасетом, facet-target-is-facet]
checks: [INV-15, "04-properties.md#6"]
severity: error
applies_to: [facet-value]
condition: "Значение ключа facet объекта type: facet-value — каноническая ссылка на объект, у которого type равен facet, а layer равен classification; id и type_prefix цели совпадают с id и именем файла найденного объекта."
message: "Ключ facet указывает не на фасет: значение фасета принадлежит одному объекту type: facet, ссылка на объект другого типа делает принадлежность значения неоднозначной."
layer: system
status: accepted
owner: human
```

- **Алгоритм:** для объекта `type: facet-value` извлечь из канонической ссылки в ключе `facet` имя файла цели и `id`, найти объект, проверить его `type` и `layer`; ключ обязателен и одиночен (кратность `1..1`), отсутствие ключа или форма значения отклоняются схемой [`../../schema/facet-value.json`](../../schema/facet-value.json), а не правилом.
- **Границы:** правило построено по образцу `media-target-is-image` (INV-23) — схема фиксирует форму ссылки, правило фиксирует тип цели. Форма значения (префикс `facet_`, наличие alias, одиночная форма) контролируется схемой (`$defs/facet-link`), существование цели — правилом `link-target-exists`, поэтому `facet-target-is-facet` срабатывает только тогда, когда объект с префиксом `facet_` существует, но не является фасетом (ручная правка `type`, перенос заметки). Отдельного инварианта о типе цели ключа `facet` нет — норма в [`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 6 (`value_type: link`, `required: always`, кратность `1..1`, область `facet-value`), поэтому `checks` содержит INV-15 и указатель пункта реестра (DL-040). Привязка объекта слоя наполнения к значению фасета выполняется отношением `object-facet-value` — его область проверяет `relation-endpoints-match`, а не это правило. Значение фасета в `status: deprecated` остаётся фасетом: правило не срабатывает, предупреждение выдаёт `deprecated-link-target`.

## 2. `collection-element-consistent` — элемент и коллекция одного рода

```yaml
id: 01a17d3b-9c02-7a22-9f12-2a3b4c5d6e7f
type: validation-rule
defined_by: 01a17d3b-4a04-7c70-99cd-5c01dddac8b4
rule_key: collection-element-consistent
title: Элемент и коллекция одного рода
aliases: [Элемент и коллекция одного рода, collection-element-consistent]
checks: [DL-025, "05-core-types.md#5"]
severity: warning
applies_to: [film, track, image]
condition: "Значение отношения part-of-collection указывает на коллекцию того рода, который соответствует типу элемента по реестру ядра: film — на film-series, track — на album, image — на gallery."
message: "Элемент и коллекция разного рода: по реестру ядра фильм входит в серию, трек — в альбом, изображение — в галерею. Для смешанной подборки создайте собственное отношение type: relation."
layer: system
status: accepted
owner: human
```

- **Алгоритм:** для каждого значения `part-of-collection` (список или одиночная ссылка) загрузить объект-цель и сверить пару «`type` источника → `type` цели» с тремя парами реестра ([`../metamodel/05-core-types.md`](../metamodel/05-core-types.md), раздел 5, колонка «Элементы»); пара вне перечня — предупреждение на объекте-элементе с указанием ключа, цели и ожидаемого типа коллекции.
- **Границы:** `severity: warning`, а не `error`: соответствие типа элемента и коллекции **не является инвариантом модели** — «состав `source_type` / `target_type` отношения `part-of-collection` фиксирует допустимые пары, а смешанная подборка (например, фильмы вместе с трейлерами) требует отношения, созданного владельцем» ([`../metamodel/05-core-types.md`](../metamodel/05-core-types.md), раздел 5, правило 3). Жёсткая часть ограничения — область отношения: её проверяет `relation-endpoints-match` (`error`), поэтому трек в галерее проходит проверку области (`track` ∈ `source_type`, `gallery` ∈ `target_type`), но получает предупреждение о роде коллекции. Пары перечислены для ядра типов; коллекции и элементы, созданные владельцем, а также его отношения правилом не ограничены (DL-025, [`../metamodel/06-relations.md`](../metamodel/06-relations.md), раздел 2, правило 5). Книга-агрегатор глав коллекцией не является: связь «глава → книга» задаётся отношением `chapter-of` ([`../metamodel/05-core-types.md`](../metamodel/05-core-types.md), раздел 5, правило 5), её область проверяет `relation-endpoints-match`. Коллекция может быть элементом другой коллекции только через общее отношение `part-of` (раздел 5, правило 4) — на `part-of` правило не распространяется. Порядок элемента задаётся свойством `position` и этим правилом не проверяется.

## 3. `relation-endpoints-match` — область отношения соблюдена

```yaml
id: 01a17d3b-9c03-7a33-8e23-3b4c5d6e7f80
type: validation-rule
defined_by: 01a17d3b-4a04-7c70-99cd-5c01dddac8b4
rule_key: relation-endpoints-match
title: Область отношения соблюдена
aliases: [Область отношения соблюдена, relation-endpoints-match]
checks: [INV-17, "06-relations.md#3", "06-relations.md#2"]
severity: error
applies_to: "*"
condition: "Для каждого ключа frontmatter, который является relation_key определения отношения, тип источника входит в source_type определения, а тип каждой цели значения — в target_type; значение * в области означает любой тип слоя content. Область наследуется: тип удовлетворяет области, если в ней назван он сам или любой его предок по цепочке extends."
message: "Отношение использовано вне области определения: тип источника или тип цели не входит в source_type либо target_type определения отношения."
layer: system
status: accepted
owner: human
```

- **Алгоритм:** построить индекс «`relation_key` → определение отношения» по объектам `type: relation` (ключи уникальны — `unique-machine-keys`); для каждого объекта разобрать ключи frontmatter, совпадающие с `relation_key`; определить тип источника по свойству `type` и развернуть цепочку `extends` его определения в множество предков; для каждого значения-ссылки загрузить цель и таким же способом получить множество её типов; область соблюдена, если пересечение непусто для источника и для каждой цели, либо область равна `*` и объект относится к слою `content`.
- **Границы:** основание — [`../metamodel/06-relations.md`](../metamodel/06-relations.md), разделы 2 и 3 (`source_type` и `target_type` — списки `type_value`, `*` означает «любой тип слоя `content`») и INV-17 (определение отношения обязано иметь `source_type`, `target_type`, `cardinality`); наследование области — ADR-004 (I3), как у свойств ([`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 1, правило 4). Ключи свойств (`property_key`) правилом не проверяются: соответствие значения свойства области `applies_to` его определения остаётся кандидатом ([`00-validation-rules.md`](00-validation-rules.md), раздел 7). `defined_by` отношением не является (INV-12) и проверяется правилом `defined-by-consistent`. Тип цели значений `media` и `list<media>` — свойство, а не отношение: его проверяет `media-target-is-image` (INV-23), тип цели ключа `facet` — `facet-target-is-facet`. Неразрешимая ссылка в значении отношения — ошибка `link-target-exists`, а не области; определение отношения в `status: deprecated` остаётся источником нормы для существующих значений ([`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 7.2), поэтому правило продолжает применяться, а предупреждение о ссылке выдаёт `deprecated-link-target`. Отношение, которого нет в хранилище (ключ frontmatter без определения), этим правилом не обнаруживается — это случай кандидата «дубли и неизвестные ключи во frontmatter» ([`00-validation-rules.md`](00-validation-rules.md), раздел 7).

## 4. `relation-cardinality-form` — форма значения соответствует кратности

```yaml
id: 01a17d3b-9c04-7a44-9f34-4c5d6e7f8091
type: validation-rule
defined_by: 01a17d3b-4a04-7c70-99cd-5c01dddac8b4
rule_key: relation-cardinality-form
title: Форма значения соответствует кратности
aliases: [Форма значения соответствует кратности, relation-cardinality-form]
checks: [INV-17, "06-relations.md#1", DL-014]
severity: error
applies_to: "*"
condition: "Форма и наличие значения отношения соответствуют cardinality его определения: при 0..1 и 1..1 значение — одиночная каноническая ссылка, а не список YAML; при 0..* и 1..* — одиночная ссылка или список ссылок; при 1..1 и 1..* значение присутствует и список непустой; при 0..1 и 0..* отсутствие ключа допустимо."
message: "Значение отношения не соответствует кратности определения: при 0..1 и 1..1 требуется одиночная ссылка, при 1..1 и 1..* значение обязательно."
layer: system
status: accepted
owner: human
```

- **Алгоритм:** по индексу определений отношений (правило 17) взять `cardinality` для каждого ключа frontmatter; проверить форму значения (строка-ссылка или список) и его наличие; список из одного элемента при кратности `0..*` и `1..*` допустим — форма не требует ровно одного значения.
- **Границы:** основание — [`../metamodel/06-relations.md`](../metamodel/06-relations.md), раздел 1 («значение хранится в объекте-источнике … множественные значения — список YAML»), разделы 2 и 3 (колонка `cardinality`) и DL-014; отдельного инварианта о форме значения по кратности нет, поэтому `checks` содержит INV-17 (определение обязано иметь `cardinality`), указатель пункта реестра и запись журнала (DL-040). Схема выразить проверку не может: кратность принадлежит определению отношения, то есть другому объекту (ADR-009, S1.2). Обязательность значения `chapter-of` (`1..1`: «глава без книги не существует как самостоятельный объект ядра», раздел 3, правило 4) и `category-domain` (`1..1`, раздел 2, правило 2) проверяется этим же правилом, отдельного правила «отношение обязательно» нет. Обязательность ключа `facet` у значения фасета — требование к свойству, а не к отношению: его контролирует схема [`../../schema/facet-value.json`](../../schema/facet-value.json) (`required`). Кратность свойств (`07-core-properties.md`, раздел 1) этим правилом не проверяется: форма значения свойства контролируется схемой [`../../schema/core-property-values.json`](../../schema/core-property-values.json), а соответствие ключа области применения — кандидат (раздел 7 реестра). Дубли целей внутри списка и repeats значений — кандидат «дубли ключей во frontmatter»; ацикличность `part-of` и `blocks` — правило второй волны `relation-acyclic`.

## 5. `expansion-keys-exist` — определения из ключей правила развёртывания существуют

```yaml
id: 01a17d3b-9c05-7a55-8e45-5d6e7f8091a2
type: validation-rule
defined_by: 01a17d3b-4a04-7c70-99cd-5c01dddac8b4
rule_key: expansion-keys-exist
title: Определения из ключей правила развёртывания существуют
aliases: [Определения из ключей правила развёртывания существуют, expansion-keys-exist]
checks: [INV-25]
severity: error
applies_to: [field-expansion]
condition: "Каждый элемент applies_to_type — type_value существующего определения типа; trigger_property — property_key существующего определения свойства с value_type enum или list<enum>; каждый элемент adds_properties — property_key существующего определения свойства; каждый элемент adds_relations — relation_key существующего определения отношения."
message: "Правило развёртывания ссылается на несуществующее определение: ключ не найден среди type_value, property_key и relation_key хранилища, либо свойство-триггер не является перечислением."
layer: system
status: accepted
owner: human
```

- **Алгоритм:** собрать три множества машинных ключей хранилища — `type_value` определений типов, `property_key` определений свойств, `relation_key` определений отношений (уникальность множеств обеспечивает `unique-machine-keys`); для объекта `type: field-expansion` сверить каждый элемент `applies_to_type`, `trigger_property`, `adds_properties`, `adds_relations` с соответствующим множеством; для `trigger_property` дополнительно загрузить определение свойства и проверить его `value_type` ∈ {`enum`, `list<enum>`}.
- **Границы:** основание — INV-25 ([`../metamodel/09-structural-invariants.md`](../metamodel/09-structural-invariants.md)): существование определений для всех четырёх ключей и требование к `value_type` триггера входят в состав инварианта, поэтому `checks` содержит только INV-25. Принадлежность `trigger_values` множеству `enum_values` триггера проверяет правило первой волны `trigger-values-subset` и не дублируется (ADR-009, S1.3); состав служебных ключей правила и непустоту `applies_to_type`, `trigger_values`, `mode` контролирует схема [`../../schema/system-definitions.json`](../../schema/system-definitions.json) (ветвь `field-expansion-rule`). Отсутствие ключей `adds_properties` и `adds_relations` одновременно (хотя бы один непустой — DL-027) схемой не выражается и остаётся кандидатом; дубликаты внутри списков (INV-25) — кандидат «дубли ключей во frontmatter». Определение в `status: deprecated` считается существующим: правило не срабатывает, а перевод триггера или добавляемого свойства в `deprecated` требует миграции правил развёртывания вручную ([`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 7.5). Применение правила к типу вне `applies_to_type` и вычисление эффективного набора полей (INV-20, INV-26) — алгоритм плагина, а не проверка (ADR-009, S1.4); значения неактивных полей обнаруживает `inactive-field-value`.

## Связанные документы

- [`00-validation-rules.md`](00-validation-rules.md) — формат объекта правила, служебные ключи, `severity`, жизненный цикл, реестр волн (раздел 6.3) и оставшиеся кандидаты (раздел 7).
- [`01-first-wave-rules.md`](01-first-wave-rules.md) — восемь правил первой волны (iter-009).
- [`02-second-wave-rules.md`](02-second-wave-rules.md) — шесть правил второй волны (iter-010).
- [`../adr/ADR-009-phase2-schemas.md`](../adr/ADR-009-phase2-schemas.md) — граница «схема — правило» (S1), формат объекта правила (S5).
- [`../metamodel/05-core-types.md`](../metamodel/05-core-types.md) — группа «Коллекции»: пары «элемент → коллекция» (раздел 5).
- [`../metamodel/06-relations.md`](../metamodel/06-relations.md) — отношения классификации и ядра, `source_type` / `target_type`, `cardinality`.
- [`../metamodel/04-properties.md`](../metamodel/04-properties.md) — ключ `facet` (раздел 6), наследование области применения (раздел 1), поведение при `deprecated` (раздел 7).
- [`../metamodel/08-field-expansion.md`](../metamodel/08-field-expansion.md) — состав правила развёртывания, эффективный набор полей.
- [`../metamodel/09-structural-invariants.md`](../metamodel/09-structural-invariants.md) — INV-17 (определение отношения), INV-25 (правило развёртывания).
- [`../../schema/facet-value.json`](../../schema/facet-value.json), [`../../schema/core-property-values.json`](../../schema/core-property-values.json) — формы, которые правила не дублируют.
- [`../../examples/README.md`](../../examples/README.md) — эталонные заметки, иллюстрирующие правила волны.
- [`../decisions/decision-log.md`](../decisions/decision-log.md) — DL-048 (состав третьей волны и `severity`), DL-049 (расширение набора примеров), DL-025, DL-014, DL-040.
