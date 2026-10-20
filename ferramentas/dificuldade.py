"""Adiciona a cena "dificuldade" (Normal / Difícil / Insano) e os multiplicadores
globais mult_hp e mult_dano ao game.json.

- HP de inimigos/bosses: o dano que eles recebem é dividido por mult_hp
  (equivale a multiplicar a vida, sem mexer no visual das barras).
- Dano em inimigos/bosses ao player: multiplicado por mult_dano.

Uso: python3 ferramentas/dificuldade.py game.json
"""
import copy
import json
import sys
import uuid

from PIL import ImageFont

DIFICULDADES = [
    # nome do botão, texto, mult_hp, mult_dano
    ("bt_normal", "txt_normal", "Normal", 1, 1),
    ("bt_dificil", "txt_dificil", "Difícil", 1.3, 1.25),
    ("bt_insano", "txt_insano", "Insano", 2, 1.75),
]
CENTRO_X = 862.5  # centro horizontal dos textos na cena menu
BAR = "PanelSpriteContinuousBar::PanelSpriteContinuousBar::"


def uid():
    return str(uuid.uuid4())


def ev(conditions, actions):
    return {"type": "BuiltinCommonInstructions::Standard",
            "conditions": conditions, "actions": actions}


def instr(value, params):
    return {"type": {"value": value}, "parameters": params}


def clicked(obj):
    return instr("PanelSpriteButton::PanelSpriteButton::IsClicked", [obj, ""])


def ir_para(cena):
    return instr("Scene", ["", f'"{cena}"', ""])


def walk(events):
    for e in events:
        yield e
        yield from walk(e.get("events", []))


def main(path):
    g = json.load(open(path))
    layouts = g["layouts"]
    if any(l["name"] == "dificuldade" for l in layouts):
        sys.exit("a cena dificuldade já existe")
    menu = next(l for l in layouts if l["name"] == "menu")

    # variáveis globais
    for nome in ("mult_hp", "mult_dano"):
        g["variables"].append({"name": nome, "type": "number", "value": 1})

    # ----- cena dificuldade, clonada da menu -----
    cena = copy.deepcopy(menu)
    cena["name"] = cena["mangledName"] = "dificuldade"
    cena["stopSoundsOnStartup"] = False  # mantém a música do menu tocando

    renomear = {"bt_jogar": "bt_normal", "bt_historia": "bt_dificil",
                "bt_equipe": "bt_insano", "bt_sair": "bt_voltar",
                "txt_jogar": "txt_normal", "txt_historio": "txt_dificil",
                "txt_equipe": "txt_insano", "txt_sair": "txt_voltar"}
    textos = {t: s for _, t, s, _, _ in DIFICULDADES}
    textos["txt_voltar"] = "Voltar"
    usados = {i["name"] for i in menu["instances"]}

    objetos = []
    for o in cena["objects"]:
        if o["name"] not in usados:
            continue
        o["name"] = renomear.get(o["name"], o["name"])
        o["persistentUuid"] = uid()
        if o["name"] in textos:
            o["string"] = o["content"]["text"] = textos[o["name"]]
        objetos.append(o)
    cena["objects"] = objetos
    cena["objectsFolderStructure"]["children"] = [{"objectName": o["name"]} for o in objetos]

    fonte = ImageFont.truetype("STAR7.ttf", 30)
    for i in cena["instances"]:
        i["name"] = renomear.get(i["name"], i["name"])
        i["persistentUuid"] = uid()
        if i["name"] in textos:
            i["x"] = round(CENTRO_X - fonte.getlength(textos[i["name"]]) / 2)

    cena["events"] = [ev([instr("SceneJustBegins", [""])],
                         [instr("SetFullScreen", ["", "yes", ""])])]
    for bt, _, _, hp, dano in DIFICULDADES:
        cena["events"].append(ev([clicked(bt)], [
            instr("SetNumberVariable", ["mult_hp", "=", str(hp)]),
            instr("SetNumberVariable", ["mult_dano", "=", str(dano)]),
            ir_para("cena1"),
        ]))
    cena["events"].append(ev([clicked("bt_voltar")], [ir_para("menu")]))
    layouts.insert(layouts.index(menu) + 1, cena)

    # ----- menu: JOGAR abre a escolha de dificuldade -----
    for e in walk(menu["events"]):
        for a in e.get("actions", []):
            if a["type"]["value"] == "Scene" and a["parameters"][1] == '"cena1"':
                a["parameters"][1] = '"dificuldade"'

    # ----- multiplicadores no dano -----
    todos = [l["events"] for l in layouts] + [x["events"] for x in g["externalEvents"]]
    n_dano = n_hp = 0
    for evs in todos:
        for e in walk(evs):
            for a in e.get("actions", []):
                if a["type"]["value"] != BAR + "SetValue" or a["parameters"][1] != "-":
                    continue
                obj, valor = a["parameters"][0], a["parameters"][2]
                if obj == "balas":
                    continue
                if obj == "bar_vida_play":
                    a["parameters"][2] = f"{valor} * mult_dano"
                    n_dano += 1
                else:
                    a["parameters"][2] = f"{valor} / mult_hp"
                    n_hp += 1
            # o drop de vida do boss lagarto testava "= 100" exato; com dano
            # fracionado a barra pode pular esse valor
            for c in e.get("conditions", []):
                p = c["parameters"]
                if c["type"]["value"] == BAR + "Value" and p[0] == "MetalRedBar" and p[1] == "=":
                    p[1] = "<="

    json.dump(g, open(path, "w"), indent=2, ensure_ascii=False)
    print(f"dano ao player: {n_dano} ações | dano em inimigos/bosses: {n_hp} ações")


if __name__ == "__main__":
    main(sys.argv[1])
