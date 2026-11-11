# Cyber Sentinel — versão Android

`CyberSentinel-v8.apk` é o port do jogo para celular. Ele roda no **Godot 4.7.2**, com um
runtime próprio que reproduz os eventos do projeto GDevelop (`game.json`). O APK tem os mesmos
eventos, objetos, instâncias e recursos do projeto original e traz controles de toque na tela.

## Instalação

1. Copie `CyberSentinel-v8.apk` para o celular (Android 7.0 ou mais recente).
2. A v8 instala por cima da v7, porque usa a mesma assinatura. **Se a v6 estiver instalada,
   desinstale antes.** A v6 tem outra chave, então o Android não deixa instalar uma por cima da
   outra. O jogo não tem save, então nada se perde.
3. Abra o APK e permita a instalação de fontes desconhecidas, se o Android pedir.

## Controles de toque

| Botão | Ação |
|---|---|
| `<` `>` | Andar |
| PULO | Pular |
| TIRO | Atirar |
| ESCUDO | Ativar o escudo (fase 3) |
| X | Começar a luta com o chefe (fase 3) |
| E / Q | Avançar / sair do diálogo final |
| II | Pausar (Continuar ou Menu principal) |

O botão **voltar** do Android pausa durante as fases, volta ao menu nas outras telas e só fecha
o jogo a partir do menu principal. O jogo também pausa sozinho quando vai para segundo plano.

## O que mudou na v8 (em relação à v7)

- **Chefe lagarto congelava.** Ele dava um tiro, andava um pouco e parava. Ao espelhar um sprite,
  o port girava a imagem e a colisão em torno da origem, mas o GDevelop gira em torno do centro.
  Como o chefe nasce virado, a colisão dele ficava deslocada. Ele parava no c2 sem tocar o
  marcador e não ia para o próximo ponto. Agora o espelhamento é igual ao do GDevelop. Isso também
  tira o "pulinho" lateral que robôs, o monstro alado e o jogador davam ao virar.
- **Robô pulava alto demais**, e a câmera mostrava o vazio acima do cenário. O pulo subia ~305 px,
  contra 140 px no GDevelop. Agora a física segue o comportamento Plataforma do GDevelop: as
  velocidades de pulo e de queda são separadas e cada passo da física dura no máximo 0,05 s.
  Assim, uma travada do celular não lança mais o robô para cima.
- Um tween com o mesmo nome agora é apagado antes de ser recriado, como no GDevelop.

## O que mudou na v7 (em relação à v6)

Erros do port:

- As barras de vida de robôs cujo sprite não tem o ponto pedido (z4 a z7, entre outros) ficavam
  soltas, seguindo a câmera. Agora usam a origem do objeto, como no GDevelop.
- O movimento de vaivém (TimedBackAndForth) começava para o lado errado e virava a cada 2 s.
  Agora segue a extensão original: respeita a distância configurada, e o tempo limite só vale
  quando o objeto fica preso.
- A música de fundo era cortada por efeitos sonoros e podia tocar duplicada. Agora só uma música
  em loop toca por vez.

Erros que vieram do projeto original e foram corrigidos só no APK:

- O robo_z7 não morria (o evento apagava o robo_z).
- A torre 3 tocava a animação de morte no robo_a em vez do robo_a3.
- A barra do barZ4 usava o ponto do robo_z2.
- O monstro alado 2 nunca saía do marcador n6, porque o n5 aparecia duplicado.
- A cura do chefe lagarto aparecia em (0,0), fora do mapa. Agora cai no próprio chefe.
- As barreiras do c6 eram recriadas a cada quadro e podiam prender o jogador depois de o chefe
  morrer.
- Explosões e esperas de morte (drone3, robôs, chefe) se repetiam a cada quadro.
- O som de pegar a arma tocava dezenas de vezes seguidas.

Também foi adicionado: pausa, tratamento do botão voltar e remoção de tiros que ficam muito longe
do jogador.

## Arquivos desta pasta

| Caminho | Conteúdo |
|---|---|
| `CyberSentinel-v8.apk` | Jogo pronto para instalar (a v7 está no histórico do git) |
| `scripts_v7/` | Os 12 scripts GDScript que a v7 alterou, em texto |
| `scripts_v8/` | Os 3 scripts que a v8 alterou (`gd_sprite`, `platformer_object`, `tween`) |
| `ferramentas/gdc.py` | Decompilador de scripts `.gdc` (GDScript compilado, Godot 4.7) |
| `ferramentas/gdtok.py` | Tokenizador que confirma que o texto gera exatamente o mesmo bytecode |
| `ferramentas/build.py` | Troca scripts no APK, refaz o índice `assets.sparsepck` e a versão do manifest |
| `ferramentas/apkv2.py` | Assina e verifica o APK (esquema v2) usando o `openssl` |
| `ferramentas/certificado.der` | Certificado público da assinatura da v7 |

A chave privada da assinatura **não** está no repositório. Ela fica guardada fora dele e é
necessária para que versões futuras instalem por cima da v8 sem desinstalar.

### Gerar uma nova versão

```bash
python3 ferramentas/build.py CyberSentinel-v8.apk pasta_raiz/ sem_assinatura.apk 9
python3 ferramentas/apkv2.py sign sem_assinatura.apk CyberSentinel-v9.apk chave.pem ferramentas/certificado.der
python3 ferramentas/apkv2.py verify CyberSentinel-v9.apk
```

`pasta_raiz/` deve conter uma pasta `scripts/` com a mesma estrutura de `scripts_v7/`
(ex.: `pasta_raiz/scripts/objects/gd_sprite.gd`). Cada `.gd` substitui o `.gdc`
correspondente dentro do APK (ou o `.gd` que uma versão anterior já tinha trocado).
