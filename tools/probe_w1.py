import re, os, sys
src = open('tools/selfcheck_iter013.py', encoding='utf-8').read()
head = src.split("# ============================================================== A. схемы")[0]
head = head.replace('ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))', "ROOT = os.path.abspath('.')")
ns = {}
exec(head, ns)
text = ns['read'](os.path.join(ns['ROOT'], 'docs/validation/01-first-wave-rules.md'))
for i, b in enumerate(re.findall(r"```yaml\n(.*?)```", text, re.S)):
    obj = ns['parse_yaml'](b)
    if obj.get('type') != 'validation-rule':
        continue
    errs = ns['schema_errors'](obj, 'system-definitions.json')
    if errs:
        print(obj['rule_key'], '| applies_to =', repr(obj.get('applies_to')))
        branch = ns['schema_errors'](obj, 'system-definitions.json', 'validation-rule-object')
        print('   oneOf:', errs[:2])
        print('   ветвь validation-rule-object:', branch[:3])
