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

## Mudanças de 11/11/2026

- **Caixas** (`bloco` a `bloco4`): convertidas com o grupo `caixas` do `convert.py` (32 cores,
  contorno, gamma 1.0, redução BOX). Antes, era a única imagem de cenário fora da grade.
- **Prédios da cena2** (`p5.png`, `p6.png`): trocados por uma versão remasterizada, alinhada
  prédio a prédio à posição e ao recorte dos antigos. As fontes alinhadas, ainda sem pixelar,
  ficam em `../originais_remaster_2026-11-11/`, ao lado dos backups. O `convert.py` lê essas
  fontes no lugar do backup (`SRC_OVERRIDE`) e usa gamma 1.0, porque o remaster já é claro.
- **Fundo das cenas 1 e 2:** `bg_neon_cena1.png` (1935x1080, ampliado com NEAREST a partir de
  1679x937), no objeto `bj_2` com y -225 e altura 1080, para cobrir tudo o que a câmera mostra
  na vertical. A imagem já é pixel art, então não passa pelo `convert.py`.
- **Fundo da cena 3:** `bg_x7_cena3.png` (1536x1024, a imagem "Neon X7 Industrial Alley" sem
  alterações), na textura do objeto `lab_externo`. Tem o mesmo tamanho do fundo antigo
  (`lab_exeterno.png`), então posição e parallax ficaram iguais. O arquivo antigo continua no
  projeto porque o objeto global `lab_externo2` (sem instâncias) ainda aponta para ele.
- **Boss final `Mysterious` (cena `final`):** substitui o `boss_x`. Os quadros vêm das spritesheets
  "Mysterious (Boss)-shoot/punch" (4x4 quadros de 128x128), ampliados para 160x160 com LANCZOS e
  salvos em `assets/image/mysterious/` (`atirar_00..15`, `socar_00..15`). Animação 0 = Atirar
  (0,08 s/quadro, ponto `arma` no cano), 1 = Socar (0,06 s/quadro). Os eventos usam a variável de
  cena `modo_boss`: 0 = jogador a mais de 650 px, boss parado na pose de tiro; 1 = até 650 px,
  atira (bala no quadro 9, mesmas balas `bala_r1d`/`bala_r1d2` dos robôs atiradores da cena 2,
  15 de dano); 2 = jogador ao alcance do punho (`Width*0.445 + 25`), soca (25 de dano no quadro 7).
  A tecla Q não leva mais para a `cenademo`: só apaga a parede `ativa_dialogo_box` e esconde a
  caixa de texto. A cena agora também manda para a tela `dead` (tela_dead 4) quando a vida acaba.
  Quando a barra do Mysterious zera, ele explode e cria o `portalF` no lugar dele (em pé no chão).
  Encostar no portal leva à tela `load` com tela_load 5, que abre a `cenademo`. O `portalF` perdeu
  o comportamento de plataforma, que o deixava sólido e impedia o jogador de encostar nele.
- **Tiro do robô (`dis_paro_player1.png`, `dis_paro_player_2.png`):** refeitos fora do `convert.py`.
  O original do backup ganhou 6 px de margem transparente em cada lado (o contorno era cortado na
  borda) e foi pixelado com bloco 3, 24 cores, contorno e gamma 0.85 (com 0.6, igual ao resto do
  robô, ficava claro demais, porque o original já é mais claro). Em todas as cenas, origem, ponto
  `disparo` e máscara de colisão desses quadros foram deslocados +6 px, então nada muda de lugar.
  Atenção: rodar o `convert.py` de novo sobrescreve esses dois arquivos com a versão antiga.
  Conversa antes da luta (11/11/2026): o Mysterious fica em x 770, y 512 (pés em y 665, onde começa
  o desenho do piso; as 3 primeiras linhas do `tilenovo.png` são transparentes), tocando a animação
  2 = Parado (spritesheet "idle-trimmed", 15 quadros, 0,1 s). As 9 falas estão em
  `assets/dialogofinal.json`. A variável de cena `dialogo` controla tudo: 0 = ainda não começou
  (a caixa fica escondida); vira 1 quando o robô chega a menos de 60 px da parede
  `ativa_dialogo_box` (por distância, não por colisão: a colisão com a parede sólida liga e desliga
  e reiniciava a conversa). Com 1, soltar o Q completa a fala que está sendo escrita ou, se ela já
  terminou, passa para a próxima (`q_usado` impede que um mesmo Q faça as duas coisas). Quando a
  extensão diz que a conversa acabou (`IsDialogueRunning` falso, depois do Q na última fala), a
  parede some, a caixa se esconde, `luta` vira 1 e `dialogo` vira 2. Só com `luta` = 1 valem tiro,
  soco e dano no boss. O texto quebra linha sozinho (instância com largura fixa de 770 px).
- **Fundo da cena final:** `bg_arena_final.png` ("Neon Cyberpunk Hacker Arena", 1672x941 ampliado com
  NEAREST para 1819x1024), no objeto `finalbg` da cena `final`. A altura de 1024 e a posição
  (-64, -64) são as do fundo antigo, então cobre a mesma área da câmera. O `finalbg.png` antigo
  continua no projeto: os objetos `finalbg` da cena 2 e da cena 3 (sem instâncias) apontam para ele.

## Munição (13/11/2026)

`municao.py` aplica o sistema de munição no `game.json` (só roda uma vez; aborta se o objeto
`Municao` já existir). Pente de 12 balas, recarga de 1,2 s (tecla **R** ou automática com o pente
vazio). Reserva inicial: Normal 36, Difícil 24. Cada caixa dá +24 (Normal) ou +30 (Difícil), até 96.
As caixas (objeto global `Municao`, quadros em `assets/image/municao/`, corrigidos a partir do
spritesheet "Pixel Art Ammo Crate") ficam em pontos fixos de cada cena. No início, um laço
apaga caixas sorteadas até sobrar `alvo_municao`:

| Cena | Pontos | Normal | Difícil |
|---|---|---|---|
| cena1 | 5 | 2 | 1 |
| cena2 | 10 | 7 | 6 |
| cena3 | 7 | 4 | 3 |
| final | 3 | 2 | 1 |

No Insano (`dificuldade` = 2) as caixas somem, o contador fica escondido e o pente nunca esvazia.
Sem nenhuma bala, o robô gera 6 balas depois de 5 s (Normal) ou 8 s (Difícil), para a fase não travar.
Para mudar um ponto, arraste a caixa no editor da cena; para mudar a quantidade, edite o
primeiro evento da cena (`alvo_municao`).
