#!/usr/bin/env python3
"""Le e grava texturas .ctex do Godot 4 (CompressedTexture2D, GST2 v1) com imagem WebP sem perda.

Layout: 'GST2' | versao u32=1 | largura u32 | altura u32 | flags u32 | mipmap_limit u32 | 3x u32 reservado
        | data_format u32 (2=WebP) | w u16 | h u16 | mipmaps u32 | formato u32 (5=RGBA8) | tamanho u32 | WebP
"""
import io, struct, sys
from PIL import Image

def parse(d):
    assert d[:4] == b'GST2', 'nao e GST2'
    ver, w, h, flags, mlim = struct.unpack_from('<IIIII', d, 4)
    fmt_data, = struct.unpack_from('<I', d, 36)
    w2, h2, mips, fmt, size = struct.unpack_from('<HHIII', d, 40)
    return dict(ver=ver, w=w, h=h, flags=flags, mlim=mlim, data_format=fmt_data, mips=mips, fmt=fmt,
                payload=d[56:56 + size], tail=len(d) - 56 - size)

def build(template, img):
    """Gera .ctex com o mesmo cabecalho do template, trocando dimensoes e imagem."""
    t = parse(template)
    assert t['ver'] == 1 and t['data_format'] == 2 and t['mips'] == 0 and t['tail'] == 0, t
    img = img.convert('RGBA')
    buf = io.BytesIO(); img.save(buf, 'WEBP', lossless=True, quality=100, method=4, exact=True)
    webp = buf.getvalue()
    w, h = img.size
    out = bytearray(template[:56])
    struct.pack_into('<II', out, 8, w, h)
    struct.pack_into('<HHIII', out, 40, w, h, 0, 5, len(webp))
    return bytes(out) + webp

def decode(d):
    t = parse(d)
    return Image.open(io.BytesIO(t['payload']))

if __name__ == '__main__':
    # ctex.py template.ctex imagem.png saida.ctex
    tpl, png, out = sys.argv[1:4]
    open(out, 'wb').write(build(open(tpl, 'rb').read(), Image.open(png)))
