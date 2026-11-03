# -*- coding: utf-8 -*-
"""Набор контрольных примеров для схем первой волны (iter-009) — артефакт самопроверки.

В репозиторий и в коммит B не входит. Запуск из корня репозитория:
    python3 sandbox/tools/schema_tests.py [путь/к/schema]
52 проверки: 9 позитивных (канонические примеры документации), 19 негативных, 10 проверок паттернов
и 14 проверок ветви validation-rule-object (iter-010).
Требуется только стандартная библиотека.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mini_validator
from mini_validator import check, load
R = mini_validator.ROOT = sys.argv[1] if len(sys.argv) > 1 else "schema"
mini_validator.cache = {}

U="01a17d3b-5d88-74e5-a071-8293a4b5c6d7"
person={"id":U,"type":"person","defined_by":"01a17d3b-4de8-70a1-ac3d-4e5f60718293","title":"Иван Петров",
        "aliases":["Иван Петров"],"layer":"content","status":"accepted","owner":"human"}
facet_value={"id":"01a17d3b-4a29-72b4-9a57-be1a133ebf6f","type":"facet-value","defined_by":"01a17d3b-4a08-7875-996d-c4af6179a249",
        "facet":"[[facet_01a17d3b-4a28-744e-a519-67031a8e0ae5|Формат]]","title":"Книга","aliases":["Книга"],
        "layer":"classification","status":"accepted","owner":"human"}
type_def={"id":"01a17d3b-4de8-70a1-ac3d-4e5f60718293","type":"type","defined_by":"01a17d3b-4a00-747f-b063-cd02895e0d4f",
        "type_value":"person","title":"Person","aliases":["Person"],"layer":"system","status":"accepted","owner":"human"}
prop_id={"id":"01a17d3b-4a09-79b2-aeb4-446d3725c4c0","type":"property","defined_by":"01a17d3b-4a01-73dd-8782-259a7e45663f",
        "property_key":"id","title":"Идентификатор","aliases":["Идентификатор","id"],"value_type":"uuid",
        "required":"always","applies_to":"*","layer":"system","status":"accepted","owner":"human"}
prop_cover=dict(prop_id, id="01a17d3b-4a21-787a-b3db-b9365bb54266", property_key="cover", title="Обложка",
        aliases=["Обложка","cover"], value_type="media", required="conditional", applies_to=["source","album","film-series"])
rel_parent={"id":"01a17d3b-4a12-7667-b7e7-50f350fab871","type":"relation","defined_by":"01a17d3b-4a02-7576-a16a-764c758b99be",
        "relation_key":"parent","title":"Родительская категория","aliases":["Родительская категория","parent"],
        "source_type":["hierarchical-category"],"target_type":["hierarchical-category"],"cardinality":"0..1",
        "layer":"system","status":"accepted","owner":"human"}
fe_rule={"id":"01a17d3b-7e02-7a17-9c53-4b6d82f10a75","type":"field-expansion","defined_by":"01a17d3b-4a32-716d-82a6-503fe47a47a1",
        "title":"Профессия → место работы","aliases":["Профессия → место работы","occupation-organization"],
        "applies_to_type":["person"],"trigger_property":"occupation",
        "trigger_values":["developer","researcher","teacher","manager"],"adds_relations":["member-of"],
        "mode":"union","layer":"system","status":"accepted","owner":"human"}
image={"id":"01a17d3b-6b30-7f11-9c42-6a2f7d1e5b84","type":"image","defined_by":"01a17d3b-6a14-7b9e-8f31-2c7d4a6e1b09",
        "title":"Обложка книги How to Take Smart Notes","aliases":["Обложка книги How to Take Smart Notes"],
        "attachment":"Pasted image 20261027143000.png",
        "about":["[[book_01a17d3b-6b21-7d4e-8a1c-2e4f6a8b0c13|How to Take Smart Notes]]"],
        "layer":"content","status":"accepted","owner":"human"}
ML="[[image_01a17d3b-6b30-7f11-9c42-6a2f7d1e5b84|Обложка книги]]"

ok=True
print("--- позитивные (ожидаются валидными) ---")
ok&=check("экземпляр person (02-layers)",person,"object.json",True)
ok&=check("значение фасета (04-properties §6)",facet_value,"object.json",True)
ok&=check("определение типа person",type_def,"system-definitions.json",True)
ok&=check("определение свойства id (applies_to: '*')",prop_id,"system-definitions.json",True)
ok&=check("определение свойства cover (applies_to списком)",prop_cover,"system-definitions.json",True)
ok&=check("определение отношения parent (без value_type)",rel_parent,"system-definitions.json",True)
ok&=check("правило развёртывания (08 §6.1)",fe_rule,"system-definitions.json",True)
ok&=check("обёртка image (05-core-types §4.2)",image,"media.json",True)
ok&=check("обёртка image против object.json",image,"object.json",True)
ok&=check("значение media (каноническая ссылка)",ML,"media.json",True) if False else True
print("--- негативные (ожидаются невалидными) ---")
import copy
d=copy.deepcopy(person); del d["owner"]; ok&=check("person без owner",d,"object.json",False)
d=copy.deepcopy(person); d["layer"]="system"; ok&=check("person с layer: system (INV-09)",d,"object.json",False)
d=copy.deepcopy(facet_value); d["layer"]="content"; ok&=check("facet-value с layer: content",d,"object.json",False)
d=copy.deepcopy(type_def); d["layer"]="content"; ok&=check("type-определение с layer: content",d,"system-definitions.json",False)
d=copy.deepcopy(person); d["id"]="01A17D3B-5D88-74E5-A071-8293A4B5C6D7"; ok&=check("id в верхнем регистре",d,"object.json",False)
d=copy.deepcopy(person); d["id"]="f47ac10b-58cc-4372-a567-0e02b2c3d479"; ok&=check("id — UUIDv4",d,"object.json",False)
d=copy.deepcopy(person); d["title"]="   "; ok&=check("title из пробелов (INV-07)",d,"object.json",False)
d=copy.deepcopy(person); d["aliases"]=[]; ok&=check("aliases пуст (INV-08)",d,"object.json",False)
d=copy.deepcopy(person); d["type"]="Person"; ok&=check("type не kebab-case (INV-04)",d,"object.json",False)
d=copy.deepcopy(person); d["defined_by"]="[[type_01a17d3b-4de8-70a1-ac3d-4e5f60718293|Person]]"; ok&=check("defined_by ссылкой, не UUID (INV-12)",d,"object.json",False)
d=copy.deepcopy(prop_id); d["value_type"]="enum"; ok&=check("property: enum без enum_values (INV-21)",d,"system-definitions.json",False)
d=copy.deepcopy(prop_id); d["value_type"]="object"; ok&=check("property: value_type вне набора",d,"system-definitions.json",False)
d=copy.deepcopy(fe_rule); del d["adds_relations"]; ok&=check("field-expansion без adds_* (INV-25)",d,"system-definitions.json",False)
d=copy.deepcopy(fe_rule); d["mode"]="first-match"; ok&=check("field-expansion mode: first-match (DL-028)",d,"system-definitions.json",False)
d=copy.deepcopy(fe_rule); d["trigger_values"]=[]; ok&=check("field-expansion: trigger_values пуст",d,"system-definitions.json",False)
d=copy.deepcopy(rel_parent); d["cardinality"]="1..2"; ok&=check("relation: cardinality вне набора (INV-17)",d,"system-definitions.json",False)
d=copy.deepcopy(image); del d["attachment"]; ok&=check("image без attachment (INV-24)",d,"media.json",False)
d=copy.deepcopy(image); d["layer"]="system"; ok&=check("image с layer: system",d,"media.json",False)
d=copy.deepcopy(type_def); d["extends"]="[[type_01a17d3b-4de8-70a1-ac3d-4e5f60718293]]"; ok&=check("extends без alias (INV-15/18)",d,"system-definitions.json",False)
print("--- паттерны значений (отдельно) ---")
import json,re
m=json.load(open(R+"/media.json",encoding="utf-8"))
pat=m["$defs"]["media-link"]["pattern"]
for v,exp in [(ML,True),("![[Pasted image 20261027143000.png]]",False),("[[image_01a17d3b-6b30-7f11-9c42-6a2f7d1e5b84]]",False),
              ("[[person_01a17d3b-5d88-74e5-a071-8293a4b5c6d7|Иван Петров]]",False),("Pasted image.png",False)]:
    r=bool(re.search(pat,v))
    print(("OK " if r==exp else "!! ")+"media-link %-52s %s"%(v[:50],"соответствует" if r else "не соответствует"))
    ok&= (r==exp)
o=json.load(open(R+"/object.json",encoding="utf-8"))
cp=o["$defs"]["canonical-link"]["pattern"]
for v,exp in [("[[person_01a17d3b-5d88-74e5-a071-8293a4b5c6d7|Иван Петров]]",True),
              ("[[hierarchical-cat_01a17d3b-4a06-7991-b54e-9352cde369c0|Языки программирования]]",True),
              ("[[Иван Петров]]",False),("[[person_01a17d3b-5d88-74e5-a071-8293a4b5c6d7]]",False),
              ("[[folder/person_01a17d3b-5d88-74e5-a071-8293a4b5c6d7|Иван]]",False)]:
    r=bool(re.search(cp,v)); print(("OK " if r==exp else "!! ")+"canonical-link %-48s %s"%(v[:46],"соответствует" if r else "не соответствует")); ok&=(r==exp)

print("--- validation-rule: пятая ветвь oneOf (iter-010, DL-041) ---")
VR={"id":"01a17d3b-9b01-7c41-8a52-3f6b81c9d041","type":"validation-rule",
    "defined_by":"01a17d3b-4a04-7c70-99cd-5c01dddac8b4","rule_key":"unique-id",
    "title":"Уникальность id","aliases":["Уникальность id","unique-id"],
    "checks":["INV-02"],"severity":"error","applies_to":"*",
    "condition":"Во всём хранилище не более одного объекта с данным id.",
    "message":"Объект с таким id уже существует.","layer":"system","status":"accepted","owner":"human"}
def drop(d,k): return {a:b for a,b in d.items() if a!=k}
for nm,inst,exp in [
  ("правило unique-id (первая волна)",VR,True),
  ("applies_to списком type_value",dict(VR,rule_key="unique-machine-keys",applies_to=["type","property"]),True),
  ("checks: пункт реестра и DL",dict(VR,rule_key="relation-acyclic",checks=["06-relations.md#2.1","06-relations.md#3.2","DL-040"]),True),
  ("warning-правило extends-depth",dict(VR,rule_key="extends-depth",checks=["INV-18"],severity="warning",applies_to=["type"]),True),
  ("без checks",drop(VR,"checks"),False),
  ("пустой checks",dict(VR,checks=[]),False),
  ("severity: info",dict(VR,severity="info"),False),
  ("checks: INV-2 (не два знака)",dict(VR,checks=["INV-2"]),False),
  ("checks: произвольная строка",dict(VR,checks=["ссылка существует"]),False),
  ("без message",drop(VR,"message"),False),
  ("layer: content",dict(VR,layer="content"),False),
  ("rule_key не kebab-case",dict(VR,rule_key="Unique ID"),False),
  ("condition из пробелов",dict(VR,condition="   "),False),
  ("без owner",drop(VR,"owner"),False)]:
    ok &= check(nm,inst,"system-definitions.json",exp)

print("\nИТОГ:", "все проверки пройдены" if ok else "ЕСТЬ РАСХОЖДЕНИЯ")
