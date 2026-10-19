"""Converte os sprites/cenarios do jogo para pixel art. Le do backup, grava no projeto."""
import json, os, sys, statistics
sys.path.insert(0, os.path.dirname(__file__))
from pixelate import process_group
from PIL import Image
SRC, DST, SCALES, OUTLIST = sys.argv[1:5]
P = 3  # pixels de tela por pixel de arte
OUT = (18, 14, 28, 255)
d = json.load(open(os.path.join(SRC, 'game.json')))
scales = json.load(open(SCALES))
res = {r['name']: r['file'] for r in d['resources']['resources'] if r['kind'] == 'image'}
def obj_files(names):
    fs = []
    objs = d.get('objects', []) + [o for l in d['layouts'] for o in l['objects']]
    for o in objs:
        if o['name'] not in names: continue
        if o['type'] == 'Sprite':
            for a in o.get('animations', []):
                for dr in a['directions']:
                    for sp in dr['sprites']:
                        if sp['image'] in res: fs.append(res[sp['image']])
        elif o.get('texture') in res: fs.append(res[o['texture']])
    return list(dict.fromkeys(fs))
CHAR = dict(colors=24, outline=OUT, gamma=0.72, con=1.0)
BG = dict(colors=40, outline=None, sat=1.12, con=1.0, gamma=0.72)
groups = [
    ('player',    obj_files({'Player', 'Player2'}), dict(CHAR, gamma=0.6, sat=1.25)),
    ('lagarto',   obj_files({'lagarto_boss1', 'lagarto_boss2'}), CHAR),
    ('lagarto_s', obj_files({'lagarto_boss3', 'lagarto_boss4'}), CHAR),
    ('boss_x',    obj_files({'boss_x'}), CHAR),
    ('monstro',   obj_files({'monstro_alado', 'monstro_alado2'}), CHAR),
    ('portal',    obj_files({'portal', 'portal2', 'portal3', 'portalF'}), CHAR),
    ('robo_z',    obj_files({'robo_z', 'robo_z2', 'robo_z3', 'robo_z4', 'robo_z5', 'robo_z6', 'robo_z7'}),
                  dict(colors=32, outline=OUT, sat=1.0, con=1.0, athr=70, src_palette=True, scale='max', resample=Image.Resampling.NEAREST)),
    ('robo_a',    obj_files({'robo_a', 'robo_a2', 'robo_a3'}),
                  dict(colors=32, outline=OUT, sat=1.0, con=1.0, athr=70, src_palette=True, scale='max', resample=Image.Resampling.NEAREST)),
    ('drone1',    obj_files({'drone1'}), dict(colors=20, outline=OUT, gamma=0.85)),
    ('drone2',    ['34.png'], dict(colors=20, outline=OUT, gamma=0.85)),
    ('upvida',    obj_files({'upvida'}), dict(colors=16, outline=OUT, gamma=0.85)),
] + [(f'arvore_{f}', [f], dict(colors=16, outline=OUT, gamma=0.85, scale='max')) for f in ['01.png', '05.png', '17.png', '19.png']] + [
    ('predio_p5', ['p5.png'], dict(colors=32, outline=OUT, gamma=0.78, scale='max')),
    ('predio_p6', ['p6.png'], dict(colors=32, outline=OUT, gamma=0.78, scale='max')),
    ('piso',      ['tilenovo.png'], dict(colors=20, outline=None, gamma=0.78)),
    ('barra',     ['assets/image/metade barra.png'], dict(colors=20, outline=None, gamma=0.78)),
] + [(f'bg_{f}', [f], BG) for f in ['bg_ad_game.png', 'bg_1.png', 'lab_exeterno.png', 'finalbg.png',
                                     'assets/image/ChatGPT Image 17 de jun. de 2026, 11_31_27.png']]
done = set(); log = []
for name, files, kw in groups:
    files = [f for f in files if f not in done and os.path.exists(os.path.join(SRC, f))]
    if not files: print('VAZIO', name); continue
    agg = max if kw.pop('scale', 'median') == 'max' else statistics.median
    sx = agg([s[0] for f in files for s in scales.get(f, [])] or [1.0])
    sy = agg([s[1] for f in files for s in scales.get(f, [])] or [1.0])
    bx, by = max(1.0, P / sx), max(1.0, P / sy)
    bx = round(bx) if abs(bx - round(bx)) < 0.15 else round(bx, 2)
    by = round(by) if abs(by - round(by)) < 0.15 else round(by, 2)
    process_group([(os.path.join(SRC, f), os.path.join(DST, f)) for f in files], bx, by, **kw)
    done.update(files)
    print(f'{name:14s} {len(files):3d} arquivos  bloco {bx}x{by}')
json.dump(sorted(done), open(OUTLIST, 'w'), ensure_ascii=False, indent=0)
