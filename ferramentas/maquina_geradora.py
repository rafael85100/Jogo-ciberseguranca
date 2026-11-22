#!/usr/bin/env python3
"""Desenha a maquina geradora de inimigos em pixel art (assets/image/maquina/).

Padrao do projeto: 3 px de tela por pixel, contorno escuro (18,14,28), sem suavizacao.
Animacoes: ligada (4 quadros, nucleo pulsando), gerando (6 quadros, nucleo aceso com anel e raios),
desligada (1 quadro). Cada quadro tem 40x50 pixels logicos -> 120x150 na tela.
Uso (na pasta do projeto): python3 ferramentas/maquina_geradora.py
"""
import math, os
from PIL import Image

W, H, ESC = 40, 50, 3
OUT = 'assets/image/maquina'
CONT = (18, 14, 28)
M0, M1, M2, M3 = (34, 30, 52), (56, 52, 84), (88, 84, 122), (132, 128, 168)   # metal escuro -> claro
AMAR, PRETO = (240, 190, 40), (24, 20, 30)
CIANO, CIANO2 = (60, 220, 255), (20, 110, 150)
VERM = [(70, 10, 30), (140, 20, 60), (220, 40, 90), (255, 110, 160), (255, 210, 230)]  # nucleo: escuro -> branco


def novo():
    return [[None] * W for _ in range(H)]


def px(c, x, y, cor):
    if 0 <= x < W and 0 <= y < H:
        c[y][x] = cor


def ret(c, x0, y0, x1, y1, cor):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(c, x, y, cor)


def corpo(c, luz_on):
    # base com faixa de perigo
    ret(c, 2, 43, 37, 48, M1)
    ret(c, 2, 43, 37, 43, M3)
    for x in range(3, 37):
        px(c, x, 46, AMAR if ((x // 2) % 2 == 0) else PRETO)
        px(c, x, 47, AMAR if (((x + 1) // 2) % 2 == 0) else PRETO)
    ret(c, 2, 48, 37, 48, M0)
    # pilares laterais
    for x0 in (4, 31):
        ret(c, x0, 12, x0 + 4, 42, M1)
        ret(c, x0, 12, x0, 42, M3)
        ret(c, x0 + 4, 12, x0 + 4, 42, M0)
        for i, y in enumerate(range(16, 40, 5)):
            px(c, x0 + 2, y, CIANO if luz_on else CIANO2)
            px(c, x0 + 2, y + 1, CIANO2)
    # arco do portal (anel metalico) entre os pilares
    cx, cy = 19.5, 25.5
    for y in range(8, 43):
        for x in range(8, 32):
            d = math.hypot(x - cx, (y - cy) * 0.92)
            if 10.5 <= d < 13.5:
                px(c, x, y, M2 if d < 12 else M1)
            if 12.6 <= d < 13.5 and y < cy:
                px(c, x, y, M3)
    # parafusos no anel
    for a in range(0, 360, 45):
        r = math.radians(a)
        px(c, int(round(cx + math.cos(r) * 12)), int(round(cy + math.sin(r) * 12 / 0.92)), M3)
    # viga superior ligando os pilares, e a caixa do topo com a antena
    ret(c, 4, 10, 35, 12, M1)
    ret(c, 4, 10, 35, 10, M3)
    ret(c, 4, 12, 35, 12, M0)
    for x in (8, 12, 27, 31):
        px(c, x, 11, M3)
    ret(c, 14, 4, 25, 9, M1)
    ret(c, 14, 4, 25, 4, M3)
    ret(c, 19, 0, 20, 3, M2)
    ret(c, 16, 6, 23, 7, M0)
    return cx, cy


def nucleo(c, cx, cy, fase, brilho, raio=10.2):
    # redemoinho: cor depende da distancia ao centro e de um angulo que gira com a fase
    for y in range(10, 42):
        for x in range(9, 31):
            dx, dy = x - cx, (y - cy) * 0.92
            d = math.hypot(dx, dy)
            if d >= raio:
                continue
            ang = math.atan2(dy, dx)
            onda = math.sin(ang * 3 + d * 0.55 - fase)
            nivel = brilho + onda * 1.1 - d / raio * 1.6
            i = max(0, min(4, int(round(nivel))))
            px(c, x, y, VERM[i])


def contorno(c):
    out = [row[:] for row in c]
    for y in range(H):
        for x in range(W):
            if c[y][x] is None and any(0 <= x + dx < W and 0 <= y + dy < H and c[y + dy][x + dx] is not None
                                       and c[y + dy][x + dx] != CONT
                                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out[y][x] = CONT
    return out


def salvar(c, nome):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for y in range(H):
        for x in range(W):
            if c[y][x] is not None:
                im.putpixel((x, y), c[y][x] + (255,))
    im.resize((W * ESC, H * ESC), Image.NEAREST).save(os.path.join(OUT, nome))


os.makedirs(OUT, exist_ok=True)

# ligada: pulsa devagar, luz da antena pisca
for f in range(4):
    c = novo()
    cx, cy = corpo(c, luz_on=f % 2 == 0)
    nucleo(c, cx, cy, fase=f * math.pi / 2, brilho=1.6 + 0.4 * math.sin(f * math.pi / 2))
    px(c, 19, 0, VERM[3] if f % 2 == 0 else VERM[1]); px(c, 20, 0, VERM[3] if f % 2 == 0 else VERM[1])
    salvar(contorno(c), 'ligada%d.png' % f)

# gerando: nucleo aceso, anel de energia crescendo e raios saindo do anel
for f in range(6):
    c = novo()
    cx, cy = corpo(c, luz_on=True)
    nucleo(c, cx, cy, fase=f * math.pi / 3, brilho=3.3)
    r = 3 + f * 1.4
    for a in range(0, 360, 6):
        t = math.radians(a)
        px(c, int(round(cx + math.cos(t) * r)), int(round(cy + math.sin(t) * r / 0.92)), VERM[4])
    for k in range(3):
        a = math.radians(f * 47 + k * 120)
        x, y = cx + math.cos(a) * 12, cy + math.sin(a) * 13
        for s in range(5):
            x += math.cos(a + (0.9 if s % 2 else -0.9)) * 1.3
            y += math.sin(a + (0.9 if s % 2 else -0.9)) * 1.3
            px(c, int(round(x)), int(round(y)), CIANO if s % 2 else VERM[4])
    px(c, 19, 0, VERM[4]); px(c, 20, 0, VERM[4])
    salvar(contorno(c), 'gerando%d.png' % f)

# desligada: nucleo apagado
c = novo()
cx, cy = corpo(c, luz_on=False)
for y in range(10, 42):
    for x in range(9, 31):
        if math.hypot(x - cx, (y - cy) * 0.92) < 10.2:
            px(c, x, y, (28, 22, 40) if (x + y) % 5 else (40, 32, 56))
px(c, 19, 0, VERM[0]); px(c, 20, 0, VERM[0])
salvar(contorno(c), 'desligada.png')
print('ok')
