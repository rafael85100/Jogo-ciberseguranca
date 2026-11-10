#!/usr/bin/env python3
"""Decodifica GDScript tokenizado (Godot 4, GDSC v101) de volta para texto."""
import struct, subprocess, sys

TOK = """EMPTY ANNOTATION IDENTIFIER LITERAL < <= > >= == != and or not && || ! & | ~ ^ << >> + - * ** / % = += -= *= **= /= %= <<= >>= &= |= ^=
if elif else for while break continue pass return match when as assert await breakpoint class class_name const enum extends func in is namespace preload self signal static super trait var void yield
[ ] { } ( ) , ; . .. ... : $ -> _ NEWLINE INDENT DEDENT PI TAU INF NAN VCS ` ? ERROR EOF""".split()


def read_variant(d, p):
    h = struct.unpack_from('<I', d, p)[0]; p += 4
    t, f64 = h & 0xFFFF, h & (1 << 16)
    if t == 0: return None, p
    if t == 1: return bool(struct.unpack_from('<I', d, p)[0]), p + 4
    if t == 2:
        if f64: return struct.unpack_from('<q', d, p)[0], p + 8
        return struct.unpack_from('<i', d, p)[0], p + 4
    if t == 3:
        if f64: return struct.unpack_from('<d', d, p)[0], p + 8
        return struct.unpack_from('<f', d, p)[0], p + 4
    if t in (4, 21):
        n = struct.unpack_from('<I', d, p)[0]; p += 4
        s = d[p:p + n].decode('utf-8'); p += n + ((4 - n % 4) % 4)
        return (s if t == 4 else ('&', s)), p
    if t == 22:  # NodePath (novo formato)
        n = struct.unpack_from('<I', d, p)[0]
        raise ValueError('NodePath nao suportado')
    raise ValueError('variant tipo %d em %d' % (t, p))


def decode(path):
    b = open(path, 'rb').read()
    assert b[:4] == b'GDSC', path
    ver, dsize = struct.unpack_from('<II', b, 4)
    d = subprocess.run(['zstd', '-d', '-c'], input=b[12:], capture_output=True, check=True).stdout if dsize else b[12:]
    nid, ncon, nline, ntok = struct.unpack_from('<4I', d, 0)
    p = 16
    ids = []
    for _ in range(nid):
        n = struct.unpack_from('<I', d, p)[0]; p += 4
        ids.append(''.join(chr(struct.unpack_from('<I', bytes(x ^ 0xb6 for x in d[p + 4 * i:p + 4 * i + 4]))[0]) for i in range(n))); p += 4 * n
    cons = []
    for _ in range(ncon):
        v, p = read_variant(d, p); cons.append(v)
    lines = {}
    for _ in range(nline):
        ti, ln = struct.unpack_from('<II', d, p); p += 8; lines[ti] = ln
    cols = {}
    for _ in range(nline):
        ti, c = struct.unpack_from('<II', d, p); p += 8; cols[ti] = c
    toks = []
    for _ in range(ntok):
        c = d[p]
        if c & 0x80:
            v = struct.unpack_from('<I', d, p)[0] & ~0x80; p += 8
        else:
            v = c; p += 1
        toks.append((v & 0x7F, v >> 8))
    return ids, cons, toks, (lines, cols), len(d) - p


def lit(v):
    if isinstance(v, str):
        return '"' + v.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t') + '"'
    if isinstance(v, tuple): return '&' + lit(v[1])
    if v is None: return 'null'
    if isinstance(v, bool): return 'true' if v else 'false'
    if isinstance(v, float):
        r = repr(v)
        if 'e' not in r and '.' not in r: r += '.0'
        if r in ('inf', '-inf', 'nan'): r = {'inf': 'INF', '-inf': '-INF', 'nan': 'NAN'}[r]
        return r
    return str(v)


NOSPACE_BEFORE = set(') ] , . : ( ['.split())
NOSPACE_AFTER = set('( [ . $ ! ~ @'.split())


def to_source(path):
    ids, cons, toks, lines, rest = decode(path)
    out, cur, indent = [], [], 0
    prev = None
    lmap, cmap = lines
    for i, (t, idx) in enumerate(toks):
        name = TOK[t]
        if i in lmap and i > 0:
            out.append('\t' * indent + ''.join(cur)); cur = []; prev = None
            indent = cmap[i] - 1
        if name == 'NEWLINE':
            out.append('\t' * indent + ''.join(cur)); cur = []; prev = None; continue
        if name == 'INDENT': indent += 1; continue
        if name == 'DEDENT': indent -= 1; continue
        if name == 'EOF': break
        if name == 'IDENTIFIER': s = ids[idx]
        elif name == 'ANNOTATION': s = ids[idx]
        elif name == 'LITERAL': s = lit(cons[idx])
        else: s = name
        if cur:
            sp = True
            if s in NOSPACE_BEFORE: sp = False
            if prev in NOSPACE_AFTER: sp = False
            if s in ('(', '[') and prev not in ('=', ',', 'and', 'or', 'not', 'return', 'in', '+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>=', ':', '+=', '-=', '*=', '/=', '%', 'if', 'elif', 'while', '{', '->', 'await'):
                sp = False
            if prev == '-' and len(cur) >= 2 and cur[-2].strip() in ('(', ',', '=', '[', 'return', '*', '/', '+', '-', '<', '>', '==', ':'):
                sp = False
            if sp: cur.append(' ')
        cur.append(s); prev = s
    if cur: out.append('\t' * indent + ''.join(cur))
    return '\n'.join(out) + '\n', rest


if __name__ == '__main__':
    src, rest = to_source(sys.argv[1])
    sys.stdout.write(src)
    if rest: sys.stderr.write('[%d bytes sobrando]\n' % rest)
