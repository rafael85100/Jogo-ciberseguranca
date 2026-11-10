#!/usr/bin/env python3
"""Monta o APK corrigido: troca scripts .gdc por .gd, refaz o indice sparse PCK,
ajusta versionCode/versionName, reempacota com alinhamento de 4 bytes (ainda sem assinar)."""
import hashlib, os, struct, sys, zipfile

src_apk, patch_dir, out_apk, version = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])

zin = zipfile.ZipFile(src_apk)
files = {i.filename: zin.read(i.filename) for i in zin.infolist()}
infos = {i.filename: i for i in zin.infolist()}
order = [i.filename for i in zin.infolist()]

# 1) scripts corrigidos
replaced = []
for root, _, names in os.walk(patch_dir):
    for n in names:
        if not n.endswith('.gd'): continue
        rel = os.path.relpath(os.path.join(root, n), patch_dir)          # scripts/x/y.gd
        gdc, remap = 'assets/' + rel[:-3] + '.gdc', 'assets/' + rel + '.remap'
        new = 'assets/' + rel
        text = open(os.path.join(root, n), 'rb').read()
        if new in files:  # ja era texto (APK gerado por este script): so troca o conteudo
            files[new] = text; replaced.append(rel); continue
        assert gdc in files and remap in files, rel
        i = order.index(gdc)
        order[i] = new
        order.remove(remap)
        files[new] = text
        ref = infos[gdc]
        zi = zipfile.ZipInfo(new, date_time=ref.date_time); zi.compress_type = ref.compress_type
        zi.external_attr = ref.external_attr; infos[new] = zi
        for k in (gdc, remap): del files[k]
        replaced.append(rel)

# 2) indice sparse PCK
pck = files['assets/assets.sparsepck']
assert pck[:4] == b'GDPC'
dir_off = struct.unpack_from('<Q', pck, 32)[0]
head = pck[:dir_off]
p = dir_off; n = struct.unpack_from('<I', pck, p)[0]; p += 4
entries = []
for _ in range(n):
    l = struct.unpack_from('<I', pck, p)[0]; p += 4
    path = pck[p:p + l].rstrip(b'\0').decode(); p += l
    off, size = struct.unpack_from('<QQ', pck, p); p += 16
    md5 = pck[p:p + 16]; p += 16
    fl = struct.unpack_from('<I', pck, p)[0]; p += 4
    entries.append([path, off, size, md5, fl])
gone = {r[:-3] + '.gdc' for r in replaced} | {r + '.remap' for r in replaced} | set(replaced)
entries = [e for e in entries if e[0] not in gone]
for r in replaced:
    b = files['assets/' + r]
    entries.append([r, 0, len(b), hashlib.md5(b).digest(), 0])
for e in entries:  # confere tamanho e md5 de tudo que o indice aponta
    b = files['assets/' + e[0]]
    assert e[2] == len(b) and e[3] == hashlib.md5(b).digest(), e[0]
body = struct.pack('<I', len(entries))
for path, off, size, md5, fl in entries:
    pb = path.encode('utf-8'); pb += b'\0' * ((4 - len(pb) % 4) % 4)
    body += struct.pack('<I', len(pb)) + pb + struct.pack('<QQ', off, size) + md5 + struct.pack('<I', fl)
files['assets/assets.sparsepck'] = head + body

# 3) versao no AndroidManifest (binario AXML)
m = bytearray(files['AndroidManifest.xml'])
sc, _, fl, so, _ = struct.unpack_from('<IIIII', m, 16)
hs = struct.unpack_from('<H', m, 10)[0]
offs = struct.unpack_from('<%dI' % sc, m, 8 + hs)
def sget(i):
    o = 8 + so + offs[i]
    if fl & 0x100:
        o += 1 + (m[o] >> 7); ln = m[o]; o += 1
        return o, bytes(m[o:o + ln]).decode()
    ln = struct.unpack_from('<H', m, o)[0]; return o + 2, bytes(m[o + 2:o + 2 + 2 * ln]).decode('utf-16le')
strs = [sget(i)[1] for i in range(sc)]
q = struct.unpack_from('<I', m, 12)[0] + 8
uses = {}
while q < len(m):
    t, _, sz = struct.unpack_from('<HHI', m, q)
    if t == 0x0102:
        name = struct.unpack_from('<i', m, q + 20)[0]
        ac = struct.unpack_from('<H', m, q + 28)[0]
        for k in range(ac):
            a = q + 36 + k * 20
            an, araw = struct.unpack_from('<ii', m, a + 4)
            vt, vd = m[a + 15], struct.unpack_from('<I', m, a + 16)[0]
            if vt == 3: uses.setdefault(vd, []).append(strs[an])
            if strs[name] == 'manifest' and strs[an] == 'versionCode':
                struct.pack_into('<I', m, a + 16, version)
            if strs[name] == 'manifest' and strs[an] == 'versionName':
                vn_idx = vd
    q += sz
old = strs[vn_idx]; new_vn = '%d.0' % version
assert len(new_vn) == len(old) and uses[vn_idx] == ['versionName'], (old, uses.get(vn_idx))
o, _ = sget(vn_idx)
if fl & 0x100: m[o:o + len(old)] = new_vn.encode()
else: m[o:o + 2 * len(old)] = new_vn.encode('utf-16le')
files['AndroidManifest.xml'] = bytes(m)

# 4) zip alinhado (dados STORED em multiplo de 4; .so em 16 KiB se STORED)
with open(out_apk, 'wb') as fp:
    zout = zipfile.ZipFile(fp, 'w')
    for name in order:
        ref = infos[name]
        zi = zipfile.ZipInfo(name, date_time=ref.date_time)
        zi.compress_type = ref.compress_type; zi.external_attr = ref.external_attr
        zi.create_system = ref.create_system
        if zi.compress_type == zipfile.ZIP_STORED:
            align = 16384 if name.endswith('.so') else 4
            pos = fp.tell() + 30 + len(name.encode())
            pad = (align - (pos + 6) % align) % align
            zi.extra = struct.pack('<HHH', 0xD935, 2 + pad, align) + b'\0' * pad
        zout.writestr(zi, files[name])
    zout.close()
print('scripts trocados:', len(replaced)); print('indice:', len(entries), 'entradas'); print('versao:', old, '->', new_vn, '| versionCode ->', version)
