// Cyber Sentinel - launcher para Windows.
// Serve o jogo exportado do GDevelop (embutido no .exe) em 127.0.0.1 e abre
// uma janela de aplicativo do Edge/Chrome. Fecha sozinho quando a janela fecha.
// O botão Sair do jogo (ação "Sair do jogo" do GDevelop) chama /__quit: o launcher
// fecha a janela do navegador e termina.
package main

import (
	"embed"
	"io/fs"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"runtime"
	"strings"
	"sync/atomic"
	"time"
)

//go:embed all:game
var gameFiles embed.FS

var lastPing atomic.Int64

// quitReq recebe um sinal quando o jogo pede para sair.
var quitReq = make(chan struct{}, 1)

// browserCmd é o processo da janela do jogo (nil se abriu no navegador padrão).
var browserCmd *exec.Cmd

// Na exportação HTML5, a ação "Sair do jogo" do GDevelop só fecha a janela no Electron.
// Aqui ela avisa o launcher (/__quit) e tenta fechar a janela.
const heartbeat = `<script>setInterval(function(){fetch("/__alive").catch(function(){})},3000);fetch("/__alive");
(function(){var R=window.gdjs&&gdjs.RuntimeGameRenderer;if(!R)return;var orig=R.prototype.stopGame;
R.prototype.stopGame=function(){try{orig&&orig.call(this)}catch(e){}
try{navigator.sendBeacon("/__quit")}catch(e){fetch("/__quit",{method:"POST",keepalive:true}).catch(function(){})}
setTimeout(function(){try{window.close()}catch(e){}},300)};})();</script></body>`

func main() {
	sub, _ := fs.Sub(gameFiles, "game")
	index, _ := fs.ReadFile(sub, "index.html")
	index = []byte(strings.Replace(string(index), "</body>", heartbeat, 1))

	mux := http.NewServeMux()
	mux.HandleFunc("/__alive", func(w http.ResponseWriter, r *http.Request) {
		lastPing.Store(time.Now().Unix())
		w.WriteHeader(204)
	})
	mux.HandleFunc("/__quit", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(204)
		select {
		case quitReq <- struct{}{}:
		default:
		}
	})
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		p := strings.TrimPrefix(path.Clean(r.URL.Path), "/")
		if p == "" || p == "index.html" {
			w.Header().Set("Content-Type", "text/html; charset=utf-8")
			w.Write(index)
			return
		}
		data, err := fs.ReadFile(sub, p)
		if err != nil {
			http.NotFound(w, r)
			return
		}
		ct := ""
		switch strings.ToLower(path.Ext(p)) {
		case ".js":
			ct = "text/javascript"
		case ".json":
			ct = "application/json"
		case ".wasm":
			ct = "application/wasm"
		case ".mp3":
			ct = "audio/mpeg"
		case ".wav":
			ct = "audio/wav"
		case ".ttf":
			ct = "font/ttf"
		default:
			ct = http.DetectContentType(data) // PNGs podem ser WebP sem perdas por dentro
		}
		w.Header().Set("Content-Type", ct)
		w.Write(data)
	})

	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		os.Exit(1)
	}
	url := "http://" + ln.Addr().String() + "/"
	go http.Serve(ln, mux)
	os.Stdout.WriteString(url + "\n")

	browserExited := make(chan struct{})
	if !openAppWindow(url, browserExited) {
		openDefault(url)
	}

	// Encerra quando a janela do jogo fecha (a página para de dar sinal).
	// Janelas minimizadas têm timers limitados a ~1/min, por isso a folga grande.
	start := time.Now()
	gone := false
	for {
		select {
		case <-quitReq:
			if browserCmd != nil && browserCmd.Process != nil {
				browserCmd.Process.Kill()
			}
			return
		case <-browserExited:
			gone = true
			browserExited = nil
		case <-time.After(2 * time.Second):
		}
		lp := lastPing.Load()
		if lp == 0 {
			if time.Since(start) > 3*time.Minute {
				return
			}
			continue
		}
		idle := time.Now().Unix() - lp
		if (gone && idle > 8) || idle > 150 {
			return
		}
	}
}

func candidates() []string {
	var c []string
	if runtime.GOOS == "windows" {
		for _, env := range []string{"ProgramFiles(x86)", "ProgramFiles", "LocalAppData"} {
			base := os.Getenv(env)
			if base == "" {
				continue
			}
			c = append(c,
				filepath.Join(base, "Microsoft", "Edge", "Application", "msedge.exe"),
				filepath.Join(base, "Google", "Chrome", "Application", "chrome.exe"),
				filepath.Join(base, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
			)
		}
	} else {
		for _, n := range []string{"microsoft-edge", "google-chrome", "chromium", "chromium-browser"} {
			if p, err := exec.LookPath(n); err == nil {
				c = append(c, p)
			}
		}
	}
	return c
}

func openAppWindow(url string, exited chan struct{}) bool {
	profile := filepath.Join(os.TempDir(), "CyberSentinelPerfil")
	if d, err := os.UserCacheDir(); err == nil {
		profile = filepath.Join(d, "CyberSentinel")
	}
	for _, exe := range candidates() {
		if _, err := os.Stat(exe); err != nil {
			continue
		}
		cmd := exec.Command(exe,
			"--app="+url,
			"--user-data-dir="+profile,
			"--window-size=1296,759",
			"--autoplay-policy=no-user-gesture-required",
			"--no-first-run",
			"--no-default-browser-check",
			"--disable-features=Translate",
		)
		if err := cmd.Start(); err != nil {
			continue
		}
		browserCmd = cmd
		go func() { cmd.Wait(); close(exited) }()
		return true
	}
	return false
}

func openDefault(url string) {
	if runtime.GOOS == "windows" {
		exec.Command("rundll32", "url.dll,FileProtocolHandler", url).Start()
	} else {
		exec.Command("xdg-open", url).Start()
	}
}
