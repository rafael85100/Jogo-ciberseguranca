# Cyber Sentinel — versão para Windows

`CyberSentinel.exe` é o jogo de PC (o mesmo `game.json` do GDevelop) num único arquivo.
Não precisa instalar nada.

## Como jogar

1. Baixe o [`CyberSentinel.exe`](CyberSentinel.exe) (no GitHub, abra o arquivo e clique em
   **Download raw file**).
2. Dê dois cliques nele. O jogo abre numa janela própria.
3. Se o Windows mostrar **"O Windows protegeu o computador"**, clique em **Mais informações** e
   depois em **Executar assim mesmo**. O aviso aparece porque o arquivo não tem assinatura digital.

Requisitos: Windows 10 ou 11 de 64 bits. A janela usa o Microsoft Edge, que já vem no Windows
(ou o Google Chrome, se o Edge não existir). Os controles são os do [README](../README.md#controles).

## Como funciona

O `.exe` traz dentro dele a exportação HTML5 do jogo, feita com o exportador oficial do GDevelop.
Ao abrir, ele serve esses arquivos só para o próprio computador (`127.0.0.1`) e abre uma janela
de aplicativo do Edge. Quando a janela fecha, o `.exe` também fecha.

O botão **Sair** do menu também fecha o jogo. Na exportação HTML5, a ação "Sair do jogo" do GDevelop
não faz nada fora do Electron, por isso o launcher acrescenta um script à página: quando o jogo pede
para sair, a página chama `/__quit` e o launcher fecha a janela e termina.

Para o arquivo caber no limite de 100 MB do GitHub, os PNGs foram regravados em WebP **sem perdas**
(os pixels são idênticos, o script confere um por um). Os nomes dos arquivos continuam iguais.

## Como gerar de novo

Ferramentas em `ferramentas/` (precisa de Node.js, Python com Pillow e Go):

```bash
npm install gdcore-tools
node ferramentas/export.mjs /caminho/do/game.json "$PWD/web"   # exporta o jogo para HTML5
python3 ferramentas/towebp.py web                              # PNG -> WebP sem perdas (TOWEBP_JOBS=6 threads)

mkdir launcher && cp ferramentas/launcher.go launcher/main.go && cp -r web launcher/game
cd launcher && go mod init cybersentinel
GOOS=windows GOARCH=amd64 go build -trimpath -ldflags="-s -w -H windowsgui" -o CyberSentinel.exe .
```
