# Правила валидации: первая волна

Описания восьми правил валидации первой волны (iter-009): объект правила в YAML-форме, условие, алгоритм проверки и границы. Формат объекта и состав ключей — [`00-validation-rules.md`](00-validation-rules.md), раздел 3; решение — [`../adr/ADR-009-phase2-schemas.md`](../adr/ADR-009-phase2-schemas.md) (S5); инварианты — [`../metamodel/01-invariants.md`](../metamodel/01-invariants.md) и [`../metamodel/09-structural-invariants.md`](../metamodel/09-structural-invariants.md).

`id` правил иллюстративные: у правил валидации фиксированных `id` нет, они выдаются при создании объекта (DL-038, по образцу DL-019 и DL-029). Все правила первой волны — `severity: error` и `status: accepted`; предупреждения отложены во вторую волну и реализованы в iter-010 ([`02-second-wave-rules.md`](02-second-wave-rules.md), DL-040), кандидаты третьей волны — [`00-validation-rules.md`](00-validation-rules.md), раздел 7.

## 1. `unique-id` — уникальность `id`

```yaml
id: 01a17d3b-9b01-7c41-8a52-3f6b81c9d041
type: validation-rule
defined_by: 01a17d3b-4a04-7c70-99cd-5c01dddac8b4
rule_key: unique-id
title: Уникальность id
aliases: [Уникальность id, unique-id]
checks: [INV-02]
severity: error
applies_to: "*"
condition: "Во всём хранилище, включая объекты системного слоя, не более одного объекта с данным значением id."
message: "Найден второй объект с тем же id: пространство идентификаторов единое, дубль — ошибка данных, а не слияние."
layer: system
status: accepted
owner: human
```

- **Алгоритм:** обойти все файлы хранилища, у которых присутствуют восемь обязательных свойств (INV-01…INV-12), собрать пары «`id` → файл», сообщить обо всех объектах группы, в которой больше одного элемента.
- **Границы:** неизменяемость `id` (INV-03) правилом не проверяется — это ограничение редактирования, контроль выполняет плагин (фазы 4–5). Файлы без обязательных свойств объектами модели не являются и в обходе не участвуют ([`../metamodel/10-plugin-ux-contracts.md`](../metamodel/10-plugin-ux-contracts.md), раздел 3.5).

## 2. `filename-matches-object` — имя файла соответствует объекту

```yaml
id: 01a17d3b-9b02-7d18-9b73-40c2a5e18f62
type: validation-rule
defined_by: 01a17d3b-4a04-7c70-99cd-5c01dddac8b4
rule_key: filename-matches-object
title: Имя файла соответствует объекту
aliases: [Имя файла соответствует объекту, filename-matches-object]
checks: [INV-05, INV-06]
severity: error
applies_to: "*"
condition: "Имя файла без расширения равно {{type_prefix}}_{{id}}, где type_prefix вычислен из значения type по правилу DL-009, а id совпадает со значением свойства id."
message: "Имя файла не соответствует типу и идентификатору объекта: ожидается {{type_prefix}}_{{id}}.md."
layer: system
status: accepted
owner: human
```

- **Алгоритм:** вычислить `type_prefix` из `type` по шести шагам DL-009 (нижний регистр, разделители в дефис, только `[a-z0-9-]`, убрать дефисы по краям, обрезать до 16 символов, пустой результат — невалиден), сравнить с именем файла до `_`, сравнить хвост имени со значением `id`.
- **Границы:** путь (папка) частью идентичности не является и не проверяется (INV-06); коллизия `type_prefix` у двух разных типов — отдельная проверка, кандидат третьей волны ([`00-validation-rules.md`](00-validation-rules.md), раздел 7); переименование файла при расхождении выполняет плагин, а не правило.

## 3. `aliases-first-equals-title` — `aliases[0]` равен `title`

```yaml
id: 01a17d3b-9b03-7e2a-8c94-51d3b6f29a73
type: validation-rule
defined_by: 01a17d3b-4a04-7c70-99cd-5c01dddac8b4
rule_key: aliases-first-equals-title
title: Первый alias равен названию
aliases: [Первый alias равен названию, aliases-first-equals-title]
checks: [INV-08]
severity: error
applies_to: "*"
condition: "Список aliases непустой и его первый элемент точно равен значению title после удаления пробельных символов по краям."
message: "aliases[0] не равен title: синхронизация обязательна, иначе поиск и ссылки по имени указывают не на тот объект."
layer: system
status: accepted
owner: human
```

- **Алгоритм:** сравнить `aliases[0]` и `title` посимвольно после `trim`; при отсутствии `aliases` или пустом списке сообщить ошибку (форма списка контролируется и схемой [`../../schema/object.json`](../../schema/object.json)).
- **Границы:** состав `aliases[1..]` не ограничивается; равенство `aliases[1]` машинному ключу у определений системного слоя (INV-16, INV-22) — кандидат третьей волны; уникальность самих ключей с iter-010 контролирует правило `unique-machine-keys` ([`02-second-wave-rules.md`](02-second-wave-rules.md)). Синхронизация при изменении `title` выполняется плагином ([`../metamodel/10-plugin-ux-contracts.md`](../metamodel/10-plugin-ux-contracts.md), раздел 3.3).

## 4. `media-target-is-image` — значение `media` указывает на обёртку `image`

```yaml
id: 01a17d3b-9b04-7f3b-9da5-62e4c7a61b85
type: validation-rule
defined_by: 01a17d3b-4a04-7c70-99cd-5c01dddac8b4
rule_key: media-target-is-image
title: Значение media указывает на обёртку изображения
aliases: [Значение media указывает на обёртку изображения, media-target-is-image]
checks: [INV-23]
severity: error
applies_to: "*"
condition: "Каждое значение свойства с value_type media или list<media> — каноническая ссылка на существующий объект type: image; путь к файлу, имя файла и встраивание ![[файл]] значением не являются."
message: "Значение визуального свойства не указывает на обёртку image: ссылка ведёт на объект другого типа или не разрешается."
layer: system
status: accepted
owner: human
```

- **Алгоритм:** по реестрам ([`../metamodel/04-properties.md`](../metamodel/04-properties.md), [`../metamodel/07-core-properties.md`](../metamodel/07-core-properties.md)) определить свойства объекта с `value_type: media` / `list<media>`; для каждой ссылки извлечь `id` цели из канонической формы, найти объект и проверить `type: image`.
- **Границы:** форма значения (префикс `image_`, наличие alias) контролируется схемой [`../../schema/media.json`](../../schema/media.json); цель в `status: deprecated` допустима и остаётся действительной ([`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 7); существование файла по пути `attachment` цели — кандидат третьей волны; существование цели ссылки с iter-010 контролирует правило `link-target-exists`, а ссылку на цель в `deprecated` помечает предупреждение `deprecated-link-target` ([`02-second-wave-rules.md`](02-second-wave-rules.md)).

## 5. `image-has-attachment` — у обёртки `image` есть `attachment`

```yaml
id: 01a17d3b-9b05-704c-8eb6-73f5d8b4bc95
type: validation-rule
defined_by: 01a17d3b-4a04-7c70-99cd-5c01dddac8b4
rule_key: image-has-attachment
title: У обёртки изображения есть вложение
aliases: [У обёртки изображения есть вложение, image-has-attachment]
checks: [INV-24]
severity: error
applies_to: image
condition: "У объекта type: image присутствует ключ attachment с непустым значением — путём к вложению Obsidian относительно хранилища."
message: "Обёртка image без attachment невалидна: вложение обязательно, иначе объект не представляет изображение."
layer: system
status: accepted
owner: human
```

- **Алгоритм:** для объектов с `type: image` проверить присутствие ключа `attachment` и непустоту значения после `trim`.
- **Границы:** требование выражено и в схеме [`../../schema/media.json`](../../schema/media.json); правило сохранено как страховка для объектов, которые схемой не проверялись (импорт заметок, ручная правка frontmatter), и как источник сообщения владельцу. Существование файла по указанному пути не проверяется (INV-24) — кандидат третьей волны (`severity: warning`, [`00-validation-rules.md`](00-validation-rules.md), раздел 7). У типов `file`, `source`, `note` ключ `attachment` необязателен ([`../metamodel/07-core-properties.md`](../metamodel/07-core-properties.md), запись 13).

## 6. `extends-acyclic` — цепочка `extends` ациклична

```yaml
id: 01a17d3b-9b06-715d-9fc7-84a6e9c5cda6
type: validation-rule
defined_by: 01a17d3b-4a04-7c70-99cd-5c01dddac8b4
rule_key: extends-acyclic
title: Цепочка наследования ациклична
aliases: [Цепочка наследования ациклична, extends-acyclic]
checks: [INV-18]
severity: error
applies_to: type
condition: "Обход цепочки extends от определения типа не возвращается ни к одному из уже посещённых определений; у определения не более одного родителя."
message: "Цепочка extends содержит цикл: эффективный набор полей такого типа невычислим."
layer: system
status: accepted
owner: human
```

- **Алгоритм:** для каждого определения `type: type` с ключом `extends` извлечь `id` цели из канонической ссылки, перейти к родителю, вести множество посещённых `id`; повторное посещение — ошибка на всех определениях цикла.
- **Границы:** неразрешимая ссылка `extends` — ошибка существования цели (с iter-010 правило `link-target-exists`), а не цикла; глубина цепочки больше пяти — предупреждение `extends-depth` (вторая волна), требование «родитель — не встроенный метатип» (INV-18, INV-14) — кандидат третьей волны ([`02-second-wave-rules.md`](02-second-wave-rules.md)); кратность `0..1` контролируется схемой ([`../../schema/system-definitions.json`](../../schema/system-definitions.json)).

## 7. `defined-by-consistent` — `defined_by` согласован с `type`

```yaml
id: 01a17d3b-9b07-726e-8ad8-95b7fac6deb7
type: validation-rule
defined_by: 01a17d3b-4a04-7c70-99cd-5c01dddac8b4
rule_key: defined-by-consistent
title: Определение объекта согласовано с его типом
aliases: [Определение объекта согласовано с его типом, defined-by-consistent]
checks: [INV-12, INV-13]
severity: error
applies_to: "*"
condition: "Объект, на который указывает defined_by, существует, имеет layer: system и type: type, а его type_value равен значению type проверяемого объекта."
message: "defined_by указывает не на то определение: объект отсутствует, не принадлежит системному слою или его type_value не совпадает с type объекта."
layer: system
status: accepted
owner: human
```

- **Алгоритм:** загрузить объект по `id` из `defined_by`; проверить `layer: system`, `type: type` и равенство `type_value` цели значению `type` проверяемого объекта; для слоя `classification` целью оказывается встроенный метатип (`domain`, `hierarchical-category`, `facet`, `facet-value`), для слоя `content` — определение типа ядра или пользовательского типа.
- **Границы:** равенство `type_value` цели и `type` объекта автоматически отвергает ссылку на предка по цепочке `extends` — `defined_by` обязан указывать на прямое определение (INV-12). Единственная допустимая самоотсылка — встроенный метатип `type` (`defined_by` равен собственному `id`); она удовлетворяет условию и отдельного исключения не требует. Уникальность `type_value` в пределах хранилища (INV-13) с iter-010 контролируется правилом `unique-machine-keys` ([`02-second-wave-rules.md`](02-second-wave-rules.md)).

## 8. `trigger-values-subset` — `trigger_values` входит в `enum_values` триггера

```yaml
id: 01a17d3b-9b08-737f-9be9-a6c80bd7efc8
type: validation-rule
defined_by: 01a17d3b-4a04-7c70-99cd-5c01dddac8b4
rule_key: trigger-values-subset
title: Значения триггера входят в его набор
aliases: [Значения триггера входят в его набор, trigger-values-subset]
checks: [INV-25]
severity: error
applies_to: field-expansion
condition: "trigger_property — property_key существующего определения свойства с value_type enum или list<enum>, а trigger_values — непустое подмножество enum_values этого определения."
message: "Правило развёртывания ссылается на несуществующий триггер или на значение вне его набора: правило никогда не активируется."
layer: system
status: accepted
owner: human
```

- **Алгоритм:** найти определение свойства по `trigger_property` (уникальность `property_key` с iter-010 контролируется правилом `unique-machine-keys`, [`02-second-wave-rules.md`](02-second-wave-rules.md)), проверить его `value_type`, сравнить множество `trigger_values` с множеством `enum_values` определения; любое значение вне набора — ошибка.
- **Границы:** существование целей `applies_to_type` (`type_value` определений типов), `adds_properties` и `adds_relations` (INV-25) — кандидаты третьей волны ([`00-validation-rules.md`](00-validation-rules.md), раздел 7); обязательность хотя бы одного из `adds_*` и `mode: union` контролируются схемой ([`../../schema/system-definitions.json`](../../schema/system-definitions.json)); расширение `enum_values` триггера владельцем допустимо и правило не ломает (набор расширяем, но не сужаем — [`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 2, правило 4).

## Связанные документы

- [`00-validation-rules.md`](00-validation-rules.md) — формат объекта правила, `severity`, жизненный цикл, первая и вторая волны, связь со схемами.
- [`02-second-wave-rules.md`](02-second-wave-rules.md) — правила второй волны: межобъектные проверки и предупреждения.
- [`../adr/ADR-009-phase2-schemas.md`](../adr/ADR-009-phase2-schemas.md) — решение, альтернативы, последствия.
- [`../../schema/object.json`](../../schema/object.json), [`../../schema/system-definitions.json`](../../schema/system-definitions.json), [`../../schema/media.json`](../../schema/media.json) — схемы первой волны.
- [`../metamodel/01-invariants.md`](../metamodel/01-invariants.md) — INV-01…INV-12 и порядок контроля.
- [`../metamodel/09-structural-invariants.md`](../metamodel/09-structural-invariants.md) — INV-13…INV-27.
- [`../metamodel/08-field-expansion.md`](../metamodel/08-field-expansion.md) — правила развёртывания полей (образец формата объекта-правила).
- [`../decisions/decision-log.md`](../decisions/decision-log.md) — DL-036…DL-042.
