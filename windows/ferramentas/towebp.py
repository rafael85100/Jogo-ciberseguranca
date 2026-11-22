import sys, os, io
from PIL import Image, ImageChops
from concurrent.futures import ThreadPoolExecutor
root = sys.argv[1]
def conv(path):
    try:
        im = Image.open(path); im.load()
    except Exception as e:
        return 0
    if getattr(im, "n_frames", 1) > 1: return 0
    mode = "RGBA" if ("A" in im.getbands() or "transparency" in im.info) else "RGB"
    src = im.convert(mode)
    buf = io.BytesIO()
    src.save(buf, "WEBP", lossless=True, quality=100, method=6, exact=True)
    data = buf.getvalue()
    old = os.path.getsize(path)
    if len(data) >= old: return 0
    back = Image.open(io.BytesIO(data)).convert(mode)
    if ImageChops.difference(src, back).getbbox() is not None: return 0
    open(path, "wb").write(data)
    return old - len(data)
files = [os.path.join(d, f) for d, _, fs in os.walk(root) for f in fs if f.lower().endswith(".png")]
# threads (o Pillow libera o GIL ao comprimir); com processos o pool quebrava (ConnectionResetError)
with ThreadPoolExecutor(max_workers=int(os.environ.get('TOWEBP_JOBS', '6'))) as ex:
    saved = sum(ex.map(conv, files))
print(len(files), "pngs, saved MB:", saved/1e6)
