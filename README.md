# Cyber Sentinel — Jogo de Cibersegurança

Jogo de plataforma 2D em pixel art sobre cibersegurança, feito no **GDevelop 5**.
Você controla um guardião robótico que atravessa o mundo digital e derrota vírus,
robôs infectados e chefes para proteger os sistemas.

Projeto da **Equipe 2 — Redes A**, da **ETE Arlindo Ferreira dos Santos**.

## História

Em um mundo digital chamado **Ciberlândia**, todos viviam em paz até que um poderoso vírus
chamado **Shadow** começou a invadir computadores, celulares e servidores, apagando arquivos
e espalhando o caos. Para impedir a destruição, **Leo**, um jovem apaixonado por tecnologia,
é escolhido para se tornar o **Guardião dos Códigos**.

Com uma armadura tecnológica e uma arma de energia, Leo viaja pelas fases do mundo digital.
Ele enfrenta vírus com habilidades diferentes, coleta antivírus e atualizações de sistema e,
no fim de cada fase, encara um vírus chefe para recuperar partes do **Código Mestre**,
a única ferramenta capaz de eliminar Shadow de vez.

Mas o maior ataque cibernético da história escondia um segredo: o vírus era só o começo...

## Controles

| Tecla | Controle | Ação |
|---|---|---|
| ← → | Direcional / analógico esq. | Andar |
| Espaço | A | Pular |
| F | X | Atirar |
| G | B | Soco corpo a corpo |
| ↑ (segure) + F | Analógico dir. + X | Atirar para cima; com ← ou → junto, na diagonal |
| R | LB | Recarregar |
| D | Y | Ativar escudo por 3 segundos (fase 3 e final) |
| X | Back | Começar a luta com o chefe (fase 3) |
| E | LT | Avançar o diálogo (fase final) |
| Q | RB | Pular o diálogo final |
| Esc ou P (ou o botão II) | Start | Pausar e continuar nas fases |
| Na pausa: ↑ ↓ e Enter, ou M | Na pausa: direcional e A, ou B | Escolher CONTINUAR / MENU PRINCIPAL (M e B vão direto ao menu) |

A tabela também aparece no jogo, no botão **Controles** do menu. Nos menus, o analógico esquerdo
move um cursor e o A clica. Esc nas telas de Jogar, História, Equipe e Controles volta ao menu.

## Fases

1. **Cidade invadida:** primeiros drones inimigos.
2. **Distrito tecnológico:** robôs infectados que patrulham a cidade.
3. **Laboratório externo:** minas, monstros alados, vírus e o chefe **Lagarto Cibernético**.
4. **Final:** o confronto que revela a verdadeira ameaça.

## Como abrir o projeto

1. Instale o [GDevelop 5](https://gdevelop.io/download) (versão 5.6 ou mais recente).
2. Baixe este repositório:
   ```bash
   git clone https://github.com/rafael85100/Jogo-ciberseguranca.git
   ```
   Se preferir, use **Code → Download ZIP** aqui no GitHub.
3. No GDevelop, vá em **Abrir projeto** e escolha o arquivo `game.json`.
4. Clique em **Preview** para jogar. O jogo começa pela cena `menu`.

## Jogar no Windows (.exe)

Baixe [`windows/CyberSentinel.exe`](windows/CyberSentinel.exe) e dê dois cliques. Não precisa
instalar nada nem abrir o GDevelop. Se o Windows avisar que protegeu o computador, clique em
**Mais informações → Executar assim mesmo**. Detalhes em [`windows/LEIAME.md`](windows/LEIAME.md).

## Versão para celular (Android)

O jogo também tem um port para Android, com controles de toque, pausa e suporte ao botão voltar.
A versão mais recente, a v22 (com as máquinas geradoras), fica na página de
[Releases](https://github.com/rafael85100/Jogo-ciberseguranca/releases/tag/apk-v22), porque passa do limite de tamanho de arquivo do GitHub. Instalação, controles e a lista de correções de cada versão estão em
[`mobile/LEIAME.md`](mobile/LEIAME.md).

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `game.json` | Projeto do GDevelop: cenas, objetos e eventos |
| `assets/` | Sprites, efeitos, barras de vida e fontes |
| `equipe/` | Fotos da equipe (tela de créditos) |
| `*.png`, `*.jpeg` (na raiz) | Cenários, chefes, telas e painéis |
| `*.mp3`, `*.wav` | Músicas e efeitos sonoros |
| `ferramentas/` | Scripts em Python que converteram o visual para pixel art (veja o `LEIAME.md` da pasta) |
| `mobile/` | APK do port para Android, scripts alterados e ferramentas de build e assinatura |

O visual do jogo foi convertido de um estilo realista para **pixel art**, com uma grade de
3 px de tela por pixel de arte. As interfaces (menu, painéis e diálogos) mantiveram o estilo original.

## Equipe

**Equipe 2 — Redes A** · ETE Arlindo Ferreira dos Santos

- Evellyn Rayane
- Glaydson Emanuel
- José Henrique
- José Iarlisson
- Júlia Francisca
- Lavinya Ellen
- Othon Lucas
- Rafael Conceição
