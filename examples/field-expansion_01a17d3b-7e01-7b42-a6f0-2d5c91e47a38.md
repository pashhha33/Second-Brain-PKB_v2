---
id: 01a17d3b-7e01-7b42-a6f0-2d5c91e47a38
type: field-expansion
defined_by: 01a17d3b-4a32-716d-82a6-503fe47a47a1
title: Профессия → специализация
aliases:
  - Профессия → специализация
  - occupation-specialization
applies_to_type:
  - person
trigger_property: occupation
trigger_values:
  - developer
  - designer
  - researcher
  - teacher
  - writer
adds_properties:
  - specialization
mode: union
layer: system
status: accepted
owner: human
---

# Профессия → специализация

Правило развёртывания полей — воспроизведение канонического примера [`08-field-expansion.md`](../docs/metamodel/08-field-expansion.md), раздел 2. `id` иллюстративный: у правил развёртывания `id` выдаётся при создании и реестром не фиксируется (DL-019, DL-029); `defined_by` — встроенный метатип `field-expansion` (запись 10 реестра метатипов).

Правило действует на тип `person` и его потомков, когда значение `occupation` пересекается с `trigger_values`; режим объединения в v1 единственный — `union` (INV-25, INV-26). Принадлежность `trigger_values` множеству `enum_values` свойства `occupation` проверяет правило `trigger-values-subset`; источник множества — определение свойства (запись 16 [`07-core-properties.md`](../docs/metamodel/07-core-properties.md)), которое в набор не входит.

Действие правила видно на экземпляре [`person_01a17d3b-6c02-7e1f-9b3d-4f6a8c0e2d57.md`](person_01a17d3b-6c02-7e1f-9b3d-4f6a8c0e2d57.md): поле `specialization` активно, значение не осиротевшее, предупреждение `inactive-field-value` не срабатывает (INV-27).
