# Правила валидации

Реестр и формат правил валидации фазы 2: как устроен объект `type: validation-rule`, чем правило отличается от JSON Schema, какие правила входят в первую волну и что отложено. Описания правил первой волны — [`01-first-wave-rules.md`](01-first-wave-rules.md); схемы — [`../../schema/`](../../schema/object.json); решение и альтернативы — [`../adr/ADR-009-phase2-schemas.md`](../adr/ADR-009-phase2-schemas.md).

## 1. Правило валидации как объект модели

1. Правило валидации — объект **системного слоя** с `type: validation-rule`; определение задаётся встроенным метатипом 5 ([`../metamodel/03-builtin-types.md`](../metamodel/03-builtin-types.md), `id` `01a17d3b-4a04-7c70-99cd-5c01dddac8b4`), `layer: system`, `defined_by` — `id` этого метатипа (INV-12).
2. Правило можно добавить, отключить и перевести в `deprecated` без изменения кода плагина ([`../PROJECT_BRIEF.md`](../PROJECT_BRIEF.md), принципы 2 и 4; DL-003).
3. Состав объекта: восемь обязательных свойств (INV-01…INV-12) плюс шесть служебных ключей (раздел 3). Формат зафиксирован ADR-009 (S5) и DL-038; в реестре служебных ключей [`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 5 ключи `validation-rule` в этой итерации не регистрировались — регистрация и инвариант состава правила (по образцу INV-25) переносятся в следующую итерацию фазы 2.
4. `id` правила выдаётся при создании объекта и реестром не фиксируется — по образцу типов ядра (DL-019) и правил развёртывания (DL-029, INV-25). В описаниях этого каталога `id` иллюстративные (правило [`../metamodel/03-builtin-types.md`](../metamodel/03-builtin-types.md), раздел «Иллюстративные `id` в примерах»).
5. Файлы этого каталога — документация фазы 2, а не объекты vault: в хранилище правила появятся при bootstrap (фазы 4–5) или создаются владельцем.

## 2. Граница: что проверяет схема, что проверяет правило

| Проверка | Где выражена | Основание |
|---|---|---|
| Присутствие и форма обязательных ключей одного объекта | JSON Schema | ADR-009, S1.1 |
| Допустимость значения (`enum`, `const`, `pattern`, `minItems`) | JSON Schema | ADR-009, S1.1 |
| Условные зависимости внутри одного объекта (`value_type: enum` ⇒ `enum_values`; `type` ⇒ `layer`) | JSON Schema | ADR-009, S1.1 |
| Уникальность `id`, соответствие имени файла, равенство `aliases[0]` и `title`, существование и тип цели ссылки, ацикличность `extends`, согласованность `defined_by` и `type_value`, `trigger_values` ⊆ `enum_values` | Правило валидации | ADR-009, S1.2 |
| Эффективный набор полей и порядок представления (INV-20, INV-26) | Алгоритм плагина, не проверяется | ADR-009, S1.4 |

Правило не дублирует проверку, выразимую схемой (ADR-009, S1.3). Исключение первой волны — `image-has-attachment`: требование `attachment` выражено и в [`../../schema/media.json`](../../schema/media.json), но правило страховает объекты, которые схемой не проверялись (импорт заметок, ручная правка frontmatter); обоснование — в описании правила.

## 3. Служебные ключи объекта правила

| Ключ | `value_type` | `required` | Назначение |
|---|---|---|---|
| `rule_key` | `string` | always | машинный идентификатор правила, ASCII kebab-case, уникален в пределах хранилища; ключ в этом реестре |
| `checks` | `list<string>` | always | непустой список идентификаторов инвариантов (`INV-02`, `INV-06`): связь правила с реестром инвариантов |
| `severity` | `enum` (`error`, `warning`) | always | исход срабатывания: `error` — объект невалиден, `warning` — данные сохраняются, владелец уведомляется |
| `applies_to` | `list<string>` или `"*"` | always | область применения: `*` (все объекты) или список `type_value` — как у определений свойств ([`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 5) |
| `condition` | `text` | always | условие и алгоритм проверки; нормативна семантика, а не реализация (исполняемый код — фазы 4–5) |
| `message` | `string` | always | текст сообщения владельцу при срабатывании |

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
2. **`warning`** — данные допустимы, но требуют внимания владельца: например, глубина цепочки `extends` больше пяти (INV-18), неактивное развёрнутое поле с непустым значением (INV-27), отсутствие файла по пути `attachment` (INV-24). Предупреждение не блокирует сохранение.
3. Третьего уровня нет (ADR-009, А4): исход проверки либо делает объект невалидным, либо нет.
4. Перевод правила из `error` в `warning` и обратно — изменение семантики модели: выполняется через DL и обновление этого реестра.

## 5. Жизненный цикл правила

- Путь правила: `draft` → `accepted` → `deprecated` (INV-10, DL-011).
- Правило в `status: draft` или `deprecated` не применяется к объектам — так же, как правило развёртывания (INV-25; [`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 7).
- Отключение правила владельцем — перевод в `deprecated`; удаление файла не требуется и историю проверок не восстанавливает.
- Новое правило добавляется объектом `type: validation-rule` и записью в этом реестре; изменение состава проверок существующего правила — через DL.

## 6. Первая волна (iter-009): восемь правил

Описания с условием, алгоритмом, сообщением и границами — [`01-first-wave-rules.md`](01-first-wave-rules.md). Все правила первой волны имеют `severity: error`: предупреждения (глубина `extends`, «осиротевшее значение» неактивного поля, `format: audiobook` без `attachment`) отложены во вторую волну.

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

## 7. Вторая волна: кандидаты

| Кандидат | Инвариант / основание | Предполагаемый `severity` |
|---|---|---|
| Файл по пути `attachment` существует в хранилище | INV-24 (второе предложение) | `warning` |
| Цель канонической ссылки существует | INV-15 | `error` |
| Alias ссылки равен `title` цели | INV-15 | `warning` (нормализуется плагином) |
| `aliases[1]` определения равен машинному ключу | INV-16, INV-22 | `warning` |
| Уникальность `type_value`, `property_key`, `relation_key`, `rule_key` | INV-13, INV-16, INV-17 | `error` |
| Глубина цепочки `extends` больше пяти | INV-18, ADR-004 (I1) | `warning` |
| Родитель `extends` — не встроенный метатип | INV-18, INV-14 | `error` |
| `excludes` и `field_order` содержат только ключи набора цепочки | INV-19, INV-20 | `error` |
| Значение свойства соответствует `applies_to` его определения | [`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 1, правило 4 | `error` |
| Соответствие типа элемента и типа коллекции (`part-of-collection`, `chapter-of`) | [`../metamodel/06-relations.md`](../metamodel/06-relations.md), раздел 3 | `error` |
| Ацикличность `parent`, `part-of`, `blocks` | [`../metamodel/06-relations.md`](../metamodel/06-relations.md), разделы 2–3 | `error` |
| Неактивное развёрнутое поле с непустым значением | INV-27, DL-028 | `warning` |
| `format: audiobook` без `attachment` и `duration` | Q-007 | `warning` |
| Значение `enum` / `list<enum>` принадлежит `enum_values` определения | INV-21 | `error` |
| Форма значения по `value_type` (`date`, `datetime`, `number`, `link`, `media`) | INV-21, [`../metamodel/04-properties.md`](../metamodel/04-properties.md), раздел 2 | `error` |

## 8. Связь со схемами `schema/`

| Схема | Класс объектов | Правила первой волны, дополняющие схему |
|---|---|---|
| [`../../schema/object.json`](../../schema/object.json) | любой объект | `unique-id`, `filename-matches-object`, `aliases-first-equals-title`, `defined-by-consistent` |
| [`../../schema/system-definitions.json`](../../schema/system-definitions.json) | определения `type`, `property`, `relation`, `field-expansion` | `extends-acyclic`, `trigger-values-subset`, `defined-by-consistent` |
| [`../../schema/media.json`](../../schema/media.json) | обёртка `image`, значения `media` / `list<media>` | `media-target-is-image`, `image-has-attachment` |

1. Изменение канонического набора (`value_type`, `layer`, `status`, `cardinality`, состав встроенных метатипов) выполняется через DL; тот же DL обновляет схемы и этот реестр — указатели и перекрёстные ссылки правятся по R-007.
2. Схемы не содержат `enum_values` конкретных свойств ядра: наборы значений живут в реестре [`../metamodel/07-core-properties.md`](../metamodel/07-core-properties.md), а контроль значения — правило второй волны.
3. Порядок представления полей (INV-20) схемами не задаётся: он вычисляется и используется плагином и валидатором одинаково.

## Связанные документы

- [`../adr/ADR-009-phase2-schemas.md`](../adr/ADR-009-phase2-schemas.md) — границы первой волны, формат правила, альтернативы.
- [`01-first-wave-rules.md`](01-first-wave-rules.md) — описания восьми правил первой волны.
- [`../metamodel/01-invariants.md`](../metamodel/01-invariants.md) — сводка INV-01…INV-27, универсальные инварианты, порядок контроля.
- [`../metamodel/09-structural-invariants.md`](../metamodel/09-structural-invariants.md) — структурные инварианты INV-13…INV-27.
- [`../metamodel/03-builtin-types.md`](../metamodel/03-builtin-types.md) — встроенный метатип `validation-rule`, правило генерации и иллюстративности `id`.
- [`../metamodel/04-properties.md`](../metamodel/04-properties.md) — служебные ключи определений, процедура `deprecated`.
- [`../metamodel/08-field-expansion.md`](../metamodel/08-field-expansion.md) — образец формата объекта-правила (раздел 6).
- [`../glossary/glossary.md`](../glossary/glossary.md) — термины Validation rule, Rule severity, Rule key.
- [`../decisions/decision-log.md`](../decisions/decision-log.md) — DL-036…DL-039, DL-011, DL-019, DL-029.
