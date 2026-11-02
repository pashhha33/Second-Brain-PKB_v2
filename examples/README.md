# Примеры — эталонные заметки (фаза 3)

Каталог `examples/` — первый набор эталонных заметок (fixtures), на которых пять схем `schema/` и четырнадцать правил валидации фазы 2 проверяются на данных, а не на фрагментах документов. Каталог создан в iter-012 (DL-046, DL-047); это не хранилище владельца, не источник определений для плагина и не набор негативных примеров.

## Назначение

- **Вход для проверок.** До появления исполняемого валидатора (фазы 4–5) схемы и правила проверяются на документах метамодели; набор даёт полный объект целиком — frontmatter и имя файла, поэтому проверяются и те правила, которым нужно имя файла или другой объект.
- **Каноническая форма по классам объектов.** Показаны семь классов: определение типа, определение свойства, правило развёртывания полей, фасет, значение фасета, экземпляр типа слоя наполнения, обёртка изображения и коллекция.
- **Форма значения на данных.** Видно различие одиночной ссылки (кратность `0..1`, `1..1`) и списка YAML (кратность `0..*`), а также формы по `value_type`: `string`, `date`, `number`, `enum`, `list<enum>`, `list<string>`, `link`, `list<link>`, `uuid`, `media`, `list<media>`.
- **Образец для ручного создания объектов.** До bootstrap объекты создаются вручную по реестрам; заметки набора — образец состава ключей и порядка записи.

Границы набора: он **не замкнут** — объекты bootstrap (десять встроенных метатипов, определения типов ядра, свойств и отношений) в него не входят и перечислены в разделе «Объекты вне набора». Негативные примеры в iter-012 не создавались (вне scope, TASK.md iter-012).

## Состав набора

Тринадцать заметок. Правила `unique-id`, `filename-matches-object` и `aliases-first-equals-title` положительным примером служит каждый файл набора, поэтому в последнем столбце перечислены только правила, для которых файл значим отдельно.

| Файл | `type` | Слой | Схемы | Значимые `rule_key` |
|---|---|---|---|---|
| [`type_01a17d3b-6a0f-7b2c-8d4e-1a3c5e7f9b20.md`](type_01a17d3b-6a0f-7b2c-8d4e-1a3c5e7f9b20.md) | `type` | `system` | `object.json`, `system-definitions.json` (ветвь `type-definition`) | `unique-machine-keys` (`type_value`), `extends-acyclic`, `extends-depth` |
| [`property_01a17d3b-4a21-787a-b3db-b9365bb54266.md`](property_01a17d3b-4a21-787a-b3db-b9365bb54266.md) | `property` | `system` | `object.json`, `system-definitions.json` (ветвь `property-definition`) | `unique-machine-keys` (`property_key`) |
| [`field-expansion_01a17d3b-7e01-7b42-a6f0-2d5c91e47a38.md`](field-expansion_01a17d3b-7e01-7b42-a6f0-2d5c91e47a38.md) | `field-expansion` | `system` | `object.json`, `system-definitions.json` (ветвь `field-expansion-rule`) | `trigger-values-subset`, `inactive-field-value` |
| [`facet_01a17d3b-6d01-7a13-9f42-3c8d51a70e64.md`](facet_01a17d3b-6d01-7a13-9f42-3c8d51a70e64.md) | `facet` | `classification` | `object.json` | `link-target-exists` (цель ключа `facet`) |
| [`facet-value_01a17d3b-6d02-7b27-8e19-5f2a74c93b18.md`](facet-value_01a17d3b-6d02-7b27-8e19-5f2a74c93b18.md) | `facet-value` | `classification` | `object.json`, `facet-value.json` | `link-target-exists` (ключ `facet`) |
| [`note_01a17d3b-6b10-7d52-9a34-1e7c42b8f056.md`](note_01a17d3b-6b10-7d52-9a34-1e7c42b8f056.md) | `note` | `content` | `object.json`, `core-property-values.json` | `defined-by-consistent`, `link-target-exists`, `media-target-is-image` |
| [`book_01a17d3b-6b21-7d4e-8a1c-2e4f6a8b0c13.md`](book_01a17d3b-6b21-7d4e-8a1c-2e4f6a8b0c13.md) | `book` | `content` | `object.json`, `core-property-values.json` | `media-target-is-image`, `link-target-exists`, `inactive-field-value` |
| [`person_01a17d3b-6c02-7e1f-9b3d-4f6a8c0e2d57.md`](person_01a17d3b-6c02-7e1f-9b3d-4f6a8c0e2d57.md) | `person` | `content` | `object.json`, `core-property-values.json` | `inactive-field-value` (развёрнутое поле активно) |
| [`chapter_01a17d3b-6b22-7e63-8b41-2f9d53c7a168.md`](chapter_01a17d3b-6b22-7e63-8b41-2f9d53c7a168.md) | `chapter` | `content` | `object.json`, `core-property-values.json` | `link-target-exists` (одиночная ссылка `1..1`) |
| [`image_01a17d3b-6b30-7f11-9c42-6a2f7d1e5b84.md`](image_01a17d3b-6b30-7f11-9c42-6a2f7d1e5b84.md) | `image` | `content` | `object.json`, `media.json`, `core-property-values.json` | `image-has-attachment`, `media-target-is-image` (цель `cover`) |
| [`image_01a17d3b-6b31-7a52-8d17-3f9c2b7e6a41.md`](image_01a17d3b-6b31-7a52-8d17-3f9c2b7e6a41.md) | `image` | `content` | `object.json`, `media.json`, `core-property-values.json` | `image-has-attachment`, `media-target-is-image` (цель `artwork`) |
| [`image_01a17d3b-6b32-7c68-9e24-5a1d8f3b7c92.md`](image_01a17d3b-6b32-7c68-9e24-5a1d8f3b7c92.md) | `image` | `content` | `object.json`, `media.json`, `core-property-values.json` | `image-has-attachment` |
| [`gallery_01a17d3b-6b40-7f28-9c53-6a1e84d92f37.md`](gallery_01a17d3b-6b40-7f28-9c53-6a1e84d92f37.md) | `gallery` | `content` | `object.json` | `link-target-exists` (цель `part-of-collection`) |

Пустой служебный файл `.gitkeep` сохранён: удаление файлов репозитория вне scope итерации (вопрос — REPORT.md iter-012).

## Покрытие правил валидации

Четырнадцать правил первой и второй волн ([`../docs/validation/00-validation-rules.md`](../docs/validation/00-validation-rules.md), разделы 5–6). Третья волна (19 кандидатов) в iter-012 не реализовывалась.

| № | `rule_key` | `severity` | Покрытие в наборе |
|---|---|---|---|
| 1 | `unique-id` | `error` | полное: 13 `id` различны, все — UUIDv7 канонической формы |
| 2 | `filename-matches-object` | `error` | полное: имя каждого файла равно `{{type_prefix}}_{{id}}.md` |
| 3 | `aliases-first-equals-title` | `error` | полное: во всех 13 файлах `aliases[0]` равен `title` |
| 4 | `media-target-is-image` | `error` | полное: четыре значения `media` / `list<media>` (`cover` книги, `artwork` книги и заметки) указывают на объекты `type: image` |
| 5 | `image-has-attachment` | `error` | полное: три обёртки `image` имеют непустой `attachment` |
| 6 | `extends-acyclic` | `error` | формальное: единственное определение типа в наборе (`note`) корневое, `extends` отсутствует; цепочка `source → book` вне набора |
| 7 | `defined-by-consistent` | `error` | частичное: пара «заметка → определение `note`» проверяется внутри набора (цель `type: type`, `type_value` равен `type` экземпляра); у остальных 12 объектов цель `defined_by` — объект bootstrap |
| 8 | `trigger-values-subset` | `error` | частичное: `trigger_values` правила ⊆ `enum_values` свойства `occupation` по реестру ([`../docs/metamodel/07-core-properties.md`](../docs/metamodel/07-core-properties.md), запись 16), но объект-определение свойства в набор не входит |
| 9 | `link-target-exists` | `error` | полное: все 15 канонических ссылок frontmatter разрешаются внутри набора; `defined_by` правилом не охватывается (INV-15, исключение) |
| 10 | `unique-machine-keys` | `error` | формальное: дублей `type_value` и `property_key` в наборе нет; полная проверка требует всего хранилища (29 типов ядра, 23 свойства, 18 отношений) |
| 11 | `relation-acyclic` | `error` | не покрыто: отношений `parent`, `part-of` и `blocks` в наборе нет |
| 12 | `inactive-field-value` | `warning` | положительное: поле `specialization` персоны активно правилом развёртывания из набора, осиротевших значений нет; срабатывание правила показано не было бы и на негативном примере — он вне scope |
| 13 | `extends-depth` | `warning` | не покрыто: цепочек `extends` в наборе нет, глубина равна нулю |
| 14 | `deprecated-link-target` | `warning` | не покрыто: все объекты набора в `status: accepted` |

Итого: семь правил имеют полный или положительный пример в наборе (1–5, 9, 12), два — частичный (7, 8), два — формальный (6, 10), три не покрыты данными (11, 13, 14).

## Соглашения

### Идентификаторы

- **Реестровые `id`** (фиксированы и защищены от пересмотра) в наборе использованы там, где объект воспроизводит реестр: определение свойства `cover` (`01a17d3b-4a21-…`, канонический пример [`../docs/metamodel/07-core-properties.md`](../docs/metamodel/07-core-properties.md), раздел 4) и `defined_by` пяти объектов, указывающий на встроенные метатипы (`01a17d3b-4a00-…`, `4a01-…`, `4a07-…`, `4a08-…`, `4a32-…`).
- **Иллюстративные `id`** ([`../docs/metamodel/03-builtin-types.md`](../docs/metamodel/03-builtin-types.md), правило об иллюстративных значениях) — у объектов, чей `id` реестром не фиксируется: определения типов ядра (DL-019) и правила развёртывания (DL-029). Там, где принятая документация уже приводила `id` той же сущности, он переиспользован дословно: определения `note` и `image`, книга, персона, обложка, две иллюстрации книги и правило «Профессия → специализация».
- **Новые сущности набора** (заметка, глава, галерея, фасет «Статус проработки» и его значение, а также определения типов `person`, `chapter`, `gallery` в таблице ниже) получили иллюстративные `id` того же формата — UUIDv7, блок `01a17d3b-6…`; все значения различны и не совпадают ни с одним реестровым `id`.
- Реестровые и иллюстративные `id` не смешиваются: объект, чей `id` зафиксирован реестром, встречается в наборе один раз и только с реестровым значением.

### Имена файлов и ссылки

Имя файла — `{{type_prefix}}_{{id}}.md` (INV-05, INV-06): `type_prefix` равен `type_value` для типов слоя наполнения и имени метатипа для системного слоя, обрезка до 16 символов в наборе не требуется (`field-expansion` — 15 символов, `facet-value` — 11). Значения свойств и отношений — канонические ссылки `[[{{type_prefix}}_{{id}}|{{title}}]]` (INV-15), alias ссылки равен `title` цели. `defined_by` — единственное исключение: «сырой» UUIDv7 без ссылки.

### `attachment`

Значение — строка, как её записывает Obsidian: имя файла или путь относительно корня хранилища ([`../schema/media.json`](../schema/media.json), `$defs/image-wrapper`; [`../docs/metamodel/07-core-properties.md`](../docs/metamodel/07-core-properties.md), запись 13). В наборе использованы обе формы: у книги — имя файла (как в примере реестра, раздел 2), у трёх обёрток `image` — путь `attachments/{{имя}}.png`. Сами файлы вложений в `examples/` не создаются: значения иллюстративные, существование файла по пути `attachment` инвариантом не проверяется (INV-24), а проверка — кандидат третьей волны.

### Оформление заметки

Заметка начинается с YAML frontmatter между двумя строками `---`, за ним следует H1, равный `title`, и 1–3 абзаца о том, что файл демонстрирует (R-002 соблюдён в части H1 и вводного текста; первое место в файле занимает frontmatter — иначе объект не существует по INV-01…INV-12). Значения списков записаны в блочной форме YAML, строки со специальным символом (`:`, `[[`) — в двойных кавычках. Документация на русском, идентификаторы — английский kebab-case (DL-001).

## Объекты вне набора

Объекты bootstrap, на которые указывают `defined_by` и ключи frontmatter набора. Их `id` приведены, чтобы ссылку можно было разрешить при проверке вне набора; файлы не создавались (вне scope iter-012).

| `id` | Объект | Указывает |
|---|---|---|
| `01a17d3b-4a00-747f-b063-cd02895e0d4f` | встроенный метатип `type` (запись 1) | `defined_by` определения типа `note` |
| `01a17d3b-4a01-73dd-8782-259a7e45663f` | встроенный метатип `property` (запись 2) | `defined_by` определения свойства `cover` |
| `01a17d3b-4a07-7494-b6d9-328c7108a3c0` | встроенный метатип `facet` (запись 8) | `defined_by` фасета |
| `01a17d3b-4a08-7875-996d-c4af6179a249` | встроенный метатип `facet-value` (запись 9) | `defined_by` значения фасета |
| `01a17d3b-4a32-716d-82a6-503fe47a47a1` | встроенный метатип `field-expansion` (запись 10) | `defined_by` правила развёртывания |
| `01a17d3b-6a11-7c4d-9e2a-3b5c7d9e1f31` | определение типа `book` | `defined_by` книги |
| `01a17d3b-6a12-7d31-8c42-6e5a93f27b14` | определение типа `person` | `defined_by` персоны |
| `01a17d3b-6a14-7b9e-8f31-2c7d4a6e1b09` | определение типа `image` | `defined_by` трёх обёрток изображения |
| `01a17d3b-6a15-7f24-8b17-3c9d52e61f48` | определение типа `chapter` | `defined_by` главы |
| `01a17d3b-6a16-7a38-9d26-5e1b74f83c29` | определение типа `gallery` | `defined_by` галереи |
| реестровые `id` ([`../docs/metamodel/07-core-properties.md`](../docs/metamodel/07-core-properties.md), раздел 1) | определения свойств `artwork`, `isbn`, `published`, `attachment`, `position`, `page`, `occupation`, `format`, `creation-method`, `specialization` | ключи frontmatter экземпляров; `trigger_property` и `adds_properties` правила развёртывания |
| реестровые `id` ([`../docs/metamodel/06-relations.md`](../docs/metamodel/06-relations.md), разделы 2–3) | определения отношений `about`, `author`, `derived-from`, `references`, `chapter-of`, `part-of-collection`, `object-facet-value` | ключи frontmatter экземпляров |
| реестрового `id` не имеет | определение ключа `facet` ([`../docs/metamodel/04-properties.md`](../docs/metamodel/04-properties.md), раздел 6) | ключ `facet` значения фасета; `id` выдаётся при создании |

Метатипы 3–7 (`relation`, `automation`, `validation-rule`, `domain`, `hierarchical-category`) в наборе не задействованы; определения типов `source`, `file`, `concept`, `organization` не задействованы, хотя на них указывают `extends` определений `book`, `image`, `chapter` и значение `about` из примера документации.

## Что намеренно не покрыто

- **Две ветви `system-definitions.json`**: `relation-definition` и `validation-rule-object`. Определения отношений и объекты правил валидации создаются bootstrap-ом; их канонические примеры — [`../docs/metamodel/06-relations.md`](../docs/metamodel/06-relations.md), раздел 2, и [`../docs/validation/01-first-wave-rules.md`](../docs/validation/01-first-wave-rules.md), [`../docs/validation/02-second-wave-rules.md`](../docs/validation/02-second-wave-rules.md). Ветвь `automation` схемой не описана.
- **Три правила без данных** (`relation-acyclic`, `extends-depth`, `deprecated-link-target`) и три правила с формальным или частичным покрытием (`extends-acyclic`, `unique-machine-keys`, `trigger-values-subset`) — см. таблицу «Покрытие правил валидации».
- **Срабатывание `inactive-field-value`**: осиротевших значений в наборе нет, а негативные примеры в iter-012 не создавались.
- **Два ключа частичной схемы `core-property-values.json`**: `photo` (область применения — `person`, `place`, `organization`; форма `media` покрыта ключом `cover`) и `poster` (`film`, `video`, `film-series` — таких типов в наборе нет). Остальные десять ключей схемы в наборе присутствуют.
- **Формы значений `text`, `boolean`, `datetime`**: свойств ядра с такими `value_type` нет (`text` — только `prompt`, `boolean` и `datetime` в реестре не используются); `$defs` этих форм проверены на примерах в iter-011.
- **Слой классификации частично**: домены, иерархические категории и отношения `object-category`, `parent`, `category-domain` не представлены — из состава слоя показаны фасет и его значение.
- **Состав ядра частично**: восемь типов из 29 (`note`, `book`, `person`, `chapter`, `image`, `gallery` — экземпляры, `type`, `property`, `field-expansion` — определения), десять свойств ядра из 23 и семь отношений из 18.
- **Роли `book`**: показаны две из трёх («карточка + файл», «агрегатор глав»); роль «карточка» без `attachment` отдельным объектом не представлена.
- **Правила развёртывания `format` и `creation-method`** (канонические примеры [`../docs/metamodel/08-field-expansion.md`](../docs/metamodel/08-field-expansion.md), разделы 6.2 и 6.3) в набор не вошли, поэтому поля `url`, `duration`, `narrator`, `model`, `prompt`, `seed` в экземплярах не заполнены; правила трёх триггеров в наборе одно.
- **Исполняемый валидатор, CI и код плагина**: проверки набора выполнены скриптом песочницы `tools/selfcheck_iter012.py`, который в репозиторий не входит (каталог `tools/` в `.gitignore`); результаты — [`../docs/_workflow/iterations/iter-012/REPORT.md`](../docs/_workflow/iterations/iter-012/REPORT.md).

## Связанные документы

- [`../docs/PROJECT_BRIEF.md`](../docs/PROJECT_BRIEF.md) — фазы проекта и критерии успеха.
- [`../docs/project-map/PROJECT_MAP.md`](../docs/project-map/PROJECT_MAP.md) — карта проекта, статус фазы 3.
- [`../docs/metamodel/00-overview.md`](../docs/metamodel/00-overview.md) — обзор метамодели и границы фаз.
- [`../docs/validation/00-validation-rules.md`](../docs/validation/00-validation-rules.md) — реестр правил валидации, 14 правил и 19 кандидатов третьей волны.
- [`../schema/object.json`](../schema/object.json) — схемы: `object.json`, `system-definitions.json`, `media.json`, `facet-value.json`, `core-property-values.json`.
- [`../docs/decisions/decision-log.md`](../docs/decisions/decision-log.md) — DL-046 (состав первого набора), DL-047 (соглашения набора).
- [`../docs/glossary/glossary.md`](../docs/glossary/glossary.md) — термины Example note и Fixture.
