# Свойства ядра

Реестр свойств ядра слоя наполнения: 23 определения с фиксированными `id` — четыре визуальных (`value_type: media`, `list<media>`), одиннадцать типовых (адреса, идентификаторы, даты, длительность, порядок, локация, вложение), три триггера развёртывания полей и пять полей, которые они разворачивают. Свойства ядра — обычные объекты `type: property`: они не являются встроенными метатипами и не защищены INV-14, но их состав и `id` зафиксированы этим реестром (DL-026, DL-027).

Механика key / label и `value_type` — [`04-properties.md`](04-properties.md), разделы 1–2; типы ядра — [`05-core-types.md`](05-core-types.md); отношения ядра — [`06-relations.md`](06-relations.md), раздел 3; инварианты — [`01-invariants.md`](01-invariants.md) и [`09-structural-invariants.md`](09-structural-invariants.md) (INV-21, INV-23…INV-27); развёртывание полей — [`08-field-expansion.md`](08-field-expansion.md); решения — DL-023, DL-024, DL-026…DL-028 и [`../adr/ADR-005-core-extension-and-split.md`](../adr/ADR-005-core-extension-and-split.md), [`../adr/ADR-006-field-expansion.md`](../adr/ADR-006-field-expansion.md).

## 1. Реестр свойств ядра

`id` фиксированы и выданы один раз (правило генерации — [`03-builtin-types.md`](03-builtin-types.md), раздел «Как сгенерированы `id`»: итерация iter-005, смещения 33…47 — записи 1–15; итерация iter-006, смещения 51…58 — записи 16–23). `label` (= `title`) — на русском, `property_key` — на английском ASCII (INV-16, INV-17; [`04-properties.md`](04-properties.md), раздел 3). Область применения наследуется: значение `source` покрывает `book`, `article`, `video`, `link`, `film`, `track`, `chapter` (ADR-004, I3).

| № | `property_key` | `label` (= `title`) | `id` определения | `value_type` | `required` | `applies_to` | Назначение |
|---|---|---|---|---|---|---|---|
| 1 | `cover` | Обложка | `01a17d3b-4a21-787a-b3db-b9365bb54266` | `media` | conditional | `source`, `album`, `film-series` | обложка издания, альбома, серии |
| 2 | `poster` | Постер | `01a17d3b-4a22-7aff-9916-309493bbe456` | `media` | conditional | `film`, `video`, `film-series` | афиша фильма, видеозаписи, серии |
| 3 | `photo` | Фотография | `01a17d3b-4a23-7130-aeb4-c8d92deafda4` | `media` | conditional | `person`, `place`, `organization` | портрет, вид места, логотип организации |
| 4 | `artwork` | Иллюстрации | `01a17d3b-4a24-7034-afca-f8fcfddf52eb` | `list<media>` | conditional | `note`, `source`, `event`, `place` | подборка изображений к объекту: схемы, кадры, скриншоты |
| 5 | `url` | URL | `01a17d3b-4a25-741b-b01d-7f64cec2571b` | `string` | conditional | `source`, `organization`, `place`, `project`, `event` | внешний адрес ресурса |
| 6 | `isbn` | ISBN | `01a17d3b-4a26-71b0-978c-95e191399813` | `string` | conditional | `book` | международный идентификатор издания |
| 7 | `published` | Дата публикации | `01a17d3b-4a27-78cc-88d6-b3b244b255cd` | `date` | conditional | `source`, `album` | дата выхода издания или альбома |
| 8 | `year` | Год | `01a17d3b-4a28-7d64-8bc6-e7e962967e84` | `number` | conditional | `source`, `album`, `film-series` | год выхода, когда точная дата неизвестна |
| 9 | `duration` | Длительность | `01a17d3b-4a29-7429-ace2-390ed40a7c17` | `number` | conditional | `film`, `video`, `track`, `chapter`, `event`, `book` | длительность в минутах; у книги — при `format: audiobook` (iter-006) |
| 10 | `date` | Дата | `01a17d3b-4a2a-700b-9630-38e1c06ca1a6` | `date` | conditional | `event`, `decision` | дата события или дата принятия решения |
| 11 | `due` | Срок | `01a17d3b-4a2b-799a-9149-18624088f8fc` | `date` | conditional | `task`, `project`, `goal` | плановая дата завершения |
| 12 | `completed` | Выполнено | `01a17d3b-4a2c-727b-8bc1-0f1489852434` | `date` | conditional | `task`, `project`, `goal` | фактическая дата завершения; отсутствие ключа — работа не завершена |
| 13 | `attachment` | Вложение | `01a17d3b-4a2d-7e3a-8854-8ad30b167096` | `string` | conditional | `file`, `source`, `note` | путь к вложению Obsidian относительно хранилища; обязателен для `image` (INV-24) |
| 14 | `position` | Позиция | `01a17d3b-4a2e-78af-a937-7cf8eaeca532` | `number` | conditional | `chapter`, `film`, `track`, `image` | порядковый номер в книге, коллекции или галерее |
| 15 | `page` | Страница | `01a17d3b-4a2f-7627-8dbc-7246566a9fe4` | `string` | conditional | `quote`, `chapter`, `note` | локация в источнике: страницы, диапазон, таймкод |
| 16 | `occupation` | Профессия | `01a17d3b-4a33-7c11-b7a3-eedf1df9d167` | `list<enum>` | conditional | `person` | **триггер**: `developer`, `designer`, `researcher`, `teacher`, `writer`, `manager` |
| 17 | `format` | Формат издания | `01a17d3b-4a34-75da-9fa0-b3e3ccd3855c` | `enum` | conditional | `book` | **триггер**: `ebook`, `paper`, `audiobook` |
| 18 | `creation-method` | Способ создания | `01a17d3b-4a35-7283-bb07-60578db23edc` | `enum` | conditional | `image` | **триггер**: `ai-generated`, `photograph`, `scan`, `illustration` |
| 19 | `specialization` | Специализация | `01a17d3b-4a36-72e1-bac2-17c7436cba22` | `list<string>` | conditional | `person` | уточнение профессии: языки, инструменты, предметные области |
| 20 | `model` | Модель | `01a17d3b-4a37-7995-a6f3-72a0487e4345` | `string` | conditional | `image` | модель генерации изображения |
| 21 | `prompt` | Запрос | `01a17d3b-4a38-7992-9374-8acf82aef7ab` | `text` | conditional | `image` | текст запроса генерации |
| 22 | `seed` | Сид | `01a17d3b-4a39-7837-9411-d1d674b55407` | `number` | conditional | `image` | значение сида генерации |
| 23 | `page-count` | Объём в страницах | `01a17d3b-4a3a-7767-bf13-a744830e3779` | `number` | conditional | `book`, `chapter` | число страниц издания или главы; не путать с `page` (запись 15) — локацией цитаты |

## 2. Визуальные свойства и обёртка `image`

Записи 1–4 — визуальные свойства (DL-023, DL-024):

1. Значение — **каноническая ссылка на обёртку изображения** (объект `type: image`, INV-23), а не путь к файлу и не имя файла: `"[[image_{{id}}|{{title}}]]"`. Для `artwork` — список YAML таких ссылок.
2. Обёртка `image` обязана иметь `attachment` (INV-24; [`05-core-types.md`](05-core-types.md), раздел 4.2): сам графический файл остаётся вложением Obsidian и не является объектом модели.
3. Один объект `image` может быть значением нескольких визуальных свойств разных объектов (обложка книги и элемент галереи одновременно) — переиспользование допустимо, копирование файла не требуется.
4. В интерфейсе визуальные свойства отображаются превью обёртки, `artwork` — галереей миниатюр (контракт — [`06-relations.md`](06-relations.md), раздел 5, п. 10).
5. Различие `cover` и `poster`: `cover` — обложка издания или альбома (книга, статья, альбом), `poster` — афиша экранного произведения (фильм, видео, серия). У `film` и `film-series` допустимы оба значения: `poster` наследуется по `applies_to`, `cover` — через предка `source`.

```yaml
# фрагмент frontmatter экземпляра книги (роль «карточка + файл», раздел 4.1 `05-core-types.md`)
cover: "[[image_01a17d3b-6b30-7f11-9c42-6a2f7d1e5b84|Обложка книги How to Take Smart Notes]]"
artwork:
  - "[[image_01a17d3b-6b31-7a52-8d17-3f9c2b7e6a41|Схема цикла Zettelkasten]]"
  - "[[image_01a17d3b-6b32-7c68-9e24-5a1d8f3b7c92|Скриншот графа заметок]]"
isbn: 978-1-9553-8817-6
published: 2022-02-15
attachment: How to Take Smart Notes.pdf
```

## 3. Типовые свойства

1. **`attachment`** (запись 13) хранит путь к вложению строкой, как его записывает Obsidian (имя файла или путь относительно хранилища). Значение не является внутренней ссылкой, поэтому каноническая форма (INV-15) к нему не применяется; сам файл не является объектом модели (INV-24). Обязателен для `image`, для остальных типов области применения — по желанию владельца.
2. **`position`** (запись 14) задаёт порядок элемента внутри книги (`chapter`) или коллекции (`film`, `track`, `image`); нумерация с 1, пропуски допустимы. Порядок не хранится списком в книге или коллекции ([`06-relations.md`](06-relations.md), раздел 3, правила 4–5).
3. **`page`** (запись 15) — строка, а не число: диапазон («42–45»), таймкод («00:12:30») и подпись («приложение B») одинаково допустимы. Локация уточняет `derived-from`, а не заменяет его.
4. **Время и сроки** (записи 7, 8, 10–12): `date` — ISO 8601 без времени; `datetime` в ядре не используется. `due` — план, `completed` — факт; признак «не завершено» выражается отсутствием ключа `completed`, а не значением `false`, потому что пустое значение свойства — отсутствие ключа ([`04-properties.md`](04-properties.md), раздел 2, правило 2).
5. **Единицы измерения не хранятся в значении** (`number`): `duration` — минуты, `year` — год четырьмя цифрами, `position` — порядковый номер. Единица фиксируется в определении свойства (поле «Назначение» и тело заметки), а не в данных.
6. **`url`** хранит адрес строкой; канонической формой для внутренних связей остаётся ссылка (INV-15), `url` относится только к внешним ресурсам.
7. **Свойства-триггеры** (записи 16–18, iter-006): `value_type` — `enum` или `list<enum>`, набор значений — в `enum_values` определения; стартовый набор зафиксирован в колонке «Назначение» и расширяем владельцем ([`04-properties.md`](04-properties.md), раздел 2, правило 4). Значение триггера определяет, какие правила развёртывания активны для объекта: механизм, вычисление и примеры — [`08-field-expansion.md`](08-field-expansion.md).
8. **Поля, разворачиваемые триггерами** (записи 19–23, iter-006): `specialization` — при `occupation`; `model`, `prompt`, `seed` — при `creation-method: ai-generated`; `page-count` — при `format: paper`. Это обычные свойства ядра: они допустимы и без триггера (правило развёртывания управляет составом формы, а не допустимостью значения), их `required` остаётся `conditional`.

## 4. Пример объекта-определения свойства ядра

```yaml
id: 01a17d3b-4a21-787a-b3db-b9365bb54266
type: property
defined_by: 01a17d3b-4a01-73dd-8782-259a7e45663f   # встроенный метатип `property`
property_key: cover
title: Обложка                                       # это же значение — label
aliases:
  - Обложка                                          # aliases[0] = title
  - cover                                            # aliases[1] = property_key
value_type: media
required: conditional
applies_to:
  - source
  - album
  - film-series
layer: system
status: accepted
owner: human
# имя файла: property_01a17d3b-4a21-787a-b3db-b9365bb54266.md
# значение — каноническая ссылка на объект `type: image` (INV-23)
```

## 5. Правила

1. **Состав реестра закрыт на итерацию.** Новое свойство ядра добавляется только через DL с обновлением этого файла. Ориентир 10–18 записей (TASK.md iter-005) превышен в iter-006: восемь записей добавлены как триггеры и необходимые им поля (TASK.md iter-006, DL-027), ориентир для следующих итераций — не более 30 записей до выделения групп в отдельные реестры. Свойства вне реестра создаются владельцем как объекты `type: property` — код плагина не меняется.
2. **`id` фиксированы** и не переиспользуются: свойство ядра в `deprecated` не освобождает свой `id` и свой `property_key` (INV-13 по аналогии с `type_value`; [`04-properties.md`](04-properties.md), раздел 7.5).
3. **`value_type` неизменяем** после `accepted` (INV-21): замена типа значения — новое определение и `deprecated` старого.
4. **Область применения наследуется** (ADR-004, I3) и может быть исключена у потомка через `excludes` (INV-19): например, тип-потомок `source` может исключить `isbn`, если он неприменим.
5. **Все записи `required: conditional`.** Обязательных для каждого объекта свойств ядра нет: обязательные свойства заданы встроенным реестром ([`04-properties.md`](04-properties.md), раздел 4). Условно обязательное требование одно — `attachment` у `image` (INV-24).
6. **Свойства ядра не объявляют отношения.** Связи «элемент → коллекция» и «глава → книга» выражаются отношениями `part-of-collection` и `chapter-of` ([`06-relations.md`](06-relations.md), раздел 3), а не свойствами-списками.
7. **Изменение `applies_to`** у принятого определения допустимо (данные не ломаются); сужение области оставляет значения у объектов вне области — такие значения помечаются правилом валидации фазы 2, автоматически не удаляются. В iter-006 так расширено `duration`: добавлен `book` для формата `audiobook`.
8. **Триггер — всегда `enum` или `list<enum>`.** Свойство другого `value_type` не может быть триггером развёртывания (INV-25): сопоставление правил работает по точному совпадению строки из `enum_values`. Триггер-ссылка на значение фасета в v1 не поддерживается ([`../adr/ADR-006-field-expansion.md`](../adr/ADR-006-field-expansion.md), А2).

## Связанные документы

- [`00-overview.md`](00-overview.md) — обзор метамодели и границы фазы 1.
- [`01-invariants.md`](01-invariants.md) — сводка INV-01…INV-27, универсальные инварианты.
- [`09-structural-invariants.md`](09-structural-invariants.md) — INV-21 (состав `value_type`), INV-23 (`media` → обёртка), INV-24 (обёртка `image`), INV-25…INV-27 (развёртывание полей).
- [`02-layers.md`](02-layers.md) — системный слой (определения свойств) и слой наполнения (значения).
- [`03-builtin-types.md`](03-builtin-types.md) — правило генерации `id`, встроенные метатипы.
- [`04-properties.md`](04-properties.md) — механика key / label, `value_type`, встроенные свойства, `deprecated`.
- [`05-core-types.md`](05-core-types.md) — типы ядра, роли `book`, обёртка `image`, коллекции.
- [`06-relations.md`](06-relations.md) — отношения ядра, каноническая ссылка, контракт для плагина.
- [`08-field-expansion.md`](08-field-expansion.md) — триггерные свойства и развёртывание полей, канонические примеры.
- [`../adr/ADR-005-core-extension-and-split.md`](../adr/ADR-005-core-extension-and-split.md) — `media`, обёртка, коллекции, свойства ядра.
- [`../adr/ADR-006-field-expansion.md`](../adr/ADR-006-field-expansion.md) — триггеры, `mode: union`, поведение при смене значения.
- [`../glossary/glossary.md`](../glossary/glossary.md) — термины `core property`, `media`, `image wrapper`, `attachment`, `trigger property`.
- [`../decisions/decision-log.md`](../decisions/decision-log.md) — DL-023, DL-024, DL-026…DL-028.
