# Правила валидации

Реестр и формат правил валидации фазы 2: как устроен объект `type: validation-rule`, чем правило отличается от JSON Schema, какие правила входят в первую и вторую волны и что отложено. Описания правил — [`01-first-wave-rules.md`](01-first-wave-rules.md) (восемь правил, iter-009) и [`02-second-wave-rules.md`](02-second-wave-rules.md) (шесть правил, iter-010); схемы — [`../../schema/`](../../schema/object.json); решение и альтернативы — [`../adr/ADR-009-phase2-schemas.md`](../adr/ADR-009-phase2-schemas.md), состав волн — DL-039 и DL-040.

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
| Уникальность `id` и машинных ключей, соответствие имени файла, равенство `aliases[0]` и `title`, существование и тип цели ссылки, ацикличность `extends` и иерархических отношений, согласованность `defined_by` и `type_value`, `trigger_values` ⊆ `enum_values` | Правило валидации | ADR-009, S1.2 |
| Состояние, которое ошибкой не является, но требует внимания владельца (неактивное поле со значением, глубина цепочки `extends`, ссылка на объект в `deprecated`) | Правило валидации с `severity: warning` | DL-040, ADR-009 (А4) |
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

Формы идентификаторов в `checks` (DL-040): `INV-NN` — инвариант ([`../metamodel/01-invariants.md`](../metamodel/01-invariants.md), [`../metamodel/09-structural-invariants.md`](../metamodel/09-structural-invariants.md)); `DL-NNN` — запись журнала решений, если ограничение введено решением без инварианта (уникальность `rule_key` — DL-038); `<имя файла реестра>#<раздел>.<пункт>` — пункт реестра, у которого нет инварианта (ацикличность `parent`, `part-of`, `blocks` — `06-relations.md#2.1` и `06-relations.md#3.2`; ссылка на объект в `deprecated` — `04-properties.md#7.1`). Если у ограничения есть инвариант, он указывается обязательно; форма идентификаторов контролируется схемой ([`../../schema/system-definitions.json`](../../schema/system-definitions.json), ветвь `validation-rule-object`).

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
2. **`warning`** — данные допустимы, но требуют внимания владельца: глубина цепочки `extends` больше пяти (INV-18), неактивное развёрнутое поле с непустым значением (INV-27), ссылка на объект в `status: deprecated` (INV-10) — правила второй волны `extends-depth`, `inactive-field-value`, `deprecated-link-target`; кандидаты — отсутствие файла по пути `attachment` (INV-24), `format: audiobook` без `attachment` и `duration` (Q-007), коллизия `type_prefix`. Предупреждение не блокирует сохранение.
3. Третьего уровня нет (ADR-009, А4): исход проверки либо делает объект невалидным, либо нет.
4. Перевод правила из `error` в `warning` и обратно — изменение семантики модели: выполняется через DL и обновление этого реестра.

## 5. Жизненный цикл правила

- Путь правила: `draft` → `accepted` → `deprecated` (INV-10, DL-011).
- Правило в `status: draft` или `deprecated` не применяется к объектам — так же, как правило развёртывания (INV-25; [`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 7).
- Отключение правила владельцем — перевод в `deprecated`; удаление файла не требуется и историю проверок не восстанавливает.
- Новое правило добавляется объектом `type: validation-rule` и записью в этом реестре; изменение состава проверок существующего правила — через DL.

## 6. Волны правил

Нумерация сквозная по всему реестру (1…14): правило не меняет номер при переносе из кандидатов в волну.

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

## 7. Третья волна: кандидаты

| Кандидат | Ограничение / основание | Предполагаемый `severity` |
|---|---|---|
| Файл по пути `attachment` существует в хранилище | INV-24 (второе предложение) | `warning` |
| Alias канонической ссылки равен `title` цели | INV-15 | `warning` (нормализуется плагином) |
| `aliases[1]` определения равен машинному ключу | INV-16, INV-22 | `warning` |
| Родитель `extends` — не встроенный метатип | INV-18, INV-14 | `error` |
| `excludes` и `field_order` содержат только ключи набора цепочки | INV-19, INV-20 | `error` |
| Значение свойства соответствует `applies_to` его определения | [`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 1, правило 4 | `error` |
| Значение `enum` / `list<enum>` принадлежит `enum_values` определения | INV-21 | `error` |
| Форма значения по `value_type` (`date`, `datetime`, `number`, `link`, `media`) | INV-21, [`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 2 | `error` |
| Тип источника и тип цели соответствуют `source_type` / `target_type` определения отношения | INV-17, [`../metamodel/06-relations.md`](../metamodel/06-relations.md), разделы 2–3 | `error` |
| Соответствие типа элемента и типа коллекции (`part-of-collection`, `chapter-of`) | [`../metamodel/06-relations.md`](../metamodel/06-relations.md), раздел 3, правила 4–5 | `error` |
| Согласованность `category-domain` в одной ветке категорий | [`../metamodel/06-relations.md`](../metamodel/06-relations.md), раздел 2, правило 2 | `error` |
| Значение отношения при кратности `0..1` или `1..1` хранится одиночной ссылкой, а не списком | [`../metamodel/06-relations.md`](../metamodel/06-relations.md), раздел 1 | `error` |
| Существование определений из `trigger_property`, `adds_properties`, `adds_relations` | INV-25 | `error` |
| Дубли ключей во frontmatter одной заметки | [`../adr/ADR-009-phase2-schemas.md`](../adr/ADR-009-phase2-schemas.md) (риски) | `error` |
| Коллизия `type_prefix` у двух разных `type_value` | ADR-001, DL-009 | `warning` |
| `format: audiobook` без `attachment` и `duration` | Q-007 | `warning` |
| `requires_properties`: обязательность развёрнутого поля при значении триггера | Q-003, REPORT.md iter-006 (вопрос 5) | `warning` — ключ не введён, механизм не принят |
| Матрица «тип элемента → допустимые типы коллекций» как источник правила соответствия | [`../metamodel/06-relations.md`](../metamodel/06-relations.md), раздел 3, правила 5–7 | `error` — матрица не введена |

Последние два кандидата перечислены без реализации (TASK.md iter-010, «Вне scope»): `requires_properties` не принят как ключ правила развёртывания, а матрица коллекций выводится из `source_type` / `target_type` определений отношений и отдельным реестром не хранится.

## 8. Связь со схемами `schema/`

| Схема | Класс объектов | Правила, дополняющие схему |
|---|---|---|
| [`../../schema/object.json`](../../schema/object.json) | любой объект | `unique-id`, `filename-matches-object`, `aliases-first-equals-title`, `defined-by-consistent`, `link-target-exists`, `deprecated-link-target` |
| [`../../schema/system-definitions.json`](../../schema/system-definitions.json) | определения `type`, `property`, `relation`, `field-expansion`; объект `validation-rule` (пятая ветвь `oneOf`, iter-010) | `extends-acyclic`, `trigger-values-subset`, `defined-by-consistent`, `unique-machine-keys`, `extends-depth`, `inactive-field-value` |
| [`../../schema/media.json`](../../schema/media.json) | обёртка `image`, значения `media` / `list<media>` | `media-target-is-image`, `image-has-attachment`, `link-target-exists` |

1. Изменение канонического набора (`value_type`, `layer`, `status`, `cardinality`, состав встроенных метатипов) выполняется через DL; тот же DL обновляет схемы и этот реестр — указатели и перекрёстные ссылки правятся по R-007.
2. Схемы не содержат `enum_values` конкретных свойств ядра: наборы значений живут в реестре [`../metamodel/07-core-properties.md`](../metamodel/07-core-properties.md), а контроль значения — кандидат третьей волны.
3. Порядок представления полей (INV-20) схемами не задаётся: он вычисляется и используется плагином и валидатором одинаково. Вычисление эффективного набора полей требуется правилу `inactive-field-value` (раздел 6.2) и выполняется по алгоритму [`../metamodel/08-field-expansion.md`](../metamodel/08-field-expansion.md), раздел 4.
4. Ветвь `validation-rule-object` схемы [`../../schema/system-definitions.json`](../../schema/system-definitions.json) проверяет форму объекта правила: шесть служебных ключей, `severity` из двух значений, непустой `checks` с допустимыми формами идентификаторов, `applies_to` в форме `"*"` или списка `type_value`. Состав правил и их семантику схема не ограничивает — это разделы 6 и 7 этого реестра (DL-041).

## Связанные документы

- [`../adr/ADR-009-phase2-schemas.md`](../adr/ADR-009-phase2-schemas.md) — границы первой волны, формат правила, альтернативы.
- [`01-first-wave-rules.md`](01-first-wave-rules.md) — описания восьми правил первой волны (iter-009).
- [`02-second-wave-rules.md`](02-second-wave-rules.md) — описания шести правил второй волны (iter-010).
- [`../metamodel/01-invariants.md`](../metamodel/01-invariants.md) — сводка INV-01…INV-27, универсальные инварианты, порядок контроля.
- [`../metamodel/09-structural-invariants.md`](../metamodel/09-structural-invariants.md) — структурные инварианты INV-13…INV-27.
- [`../metamodel/03-builtin-types.md`](../metamodel/03-builtin-types.md) — встроенный метатип `validation-rule`, правило генерации и иллюстративности `id`.
- [`../metamodel/04-properties.md`](../metamodel/04-properties.md) — служебные ключи определений и правил валидации (раздел 5), процедура `deprecated` (раздел 7).
- [`../metamodel/08-field-expansion.md`](../metamodel/08-field-expansion.md) — образец формата объекта-правила (раздел 6).
- [`../glossary/glossary.md`](../glossary/glossary.md) — термины Validation rule, Rule severity, Rule key.
- [`../decisions/decision-log.md`](../decisions/decision-log.md) — DL-036…DL-042, DL-011, DL-019, DL-028, DL-029.
