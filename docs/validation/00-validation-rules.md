# Правила валидации

Реестр и формат правил валидации фазы 2: как устроен объект `type: validation-rule`, чем правило отличается от JSON Schema, какие правила входят в первую, вторую и третью волны и что отложено. Описания правил — [`01-first-wave-rules.md`](01-first-wave-rules.md) (восемь правил, iter-009), [`02-second-wave-rules.md`](02-second-wave-rules.md) (шесть правил, iter-010) и [`03-third-wave-rules.md`](03-third-wave-rules.md) (пять правил, iter-013); схемы — [`../../schema/`](../../schema/object.json) (пять файлов: `object.json`, `system-definitions.json`, `media.json`, `facet-value.json`, `core-property-values.json`); решения и альтернативы — [`../adr/ADR-009-phase2-schemas.md`](../adr/ADR-009-phase2-schemas.md) и [`../adr/ADR-010-schema-second-wave.md`](../adr/ADR-010-schema-second-wave.md), состав волн — DL-039, DL-040, DL-043…DL-045 и DL-048.

## 1. Правило валидации как объект модели

1. Правило валидации — объект **системного слоя** с `type: validation-rule`; определение задаётся встроенным метатипом 5 ([`../metamodel/03-builtin-types.md`](../metamodel/03-builtin-types.md), `id` `01a17d3b-4a04-7c70-99cd-5c01dddac8b4`), `layer: system`, `defined_by` — `id` этого метатипа (INV-12).
2. Правило можно добавить, отключить и перевести в `deprecated` без изменения кода плагина ([`../PROJECT_BRIEF.md`](../PROJECT_BRIEF.md), принципы 2 и 4; DL-003).
3. Состав объекта: восемь обязательных свойств (INV-01…INV-12) плюс шесть служебных ключей (раздел 3). Формат зафиксирован ADR-009 (S5) и DL-038; с iter-010 ключи зарегистрированы в реестре служебных ключей [`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 5, а форма объекта контролируется схемой [`../../schema/system-definitions.json`](../../schema/system-definitions.json) (ветвь `validation-rule-object`, DL-041). Инвариант состава правила по образцу INV-25 не вводился — его заменяют схема и реестр (DL-041).
4. `id` правила выдаётся при создании объекта и реестром не фиксируется — по образцу типов ядра (DL-019) и правил развёртывания (DL-029, INV-25). В описаниях этого каталога `id` иллюстративные (правило [`../metamodel/03-builtin-types.md`](../metamodel/03-builtin-types.md), раздел «Иллюстративные `id` в примерах»).
5. Файлы этого каталога — документация фазы 2, а не объекты vault: в хранилище правила появятся при bootstrap (фазы 4–5) или создаются владельцем.

## 2. Граница: что проверяет схема, что проверяет правило

| Проверка | Где выражена | Основание |
|---|---|---|
| Присутствие и форма обязательных ключей одного объекта | JSON Schema | ADR-009, S1.1 |
| Допустимость значения (`enum`, `const`, `pattern`, `minItems`) | JSON Schema | ADR-009, S1.1 |
| Условные зависимости внутри одного объекта (`value_type: enum` ⇒ `enum_values`; `type` ⇒ `layer`) | JSON Schema | ADR-009, S1.1 |
| Уникальность `id` и машинных ключей, соответствие имени файла, равенство `aliases[0]` и `title`, существование и тип цели ссылки, ацикличность `extends` и иерархических отношений, согласованность `defined_by` и `type_value`, `trigger_values` ⊆ `enum_values`, тип цели ключа `facet`, тип источника и цели отношения, форма значения отношения по кратности, род элемента и коллекции, существование определений из ключей правила развёртывания | Правило валидации | ADR-009, S1.2 |
| Состояние, которое ошибкой не является, но требует внимания владельца (неактивное поле со значением, глубина цепочки `extends`, ссылка на объект в `deprecated`, элемент и коллекция разного рода) | Правило валидации с `severity: warning` | DL-040, DL-048, ADR-009 (А4) |
| Эффективный набор полей и порядок представления (INV-20, INV-26) | Алгоритм плагина, не проверяется | ADR-009, S1.4 |

Правило не дублирует проверку, выразимую схемой (ADR-009, S1.3). Исключение первой волны — `image-has-attachment`: требование `attachment` выражено и в [`../../schema/media.json`](../../schema/media.json), но правило страховает объекты, которые схемой не проверялись (импорт заметок, ручная правка frontmatter); обоснование — в описании правила.

## 3. Служебные ключи объекта правила

| Ключ | `value_type` | `required` | Назначение |
|---|---|---|---|
| `rule_key` | `string` | always | машинный идентификатор правила, ASCII kebab-case, уникален в пределах хранилища; ключ в этом реестре |
| `checks` | `list<string>` | always | непустой список идентификаторов нормативных ограничений: связь правила с нормой (см. примечание под таблицей) |
| `severity` | `enum` (`error`, `warning`) | always | исход срабатывания: `error` — объект невалиден, `warning` — данные сохраняются, владелец уведомляется |
| `applies_to` | `list<string>` или `"*"` | always | область применения: `*` (все объекты) или список `type_value` — как у определений свойств ([`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 5) |
| `condition` | `text` | always | условие и алгоритм проверки; нормативна семантика, а не реализация (исполняемый код — фазы 4–5) |
| `message` | `string` | always | текст сообщения владельцу при срабатывании |

Формы идентификаторов в `checks` (DL-040): `INV-NN` — инвариант ([`../metamodel/01-invariants.md`](../metamodel/01-invariants.md), [`../metamodel/09-structural-invariants.md`](../metamodel/09-structural-invariants.md)); `DL-NNN` — запись журнала решений, если ограничение введено решением без инварианта (уникальность `rule_key` — DL-038, пары «элемент → коллекция» — DL-025); `<имя файла реестра>#<раздел>[.<пункт>]` — раздел или пункт реестра, у которого нет инварианта (ацикличность `parent`, `part-of`, `blocks` — `06-relations.md#2.1` и `06-relations.md#3.2`; ссылка на объект в `deprecated` — `04-properties.md#7.1`; тип цели ключа `facet` — `04-properties.md#6`; соответствие типа элемента и коллекции — `05-core-types.md#5`; область и кратность отношения — `06-relations.md#1`…`06-relations.md#3`). Если у ограничения есть инвариант, он указывается обязательно; форма идентификаторов контролируется схемой ([`../../schema/system-definitions.json`](../../schema/system-definitions.json), ветвь `validation-rule-object`).

Обязательные свойства и ключи в YAML-форме (шаблон; `id` иллюстративный):

```yaml
id: 01a17d3b-9b01-7c41-8a52-3f6b81c9d041                # выдаётся при создании
type: validation-rule
defined_by: 01a17d3b-4a04-7c70-99cd-5c01dddac8b4        # встроенный метатип `validation-rule`
rule_key: unique-id
title: Уникальность id                                   # это же значение — label (INV-22)
aliases:
  - Уникальность id                                      # aliases[0] = title (INV-08)
  - unique-id                                            # aliases[1] = rule_key (по образцу INV-16)
checks:
  - INV-02
severity: error
applies_to: "*"
condition: >-
  Во всём хранилище не более одного объекта с данным значением id.
message: "Объект с таким id уже существует: два объекта с одинаковым id — ошибка данных, а не слияние."
layer: system
status: accepted
owner: human
# имя файла: validation-rule_01a17d3b-9b01-7c41-8a52-3f6b81c9d041.md
```

## 4. `severity`: два исхода проверки

1. **`error`** — нарушен инвариант: объект невалиден, не принимается как источник определений и не используется как основа автоматизаций ([`../metamodel/01-invariants.md`](../metamodel/01-invariants.md), «Как контролируются инварианты»). Данные сохраняются (плагин не удаляет заметки), но объект помечен ошибкой.
2. **`warning`** — данные допустимы, но требуют внимания владельца: глубина цепочки `extends` больше пяти (INV-18), неактивное развёрнутое поле с непустым значением (INV-27), ссылка на объект в `status: deprecated` (INV-10) — правила второй волны `extends-depth`, `inactive-field-value`, `deprecated-link-target`; элемент и коллекция разного рода при формально допустимой паре `source_type` / `target_type` ([`../metamodel/05-core-types.md`](../metamodel/05-core-types.md), раздел 5, правило 3) — правило третьей волны `collection-element-consistent` (DL-048); кандидаты — отсутствие файла по пути `attachment` (INV-24), `format: audiobook` без `attachment` и `duration` (Q-007), коллизия `type_prefix`. Предупреждение не блокирует сохранение.
3. Третьего уровня нет (ADR-009, А4): исход проверки либо делает объект невалидным, либо нет.
4. Перевод правила из `error` в `warning` и обратно — изменение семантики модели: выполняется через DL и обновление этого реестра.

## 5. Жизненный цикл правила

- Путь правила: `draft` → `accepted` → `deprecated` (INV-10, DL-011).
- Правило в `status: draft` или `deprecated` не применяется к объектам — так же, как правило развёртывания (INV-25; [`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 7).
- Отключение правила владельцем — перевод в `deprecated`; удаление файла не требуется и историю проверок не восстанавливает.
- Новое правило добавляется объектом `type: validation-rule` и записью в этом реестре; изменение состава проверок существующего правила — через DL.

## 6. Волны правил

Нумерация сквозная по всему реестру (1…19): правило не меняет номер при переносе из кандидатов в волну.

### 6.1 Первая волна (iter-009): восемь правил

Описания с условием, алгоритмом, сообщением и границами — [`01-first-wave-rules.md`](01-first-wave-rules.md). Все правила первой волны имеют `severity: error`.

| № | `rule_key` | Название | Инварианты | `applies_to` | `severity` |
|---|---|---|---|---|---|
| 1 | `unique-id` | Уникальность `id` | INV-02 | `*` | `error` |
| 2 | `filename-matches-object` | Имя файла соответствует объекту | INV-05, INV-06 | `*` | `error` |
| 3 | `aliases-first-equals-title` | `aliases[0]` равен `title` | INV-08 | `*` | `error` |
| 4 | `media-target-is-image` | Значение `media` указывает на обёртку `image` | INV-23 | `*` | `error` |
| 5 | `image-has-attachment` | У обёртки `image` есть `attachment` | INV-24 | `image` | `error` |
| 6 | `extends-acyclic` | Цепочка `extends` ациклична | INV-18 | `type` | `error` |
| 7 | `defined-by-consistent` | `defined_by` согласован с `type` | INV-12, INV-13 | `*` | `error` |
| 8 | `trigger-values-subset` | `trigger_values` — подмножество `enum_values` триггера | INV-25 | `field-expansion` | `error` |

Соответствие перечню TASK.md iter-009: правила 1, 2, 4, 5, 6, 7, 8 — из задания; правило 3 (`aliases[0] = title`) добавлено по списку кандидатов первой очереди [`../metamodel/01-invariants.md`](../metamodel/01-invariants.md) («Как контролируются инварианты»).

### 6.2 Вторая волна (iter-010): шесть правил

Описания с условием, алгоритмом, сообщением и границами — [`02-second-wave-rules.md`](02-second-wave-rules.md). Три межобъектные проверки с `severity: error` и три предупреждения; состав волны и шкала — DL-040.

| № | `rule_key` | Название | Ограничения (`checks`) | `applies_to` | `severity` |
|---|---|---|---|---|---|
| 9 | `link-target-exists` | Цель канонической ссылки существует | INV-15, INV-23 | `*` | `error` |
| 10 | `unique-machine-keys` | Машинные ключи уникальны | INV-13, INV-16, INV-17, DL-038 | `type`, `property`, `relation`, `validation-rule` | `error` |
| 11 | `relation-acyclic` | Иерархические отношения ацикличны | `06-relations.md#2.1`, `06-relations.md#3.2` | `*` | `error` |
| 12 | `inactive-field-value` | Неактивное поле со значением | INV-27, DL-028 | `*` | `warning` |
| 13 | `extends-depth` | Глубина цепочки наследования | INV-18 | `type` | `warning` |
| 14 | `deprecated-link-target` | Ссылка на устаревший объект | INV-10, `04-properties.md#7.1` | `*` | `warning` |

Соответствие перечню TASK.md iter-010: правила 9, 10, 11 — обязательный минимум (существование цели канонической ссылки и `media-link`; уникальность `property_key` / `relation_key` / `type_value` / `rule_key`; ацикличность `parent`, `part-of`, `blocks`); правила 12–14 — три предупреждения (INV-27 «осиротевшее значение», глубина `extends`, ссылка на объект в `deprecated`).

Правило 10 объединяет четыре машинных ключа в одну проверку, потому что алгоритм один (группировка по значению ключа в пределах хранилища), а сообщение владельцу отличается только видом ключа; разделение на четыре правила потребовало бы четырёх объектов с одинаковым условием.

### 6.3 Третья волна (iter-013): пять правил

Описания с условием, алгоритмом, сообщением и границами — [`03-third-wave-rules.md`](03-third-wave-rules.md). Четыре межобъектные проверки с `severity: error` и одно предупреждение; состав волны, выбор `severity` и отклонённые альтернативы — DL-048.

| № | `rule_key` | Название | Ограничения (`checks`) | `applies_to` | `severity` |
|---|---|---|---|---|---|
| 15 | `facet-target-is-facet` | Цель ключа `facet` является фасетом | INV-15, `04-properties.md#6` | `facet-value` | `error` |
| 16 | `collection-element-consistent` | Элемент и коллекция одного рода | DL-025, `05-core-types.md#5` | `film`, `track`, `image` | `warning` |
| 17 | `relation-endpoints-match` | Область отношения соблюдена | INV-17, `06-relations.md#3`, `06-relations.md#2` | `*` | `error` |
| 18 | `relation-cardinality-form` | Форма значения соответствует кратности | INV-17, `06-relations.md#1`, DL-014 | `*` | `error` |
| 19 | `expansion-keys-exist` | Определения из ключей правила развёртывания существуют | INV-25 | `field-expansion` | `error` |

Соответствие перечню TASK.md iter-013: правила 15 и 16 — обязательный минимум (тип цели ключа `facet` значения фасета; согласованность элемента и коллекции для `part-of-collection`), правила 17–19 — три кандидата раздела 7, взятые в волну (область отношения, форма значения по кратности, существование определений из ключей правила развёртывания).

Правило 16 — единственное предупреждение волны: соответствие типа элемента и коллекции не является инвариантом модели ([`../metamodel/05-core-types.md`](../metamodel/05-core-types.md), раздел 5, правило 3), а жёсткая часть ограничения — принадлежность пары типов областям `source_type` и `target_type` отношения `part-of-collection` — проверяется правилом 17 с `severity: error`. Правила 17 и 18 не объединены, хотя оба разбирают значения отношений: основания разные (область определения против формы хранения по кратности), сообщения разные, а правило 18 срабатывает и при отсутствии значения — тогда правилу 17 проверять нечего.

Пять правил закрывают проверки, которые в разделе «Как контролируются инварианты» ([`../metamodel/01-invariants.md`](../metamodel/01-invariants.md)) числились кандидатами третьей волны: тип цели ключа `facet` (INV-15), область отношения и форма его значения (INV-17), существование определений из ключей правила развёртывания (INV-25). Новые схемы не добавлялись: ни одна из пяти проверок не выражается схемой, так как требует другого объекта (ADR-009, S1.2).

## 7. Кандидаты следующих волн

Четырнадцать кандидатов. Пять строк прежнего раздела перенесены в третью волну (раздел 6.3, DL-048): тип цели ключа `facet` (правило 15), соответствие типа элемента и коллекции в части `part-of-collection` (правило 16; пара `chapter` → `book` отношения `chapter-of` проверяется правилом 17 как область отношения), тип источника и цели отношения (правило 17), форма значения по кратности (правило 18), существование определений из `trigger_property`, `adds_properties`, `adds_relations` (правило 19). Два кандидата отложены сознательно, а не забыты: соответствие значения свойства `applies_to` его определения и принадлежность значения `enum_values` требуют полного реестра определений в хранилище, поэтому реализуются вместе с bootstrap (фазы 4–5).

| Кандидат | Ограничение / основание | Предполагаемый `severity` |
|---|---|---|
| Файл по пути `attachment` существует в хранилище | INV-24 (второе предложение) | `warning` |
| Alias канонической ссылки равен `title` цели | INV-15 | `warning` (нормализуется плагином) |
| `aliases[1]` определения равен машинному ключу | INV-16, INV-22 | `warning` |
| Родитель `extends` — не встроенный метатип | INV-18, INV-14 | `error` |
| `excludes` и `field_order` содержат только ключи набора цепочки | INV-19, INV-20 | `error` |
| Значение свойства соответствует `applies_to` его определения | [`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 1, правило 4 | `error` |
| Значение `enum` / `list<enum>` принадлежит `enum_values` определения | INV-21 | `error` |
| Форма значения по `value_type` (`date`, `datetime`, `number`, `link`, `media`) — для одиннадцати ключей свойств ядра вне [`../../schema/core-property-values.json`](../../schema/core-property-values.json) и для значений отношений | INV-21, [`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 2; форма значений двенадцати ключей выражена схемой (iter-011, DL-044) | `error` |
| Согласованность `category-domain` в одной ветке категорий | [`../metamodel/06-relations.md`](../metamodel/06-relations.md), раздел 2, правило 2 | `error` |
| Дубли ключей во frontmatter одной заметки | [`../adr/ADR-009-phase2-schemas.md`](../adr/ADR-009-phase2-schemas.md) (риски) | `error` |
| Коллизия `type_prefix` у двух разных `type_value` | ADR-001, DL-009 | `warning` |
| `format: audiobook` без `attachment` и `duration` | Q-007 | `warning` |
| `requires_properties`: обязательность развёрнутого поля при значении триггера | Q-003, REPORT.md iter-006 (вопрос 5) | `warning` — ключ не введён, механизм не принят |
| Матрица «тип элемента → допустимые типы коллекций» как источник правила соответствия | [`../metamodel/06-relations.md`](../metamodel/06-relations.md), раздел 3, правила 5–7 | `error` — матрица не введена |

Последние два кандидата перечислены без реализации (TASK.md iter-010, «Вне scope»): `requires_properties` не принят как ключ правила развёртывания, а матрица коллекций выводится из `source_type` / `target_type` определений отношений и отдельным реестром не хранится. Правило 16 использует как источник пары «элемент → коллекция» из [`../metamodel/05-core-types.md`](../metamodel/05-core-types.md), раздел 5, поэтому отдельный реестр матрицы по-прежнему не введён.

## 8. Связь со схемами `schema/`

| Схема | Класс объектов | Правила, дополняющие схему |
|---|---|---|
| [`../../schema/object.json`](../../schema/object.json) | любой объект | `unique-id`, `filename-matches-object`, `aliases-first-equals-title`, `defined-by-consistent`, `link-target-exists`, `deprecated-link-target`, `relation-endpoints-match`, `relation-cardinality-form`, `collection-element-consistent` |
| [`../../schema/system-definitions.json`](../../schema/system-definitions.json) | определения `type`, `property`, `relation`, `field-expansion`; объект `validation-rule` (пятая ветвь `oneOf`, iter-010) | `extends-acyclic`, `trigger-values-subset`, `defined-by-consistent`, `unique-machine-keys`, `extends-depth`, `inactive-field-value`, `expansion-keys-exist` |
| [`../../schema/media.json`](../../schema/media.json) | обёртка `image`, значения `media` / `list<media>` | `media-target-is-image`, `image-has-attachment`, `link-target-exists` |
| [`../../schema/facet-value.json`](../../schema/facet-value.json) | объект `type: facet-value` (слой классификации), ключ `facet` | `link-target-exists`, `defined-by-consistent`, `unique-id`, `filename-matches-object`, `aliases-first-equals-title`, `deprecated-link-target`, `facet-target-is-facet` |
| [`../../schema/core-property-values.json`](../../schema/core-property-values.json) | формы значений по `value_type` и двенадцать ключей свойств ядра (фрагмент документа frontmatter) | `media-target-is-image`, `link-target-exists`, `inactive-field-value`; кандидаты — соответствие значения `applies_to` определения и принадлежность значения `enum_values` |

1. Изменение канонического набора (`value_type`, `layer`, `status`, `cardinality`, состав встроенных метатипов) выполняется через DL; тот же DL обновляет схемы и этот реестр — указатели и перекрёстные ссылки правятся по R-007.
2. Схемы не содержат `enum_values` конкретных свойств ядра: наборы значений живут в реестре [`../metamodel/07-core-properties.md`](../metamodel/07-core-properties.md), а принадлежность значения набору — кандидат следующих волн (раздел 7): в третью волну (iter-013, DL-048) правило не вошло, так как требует полного реестра определений в хранилище. С iter-011 форма значений двенадцати ключей свойств ядра выражена схемой [`../../schema/core-property-values.json`](../../schema/core-property-values.json): наборы значений в неё не переносились (DL-044, ADR-010, W3).
3. Порядок представления полей (INV-20) схемами не задаётся: он вычисляется и используется плагином и валидатором одинаково. Вычисление эффективного набора полей требуется правилу `inactive-field-value` (раздел 6.2) и выполняется по алгоритму [`../metamodel/08-field-expansion.md`](../metamodel/08-field-expansion.md), раздел 4.
4. Ветвь `validation-rule-object` схемы [`../../schema/system-definitions.json`](../../schema/system-definitions.json) проверяет форму объекта правила: шесть служебных ключей, `severity` из двух значений, непустой `checks` с допустимыми формами идентификаторов, `applies_to` в форме `"*"` или списка `type_value`. Состав правил и их семантику схема не ограничивает — это разделы 6 и 7 этого реестра (DL-041).
5. Схемы второй волны (iter-011, DL-043…DL-045, [`../adr/ADR-010-schema-second-wave.md`](../adr/ADR-010-schema-second-wave.md)): [`../../schema/facet-value.json`](../../schema/facet-value.json) проверяет форму объекта `type: facet-value` и обязательного ключа `facet` (каноническая ссылка с префиксом `facet_`, одиночная форма по кратности `1..1`); тип цели ключа с iter-013 проверяет правило `facet-target-is-facet` (раздел 6.3, DL-048). [`../../schema/core-property-values.json`](../../schema/core-property-values.json) — частичная схема документа: применяется вместе со схемой класса объекта, проверяет форму значения двенадцати ключей, если ключ присутствует, и не ограничивает состав полей (`additionalProperties` не запрещён, ADR-009, S2.4). Соответствие ключа области применения `applies_to` и эффективный набор полей схема не проверяет (INV-20, INV-26, ADR-009, S1.4) — это кандидаты раздела 7.

## Связанные документы

- [`../adr/ADR-009-phase2-schemas.md`](../adr/ADR-009-phase2-schemas.md) — границы первой волны, формат правила, альтернативы.
- [`../adr/ADR-010-schema-second-wave.md`](../adr/ADR-010-schema-second-wave.md) — состав второй волны схем, форма значения и наборы значений, частичная схема документа, альтернативы.
- [`01-first-wave-rules.md`](01-first-wave-rules.md) — описания восьми правил первой волны (iter-009).
- [`02-second-wave-rules.md`](02-second-wave-rules.md) — описания шести правил второй волны (iter-010).
- [`03-third-wave-rules.md`](03-third-wave-rules.md) — описания пяти правил третьей волны (iter-013).
- [`../metamodel/01-invariants.md`](../metamodel/01-invariants.md) — сводка INV-01…INV-27, универсальные инварианты, порядок контроля.
- [`../metamodel/09-structural-invariants.md`](../metamodel/09-structural-invariants.md) — структурные инварианты INV-13…INV-27.
- [`../metamodel/03-builtin-types.md`](../metamodel/03-builtin-types.md) — встроенный метатип `validation-rule`, правило генерации и иллюстративности `id`.
- [`../metamodel/04-properties.md`](../metamodel/04-properties.md) — служебные ключи определений и правил валидации (раздел 5), процедура `deprecated` (раздел 7).
- [`../metamodel/08-field-expansion.md`](../metamodel/08-field-expansion.md) — образец формата объекта-правила (раздел 6).
- [`../glossary/glossary.md`](../glossary/glossary.md) — термины Validation rule, Rule severity, Rule key, Third wave.
- [`../../schema/facet-value.json`](../../schema/facet-value.json), [`../../schema/core-property-values.json`](../../schema/core-property-values.json) — схемы второй волны: значение фасета, формы значений и ключи свойств ядра.
- [`../../examples/README.md`](../../examples/README.md) — эталонные заметки и покрытие девятнадцати правил данными (iter-012, iter-013).
- [`../decisions/decision-log.md`](../decisions/decision-log.md) — DL-036…DL-049, DL-011, DL-014, DL-019, DL-025, DL-028, DL-029.
