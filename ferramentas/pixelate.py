"""Converte imagens para pixel art mantendo o tamanho original (grade de blocos)."""
import math
from PIL import Image, ImageFilter, ImageChops, ImageEnhance

def shrink(im, bx, by, resample):
    w, h = im.size
    sw, sh = max(1, math.ceil(w / bx)), max(1, math.ceil(h / by))
    return im.resize((sw, sh), resample)

def prep(small, sat, con, athr, gamma=1.0):
    rgb = small.convert('RGB')
    if gamma != 1: rgb = rgb.point([round(255 * (v / 255) ** gamma) for v in range(256)] * 3)
    if sat != 1: rgb = ImageEnhance.Color(rgb).enhance(sat)
    if con != 1: rgb = ImageEnhance.Contrast(rgb).enhance(con)
    a = small.getchannel('A').point(lambda v: 255 if v >= athr else 0)
    return rgb, a

def build_palette(pairs, colors):
    px = []
    for rgb, a in pairs:
        px += [p for p, al in zip(rgb.getdata(), a.getdata()) if al]
    if not px: px = [(0, 0, 0)]
    strip = Image.new('RGB', (len(px), 1)); strip.putdata(px)
    return strip.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, kmeans=3)

def finish(rgb, a, pal, outline, w, h, bx, by, clean=0):
    q = rgb.quantize(palette=pal, dither=Image.Dither.NONE)
    for _ in range(clean):
        q = q.filter(ImageFilter.ModeFilter(3))
    q = q.convert('RGB')
    out = q.convert('RGBA'); out.putalpha(a)
    if outline:
        dil = a.filter(ImageFilter.MaxFilter(3))
        ring = ImageChops.subtract(dil, a)
        out.paste(Image.new('RGBA', out.size, outline), (0, 0), ring)
    big = out.resize((out.width * round(bx) if bx == round(bx) else math.ceil(out.width * bx),
                      out.height * round(by) if by == round(by) else math.ceil(out.height * by)),
                     Image.Resampling.NEAREST)
    return big.crop((0, 0, w, h))

def process_group(files, bx, by, colors=24, outline=None, sat=1.15, con=1.1,
                  athr=110, resample=Image.Resampling.LANCZOS, clean=0, gamma=1.0, src_palette=False):
    """files: lista de (src, dst). Paleta compartilhada => animação sem tremedeira de cor."""
    loaded = []
    for src, dst in files:
        im = Image.open(src).convert('RGBA')
        small = shrink(im, bx, by, resample)
        loaded.append((im.size, small, dst))
    pairs = [prep(s, sat, con, athr, gamma) for _, s, _ in loaded]
    if src_palette:  # pixel art de origem: reaproveita as cores exatas do desenho original
        full = [Image.open(src).convert('RGBA') for src, _ in files]
        pal = build_palette([(im.convert('RGB'), im.getchannel('A').point(lambda v: 255 if v >= 128 else 0)) for im in full], colors)
    else:
        pal = build_palette(pairs, colors)
    for (size, _, dst), (rgb, a) in zip(loaded, pairs):
        finish(rgb, a, pal, outline, size[0], size[1], bx, by, clean).save(dst)
