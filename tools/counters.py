import re, os
src = open('tools/selfcheck_iter013.py', encoding='utf-8').read()
head = src.split("# ============================================================== A. схемы")[0].replace(
    'ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))', "ROOT = os.path.abspath('.')")
mid = src.split("# ============================================================== A. схемы")[1].split("# ============================================================== B. правила")[0]
ns = {}
exec(head, ns)
exec("if True:\n" + "\n".join("    " + l for l in mid.splitlines()), ns)
NOTES = ns['NOTES']; PROPS = ns['PROPS']; RELS = ns['RELS']; TYPES = ns['TYPES']
props = sorted({k for n in NOTES for k in n['fm'] if k in PROPS})
rels = sorted({k for n in NOTES for k in n['fm'] if k in RELS})
types = sorted({n['fm']['type'] for n in NOTES})
media_vals = sum(len(v) if isinstance(v := n['fm'][k], list) else 1
                 for n in NOTES for k in ns['media_keys'](n['fm']['type']) if k in n['fm'])
links = sum(1 for n in NOTES for k, s, a, d in ns['links_of'](n['fm']) if not d)
vt = {PROPS[k]['value_type'] for k in props}
print('заметок:', len(NOTES))
print('типов экземпляров:', len(types), types)
print('свойств ядра:', len(props), props)
print('value_type свойств:', sorted(vt))
print('отношений:', len(rels), rels)
print('значений media/list<media>:', media_vals)
print('обёрток image:', sum(1 for n in NOTES if n['fm']['type'] == 'image'))
print('канонических ссылок:', links)
print('слоёв:', {n['fm']['layer'] for n in NOTES})
print('всего типов в реестре:', len([t for t in TYPES if TYPES[t]['layer'] == 'content']))
