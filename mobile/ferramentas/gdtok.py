#!/usr/bin/env python3
"""Tokenizador GDScript minimo para validar ida-e-volta contra o bytecode (.gdc)."""
import re, sys, glob, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gdc

KEYWORDS = {n for n in gdc.TOK if re.fullmatch(r'[a-z_]+', n) and n not in ('_',)} | {'PI', 'TAU', 'INF', 'NAN'}
OPS = sorted([n for n in gdc.TOK if not re.fullmatch(r'[A-Za-z_]+', n)], key=len, reverse=True)


def tokenize(src):
    out = []
    i, n = 0, len(src)
    depth = 0
    line_start = True
    indent_stack = [0]
    while i < n:
        c = src[i]
        if c == '\n':
            i += 1; continue
        if c in ' \t':
            i += 1; continue
        if c == '#':
            while i < n and src[i] != '\n': i += 1
            continue
        if c == '\\' and i + 1 < n and src[i + 1] == '\n':
            i += 2; continue
        if c == '@':
            m = re.match(r'@[A-Za-z_]\w*', src[i:]); out.append(('ANNOTATION', m.group(0))); i += len(m.group(0)); continue
        if c == '&' and i + 1 < n and src[i + 1] == '"':
            s, i = _string(src, i + 1); out.append(('LITERAL', ('&', s))); continue
        if c == '"':
            s, i = _string(src, i); out.append(('LITERAL', s)); continue
        m = re.match(r'(\d[\d_]*\.\d*(?:e[+-]?\d+)?|\d[\d_]*e[+-]?\d+|\.\d+(?:e[+-]?\d+)?|0x[0-9a-fA-F_]+|\d[\d_]*)', src[i:])
        if m and (c.isdigit() or (c == '.' and i + 1 < n and src[i + 1].isdigit())):
            t = m.group(0).replace('_', '')
            if t.startswith('0x'): v = int(t, 16)
            elif any(ch in t for ch in '.e'): v = float(t)
            else: v = int(t)
            out.append(('LITERAL', v)); i += len(m.group(0)); continue
        m = re.match(r'[A-Za-z_]\w*', src[i:])
        if m:
            w = m.group(0); i += len(w)
            if w in ('true', 'false'): out.append(('LITERAL', w == 'true'))
            elif w == 'null': out.append(('LITERAL', None))
            elif w == '_': out.append(('_', None))
            elif w in KEYWORDS: out.append((w, None))
            else: out.append(('IDENTIFIER', w))
            continue
        for op in OPS:
            if src.startswith(op, i):
                out.append((op, None)); i += len(op); break
        else:
            raise SyntaxError('caractere inesperado %r na posicao %d' % (c, i))
    return _fold_negatives(out)


def _fold_negatives(toks):
    out = []
    operand_end = {'IDENTIFIER', 'LITERAL', ')', ']', '}', 'PI', 'TAU', 'INF', 'NAN', 'self'}
    for t in toks:
        if (t[0] == 'LITERAL' and isinstance(t[1], (int, float)) and not isinstance(t[1], bool)
                and out and out[-1][0] == '-' and (len(out) < 2 or out[-2][0] not in operand_end)):
            out[-1] = ('LITERAL', -t[1]); continue
        out.append(t)
    return out


def _string(src, i):
    assert src[i] == '"'
    i += 1; buf = []
    while src[i] != '"':
        if src[i] == '\\':
            e = src[i + 1]
            buf.append({'n': '\n', 't': '\t', '"': '"', '\\': '\\', 'r': '\r'}.get(e, '\\' + e)); i += 2
        else:
            if src[i] == '\n': raise SyntaxError('string sem fechar')
            buf.append(src[i]); i += 1
    return ''.join(buf), i + 1


def from_gdc(path):
    ids, cons, toks, _, _ = gdc.decode(path)
    out = []
    for t, idx in toks:
        name = gdc.TOK[t]
        if name in ('NEWLINE', 'INDENT', 'DEDENT', 'EOF'): continue
        if name in ('IDENTIFIER', 'ANNOTATION'): out.append((name, ids[idx]))
        elif name == 'LITERAL': out.append((name, cons[idx]))
        elif name == '_': out.append(('_', None))
        else: out.append((name, None))
    return out


def same(a, b):
    if len(a) != len(b): return False, 'tamanhos %d != %d' % (len(a), len(b))
    for k, (x, y) in enumerate(zip(a, b)):
        if x[0] != y[0]: return False, 'token %d: %r != %r' % (k, x, y)
        if isinstance(x[1], float) or isinstance(y[1], float):
            if abs(float(x[1]) - float(y[1])) > 1e-6 * max(1, abs(float(y[1]))): return False, 'token %d: %r != %r' % (k, x, y)
        elif x[1] != y[1] or type(x[1]) != type(y[1]):
            return False, 'token %d: %r != %r' % (k, x, y)
    return True, ''


if __name__ == '__main__':
    gdc_root, src_root = sys.argv[1], sys.argv[2]
    bad = 0
    for f in sorted(glob.glob(gdc_root + '/**/*.gdc', recursive=True)):
        rel = os.path.relpath(f, gdc_root)[:-4] + '.gd'
        ok, why = same(tokenize(open(os.path.join(src_root, rel)).read()), from_gdc(f))
        if not ok: bad += 1; print('DIFERE', rel, why)
    print('arquivos com diferenca:', bad)
