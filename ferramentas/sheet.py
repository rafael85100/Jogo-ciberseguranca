import sys
from PIL import Image, ImageDraw
out, cell = sys.argv[1], int(sys.argv[2]); files = sys.argv[3:]
cols = 4; rows = (len(files)+cols-1)//cols
S = Image.new('RGB', (cols*cell, rows*(cell+14)), (60,60,70)); dr = ImageDraw.Draw(S)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGBA'); im.thumbnail((cell, cell))
    bg = Image.new('RGBA', im.size, (200,0,200,255)) if False else Image.new('RGBA', im.size, (90,90,100,255))
    bg.alpha_composite(im)
    x, y = (i%cols)*cell, (i//cols)*(cell+14)
    S.paste(bg.convert('RGB'), (x, y+14)); dr.text((x+2, y), f.split('/')[-1][:40], fill=(255,255,0))
S.save(out)
