#!/usr/bin/env python3
"""Desenha assets/image/tabela_controles.png (1280x720), a tabela da cena "controles".

Mesmo desenho da tela de controles do APK v21 (runtime/gd_controles_lista.gd), com as teclas do PC.
Gera tambem soco_hitbox.png (area invisivel do soco) e cursor_pad.png (cursor do controle nos menus).
Uso: python3 ferramentas/tabela_controles.py   (na pasta do projeto)
"""
from PIL import Image, ImageDraw, ImageFont

PAINEL = (60, 14, 1220, 576)
LARANJA = (255, 158, 51)
AZUL = (115, 217, 255)
BRANCO = (242, 242, 247)
CINZA = (184, 189, 204)
Y_TITULO, Y_CAB, Y_LIN, ALT = 56, 104, 116, 24
COL_ACAO, COL_TECLADO, COL_CONTROLE = 100, 470, 820

LINHAS = [
    ("Andar", ["@L", "@R", "~ou", "A", "D"], ["Direcional", "~ou", "Analógico esq."]),
    ("Pular", ["ESPAÇO"], ["A"]),
    ("Atirar (para onde está virado)", ["F"], ["X"]),
    ("Soco corpo a corpo", ["G"], ["B"]),
    ("Mirar para cima (segure)", ["@U", "~ou", "W"], ["Analógico dir.", "~para cima"]),
    ("Mirar na diagonal (segure)", ["@U", "~+", "@L", "~/", "@R", "~ou", "W", "~+", "A", "~/", "D"], ["Analógico dir.", "~+ lado"]),
    ("Atirar na direção da mira", ["~Mirar +", "F"], ["~Mirar +", "X"]),
    ("Escudo (fase 3 e final)", ["C"], ["Y"]),
    ("Avançar o diálogo", ["E"], ["LT"]),
    ("Fechar diálogo / próxima cena", ["Q"], ["RB"]),
    ("Recarregar", ["R"], ["LB"]),
    ("Iniciar a luta do chefe", ["X", "~(solte)"], ["Back"]),
    ("Pausar / continuar (nas fases)", ["Esc", "~ou", "P", "~ou botão II na tela"], ["Start"]),
    ("Pausa: escolher a opção", ["@U", "@D", "~ou", "W", "S"], ["Direcional"]),
    ("Pausa: confirmar a opção", ["Enter", "~ou", "ESPAÇO"], ["A"]),
    ("Pausa: ir direto ao menu principal", ["M"], ["B"]),
    ("Voltar ao menu (Jogar, História, Equipe...)", ["Esc"], ["~botão Voltar na tela"]),
    ("Menus", ["~mouse"], ["Analógico esq. move", "A clica"]),
]

f_tit = ImageFont.truetype('STAR7.ttf', 34)
f_cab = ImageFont.truetype('assets/Roboto-Regular.ttf', 18)
f_txt = ImageFont.truetype('assets/Roboto-Regular.ttf', 16)
f_chip = ImageFont.truetype('assets/Roboto-Regular.ttf', 14)
f_rod = ImageFont.truetype('assets/Roboto-Regular.ttf', 14)

im = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
d = ImageDraw.Draw(im, 'RGBA')
d.rectangle(PAINEL, fill=(5, 8, 13, 219))
d.rectangle(PAINEL, outline=LARANJA, width=3)
d.text((640, Y_TITULO), "CONTROLES", font=f_tit, fill=LARANJA, anchor='ms')
d.text((COL_ACAO, Y_CAB), "AÇÃO", font=f_cab, fill=LARANJA, anchor='ls')
d.text((COL_TECLADO, Y_CAB), "TECLADO", font=f_cab, fill=LARANJA, anchor='ls')
d.text((COL_CONTROLE, Y_CAB), "CONTROLE", font=f_cab, fill=AZUL, anchor='ls')
d.line((PAINEL[0] + 30, Y_CAB + 8, PAINEL[2] - 30, Y_CAB + 8), fill=LARANJA + (153,), width=2)


def chip(x, y, w, cor):
    d.rectangle((x, y + 2, x + w, y + 21), fill=(26, 31, 41, 245), outline=cor + (230,), width=2)


def seta(cx, cy, k):
    if k == 'L':
        pts = [(cx - 7, cy), (cx + 2, cy - 6), (cx + 2, cy + 6)]
    elif k == 'R':
        pts = [(cx + 7, cy), (cx - 2, cy - 6), (cx - 2, cy + 6)]
    elif k == 'D':
        pts = [(cx, cy + 7), (cx - 6, cy - 2), (cx + 6, cy - 2)]
    else:
        pts = [(cx, cy - 7), (cx - 6, cy + 2), (cx + 6, cy + 2)]
    d.polygon(pts, fill=BRANCO)


def celulas(x, y, tokens, cor):
    for t in tokens:
        if t.startswith('~'):
            d.text((x, y + 16), t[1:], font=f_chip, fill=CINZA, anchor='ls')
            x += d.textlength(t[1:], font=f_chip) + 6
        elif t.startswith('@'):
            chip(x, y, 26, cor)
            seta(x + 13, y + 12, t[1:])
            x += 32
        else:
            w = d.textlength(t, font=f_chip) + 16
            chip(x, y, w, cor)
            d.text((x + 8, y + 16), t, font=f_chip, fill=BRANCO, anchor='ls')
            x += w + 6


for i, (acao, tec, pad) in enumerate(LINHAS):
    y = Y_LIN + i * ALT
    if i % 2 == 0:
        d.rectangle((PAINEL[0] + 24, y, PAINEL[2] - 24, y + ALT), fill=(17, 20, 25, 219))
    d.text((COL_ACAO, y + 17), acao, font=f_txt, fill=BRANCO, anchor='ls')
    celulas(COL_TECLADO, y, tec, LARANJA)
    celulas(COL_CONTROLE, y, pad, AZUL)

d.text((PAINEL[0] + 30, PAINEL[3] - 12),
       "Com um controle conectado (Xbox ou parecido), os botões dele funcionam junto com o teclado.",
       font=f_rod, fill=CINZA, anchor='ls')
im.save('assets/image/tabela_controles.png')

Image.new('RGBA', (68, 60), (0, 0, 0, 0)).save('assets/image/soco_hitbox.png')

c = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
cd = ImageDraw.Draw(c)
cd.ellipse((2, 2, 30, 30), outline=(255, 255, 255, 230), width=2)
cd.ellipse((13, 13, 19, 19), fill=(255, 51, 77, 242))
c.save('assets/image/cursor_pad.png')
print('ok')
