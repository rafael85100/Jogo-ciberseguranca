#!/usr/bin/env python3
"""Troca ou acrescenta arquivos no APK (texturas .ctex e .import, cenas .scn, JSON de dados etc.),
atualiza tamanho e md5 no indice assets.sparsepck (arquivos novos ganham entrada nova) e a versao
do manifest. Nao assina.

Uso: build_assets.py base.apk pasta_patch/ saida.apk versionCode
pasta_patch/ espelha os caminhos do APK, ex.: pasta_patch/assets/.godot/imported/p5.png-....ctex
"""
import hashlib, os, struct, sys, zipfile

src_apk, patch_dir, out_apk, version = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
zin = zipfile.ZipFile(src_apk)
infos = {i.filename: i for i in zin.infolist()}
order = [i.filename for i in zin.infolist()]
files = {n: zin.read(n) for n in order}

# 1) troca de arquivos; caminhos que nao existem entram no fim do zip
changed, added = [], []
ref_info = infos['assets/assets.sparsepck']
for root, _, names in sorted(os.walk(patch_dir)):
    for n in sorted(names):
        rel = os.path.relpath(os.path.join(root, n), patch_dir).replace(os.sep, '/')
        if rel not in files:
            zi = zipfile.ZipInfo(rel, date_time=ref_info.date_time)
            # .ctex vai sem compressao, como os outros do APK; o resto com deflate
            zi.compress_type = zipfile.ZIP_STORED if rel.endswith('.ctex') else zipfile.ZIP_DEFLATED
            zi.external_attr = ref_info.external_attr; zi.create_system = ref_info.create_system
            infos[rel] = zi; order.append(rel); added.append(rel)
        files[rel] = open(os.path.join(root, n), 'rb').read()
        changed.append(rel)

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
idx = {e[0]: e for e in entries}
for rel in changed:
    if rel == 'assets/assets.sparsepck' or not rel.startswith('assets/'):
        continue
    e = idx.get(rel[len('assets/'):])
    if e is None:
        assert rel in added, 'fora do indice: ' + rel
        e = [rel[len('assets/'):], 0, 0, b'', 0]; entries.append(e); idx[e[0]] = e
    b = files[rel]; e[2] = len(b); e[3] = hashlib.md5(b).digest()
for e in entries:
    b = files['assets/' + e[0]]
    assert e[2] == len(b) and e[3] == hashlib.md5(b).digest(), e[0]
body = struct.pack('<I', len(entries))
for path, off, size, md5, fl in entries:
    pb = path.encode('utf-8'); pb += b'\0' * ((4 - len(pb) % 4) % 4)
    body += struct.pack('<I', len(pb)) + pb + struct.pack('<QQ', off, size) + md5 + struct.pack('<I', fl)
files['assets/assets.sparsepck'] = head + body

# 3) versao no AndroidManifest (binario AXML)
def set_version(m, version):
    m = bytearray(m)
    cs = 8                                   # chunk da tabela de strings logo apos o cabecalho do arquivo
    ctype, hsz, csize, sc, stc, fl, sstart, ststart = struct.unpack_from('<HHIIIIII', m, cs)
    assert ctype == 0x0001 and stc == 0, 'tabela de strings inesperada'
    offs = list(struct.unpack_from('<%dI' % sc, m, cs + hsz))
    def sget(i):
        o = cs + sstart + offs[i]
        if fl & 0x100:
            o += 1 + (m[o] >> 7); ln = m[o]; o += 1
            return bytes(m[o:o + ln]).decode()
        ln = struct.unpack_from('<H', m, o)[0]; return bytes(m[o + 2:o + 2 + 2 * ln]).decode('utf-16le')
    strs = [sget(i) for i in range(sc)]
    # acha os atributos versionCode/versionName da tag <manifest>
    q = cs + csize; vc_pos = vn_pos = None
    while q < len(m):
        t, _, sz = struct.unpack_from('<HHI', m, q)
        if t == 0x0102:
            name = struct.unpack_from('<i', m, q + 20)[0]
            ac = struct.unpack_from('<H', m, q + 28)[0]
            for k in range(ac):
                a = q + 36 + k * 20
                an = struct.unpack_from('<i', m, a + 4)[0]
                if strs[name] == 'manifest' and strs[an] == 'versionCode': vc_pos = a
                if strs[name] == 'manifest' and strs[an] == 'versionName': vn_pos = a
        q += sz
    assert vc_pos and vn_pos
    struct.pack_into('<I', m, vc_pos + 16, version)
    old = strs[struct.unpack_from('<I', m, vn_pos + 16)[0]]
    new_vn = '%d.0' % version
    if new_vn in strs:
        idx = strs.index(new_vn)
    else:                                    # acrescenta a string nova no fim da tabela
        data = bytes(m[cs + sstart: cs + csize])
        if fl & 0x100:
            b = new_vn.encode(); enc = bytes([len(new_vn), len(b)]) + b + b'\0'
        else:
            enc = struct.pack('<H', len(new_vn)) + new_vn.encode('utf-16le') + b'\0\0'
        new_off = len(data); data += enc; data += b'\0' * ((4 - len(data) % 4) % 4)
        offs.append(new_off); idx = sc
        nsc = sc + 1; nsstart = hsz + 4 * nsc
        chunk = struct.pack('<HHIIIIII', ctype, hsz, nsstart + len(data), nsc, 0, fl, nsstart, 0)
        chunk += struct.pack('<%dI' % nsc, *offs) + data
        delta = len(chunk) - csize
        m = m[:cs] + chunk + m[cs + csize:]
        struct.pack_into('<I', m, 4, len(m))
        vn_pos += delta
    struct.pack_into('<i', m, vn_pos + 8, idx)       # rawValue
    struct.pack_into('<I', m, vn_pos + 16, idx)      # typedValue.data
    return bytes(m), old, new_vn
files['AndroidManifest.xml'], old, new_vn = set_version(files['AndroidManifest.xml'], version)

# 4) zip alinhado
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
print('arquivos trocados:', len(changed) - len(added), '| novos:', len(added)); print('indice:', len(entries), 'entradas'); print('versao:', old, '->', new_vn, '| versionCode ->', version)
