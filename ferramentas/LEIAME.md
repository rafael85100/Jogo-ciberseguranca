# Ferramentas de pixel art — Cyber Sentinel

Scripts usados em 19/10/2026 para converter o jogo para pixel art.
Requisito: Python 3 com Pillow (`pip install pillow`).

Rode os comandos a partir da pasta `projeto_ete_expo/` (a que fica acima do projeto).
**Feche o GDevelop antes**, porque alguns scripts alteram o `game.json`.

## Scripts

| Arquivo | O que faz |
|---|---|
| `pixelate.py` | Biblioteca de conversão. Reduz a imagem em blocos, limita a paleta (compartilhada entre os quadros de uma animação), coloca contorno escuro e aumenta de volta para o tamanho original. Como o tamanho é preservado, colisões e pontos não mudam. |
| `scales.py` | Calcula com que escala cada imagem aparece na tela (tamanho das instâncias e `SetSize` nos eventos). Gera o `scales.json` usado pelo `convert.py`. |
| `convert.py` | Converte todos os sprites e cenários escolhidos. **Lê sempre do backup original** e grava no projeto. A lista de grupos (player, bosses, fundos etc.) e os ajustes de cada um ficam no próprio arquivo. |
| `patch_json.py` | Desliga a suavização (`smoothed: false`) nas imagens pixel art e liga o `pixelsRounding` no `game.json`. |
| `inventory.py` | Lista todas as imagens do projeto, o tamanho delas e quais objetos as usam. |
| `events.py` | Imprime os eventos de uma cena ou de eventos externos que mencionam um objeto. Exemplo: `events.py game.json ex_serpente lagarto_boss`. |
| `sheet.py` | Monta uma folha de prévia com várias imagens lado a lado. |

## Refazer a conversão

```bash
cd ~/Downloads/projeto_ete_expo
python3 projeto_ete_expo/ferramentas/scales.py projeto_ete_expo scales.json
python3 projeto_ete_expo/ferramentas/convert.py backup_antes_pixelart_2026-10-19 projeto_ete_expo scales.json convertidas.json
python3 projeto_ete_expo/ferramentas/patch_json.py projeto_ete_expo/game.json convertidas.json
```

Para converter um sprite novo, adicione uma linha à lista `groups` do `convert.py`, de preferência pelo nome do objeto com `obj_files({...})`. Como o `convert.py` lê do backup, uma imagem nova também precisa ser copiada para o backup, no mesmo caminho relativo.

## Padrões usados

- **Grade:** 3 px de tela por pixel de arte (`P = 3` no `convert.py`).
- **Contorno:** cor `(18, 14, 28)`.
- **Cores e brilho por tipo:**
  - personagens: 24 cores, gamma 0,72;
  - protagonista: gamma 0,6;
  - fundos: 40 cores, gamma 0,72, sem contorno.
- **Imagens esticadas nas cenas** (prédios, árvores): usam `scale='max'`.
- **Pixel art de origem** (robôs): usa `src_palette=True` e redução `NEAREST`.
- **Efeitos criados nos eventos:** posicione no centro do alvo com `Alvo.BoundingBoxCenterX()` e `Alvo.BoundingBoxCenterY()`, porque os sprites têm origem no canto superior esquerdo.
