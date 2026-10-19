import json, sys
d = json.load(open(sys.argv[1])); target = sys.argv[2]; pat = sys.argv[3:]
src = [l for l in d['layouts'] if l['name'] == target] + [e for e in d['externalEvents'] if e['name'] == target]
def fmt(i): return ('NOT ' if i['type'].get('inverted') else '') + i['type']['value'] + '(' + ', '.join(i['parameters']) + ')'
def walk(evs, depth, path):
    for k, e in enumerate(evs):
        txt = json.dumps(e)
        if not any(p in txt for p in pat): continue
        conds = [fmt(c) for c in e.get('conditions', [])]; acts = [fmt(a) for a in e.get('actions', [])]
        if conds or acts:
            print('  ' * depth + f'[{path}{k}] SE ' + ' & '.join(conds))
            for a in acts: print('  ' * depth + '      -> ' + a)
        walk(e.get('events', []), depth + 1, f'{path}{k}.')
for s in src: walk(s['events'], 0, '')
