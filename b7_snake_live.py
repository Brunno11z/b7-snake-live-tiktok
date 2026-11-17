#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
🐍 B7 GAMES • COBRINHA 2.5D INTERATIVA TIKTOK LIVE (EULERSTREAM API)
====================================================================
Servidor Python Localhost para Jogos Interativos no TikTok Live
- Conexão nativa com EulerStream API (WebSockets e Webcast)
- Painel Web B7 GAMES (Azul Royal Neon)
- Transmissão em tempo real de presentes (Maçã / Bomba) via SSE
- Compatível 100% com OBS Studio (Browser Source 9:16)
- Sons de Maçã (Crunch) e Bomba (Explosão) integrados
====================================================================
"""

import os
import sys
import json
import time
import socket
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'b7_config.json')

DEFAULT_CONFIG = {
    "username": "@b7games",
    "euler_api_key": "",
    "sound_enabled": True,
    "sound_volume": 0.85,
    "auto_ia": True,
    "goal": 100,
    "gifts": [
        {"id": "g1", "name": "Rosa", "emoji": "🌹", "img": None, "qty": 1, "type": "bomb", "gift_id": 5655},
        {"id": "g2", "name": "Buquê", "emoji": "💐", "img": None, "qty": 10, "type": "apple", "gift_id": 5658},
        {"id": "g3", "name": "Caixa", "emoji": "🎁", "img": None, "qty": 20, "type": "apple", "gift_id": 5660},
        {"id": "g4", "name": "Donut", "emoji": "🍩", "img": None, "qty": 30, "type": "bomb", "gift_id": 5827},
        {"id": "g5", "name": "Luvas", "emoji": "🥊", "img": None, "qty": 300, "type": "apple", "gift_id": 6064}
    ]
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {**DEFAULT_CONFIG, **data}
        except Exception as e:
            print(f"[AVISO] Erro ao carregar {CONFIG_FILE}: {e}")
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERRO] Falha ao salvar configuração: {e}")

# Gerenciador global de eventos em tempo real (SSE)
class EventBroker:
    def __init__(self):
        self.clients = []
        self.lock = threading.Lock()

    def add_client(self, client):
        with self.lock:
            self.clients.append(client)

    def remove_client(self, client):
        with self.lock:
            if client in self.clients:
                self.clients.remove(client)

    def broadcast(self, event_type, data):
        payload = f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
        with self.lock:
            dead_clients = []
            for client in self.clients:
                try:
                    client.wfile.write(payload.encode('utf-8'))
                    client.wfile.flush()
                except Exception:
                    dead_clients.append(client)
            for dc in dead_clients:
                if dc in self.clients:
                    self.clients.remove(dc)

broker = EventBroker()

# Estado da Conexão TikTok Live
live_state = {
    "connected": False,
    "username": "",
    "status": "Desconectado",
    "viewers": 0,
    "diamonds": 0,
    "last_gift": None,
    "euler_connected": False
}

# Gerenciador de conexão com a Live via EulerStream API
class TikTokLiveEulerWorker:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self, username, euler_key):
        self.stop()
        self.running = True
        self.thread = threading.Thread(target=self._run, args=(username, euler_key), daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        live_state["connected"] = False
        live_state["status"] = "Desconectado"
        broker.broadcast("live_status", live_state)

    def _run(self, username, euler_key):
        clean_user = username.strip().lstrip('@')
        if not clean_user:
            live_state["status"] = "Erro: Usuário não informado"
            broker.broadcast("live_status", live_state)
            return

        live_state["username"] = clean_user
        live_state["status"] = "Conectando ao TikTok Live..."
        broker.broadcast("live_status", live_state)

        # Tentativa 1: Biblioteca TikTokLive oficial com EulerStream API Key
        try:
            from TikTokLive import TikTokLiveClient
            from TikTokLive.client.web.web_settings import WebDefaults
            from TikTokLive.events import ConnectEvent, GiftEvent, CommentEvent, LikeEvent, DisconnectEvent

            if euler_key:
                WebDefaults.tiktok_sign_api_key = euler_key
                print(f"[EULER] Configurada chave de assinatura EulerStream para @{clean_user}")

            client = TikTokLiveClient(unique_id=f"@{clean_user}")

            @client.on(ConnectEvent)
            async def on_connect(event: ConnectEvent):
                live_state["connected"] = True
                live_state["euler_connected"] = bool(euler_key)
                live_state["status"] = f"Ao Vivo: @{clean_user}"
                broker.broadcast("live_status", live_state)
                print(f"[TIKTOK] Conectado à Live de @{clean_user}!")

            @client.on(GiftEvent)
            async def on_gift(event: GiftEvent):
                gift_name = getattr(event.gift, 'name', '') or getattr(event.gift, 'describe', '')
                repeat_count = getattr(event, 'repeat_count', 1) or 1
                sender = getattr(event.user, 'unique_id', 'Anônimo')
                diamonds = getattr(event.gift, 'diamond_count', 1) or 1
                avatar = getattr(event.user.avatar, 'urls', [''])[0] if hasattr(event.user, 'avatar') else None

                print(f"[PRESENTE] {sender} enviou {gift_name} x{repeat_count} ({diamonds} 💎)")
                
                # Mapeia para configuração salva
                cfg = load_config()
                matched_gift = None
                for g in cfg.get("gifts", []):
                    if g["name"].lower() in gift_name.lower() or gift_name.lower() in g["name"].lower():
                        matched_gift = g
                        break

                gift_type = matched_gift["type"] if matched_gift else ("bomb" if "rosa" in gift_name.lower() else "apple")
                base_qty = matched_gift["qty"] if matched_gift else 1
                total_qty = base_qty * repeat_count

                event_data = {
                    "id": matched_gift["id"] if matched_gift else "custom",
                    "name": gift_name,
                    "emoji": matched_gift.get("emoji", "🎁") if matched_gift else "🎁",
                    "img": matched_gift.get("img") if matched_gift else avatar,
                    "qty": total_qty,
                    "type": gift_type,
                    "user": sender,
                    "diamonds": diamonds * repeat_count
                }
                live_state["diamonds"] += diamonds * repeat_count
                live_state["last_gift"] = event_data
                broker.broadcast("gift", event_data)
                broker.broadcast("live_status", live_state)

            @client.on(CommentEvent)
            async def on_comment(event: CommentEvent):
                comment_data = {
                    "user": getattr(event.user, 'unique_id', 'Espectador'),
                    "comment": getattr(event, 'comment', '')
                }
                broker.broadcast("comment", comment_data)

            @client.on(DisconnectEvent)
            async def on_disconnect(event: DisconnectEvent):
                live_state["connected"] = False
                live_state["status"] = "Desconectado"
                broker.broadcast("live_status", live_state)

            client.run()
            return
        except ImportError:
            print("[INFO] Biblioteca TikTokLive não instalada. Tentando conexão WebSocket direta com EulerStream...")
        except Exception as e:
            print(f"[ERRO TikTokLive] {e}. Tentando fallback WebSocket EulerStream...")

        # Tentativa 2: Conexão Direta WebSocket com EulerStream (wss://ws.eulerstream.com)
        try:
            import websocket  # pip install websocket-client
            import ssl

            ws_url = f"wss://ws.eulerstream.com?uniqueId={clean_user}"
            if euler_key:
                ws_url += f"&apiKey={euler_key}"

            print(f"[EULER] Conectando diretamente ao WebSocket EulerStream: {ws_url}")

            def on_message(ws, message):
                try:
                    payload = json.loads(message)
                    evt_type = payload.get("event")
                    data = payload.get("data", {})
                    if evt_type == "gift":
                        broker.broadcast("gift", data)
                    elif evt_type == "comment":
                        broker.broadcast("comment", data)
                except Exception as ex:
                    print(f"[EULER WS ERRO MSG] {ex}")

            def on_open(ws):
                live_state["connected"] = True
                live_state["euler_connected"] = True
                live_state["status"] = f"Conectado EulerStream: @{clean_user}"
                broker.broadcast("live_status", live_state)

            def on_close(ws, close_status_code, close_msg):
                live_state["connected"] = False
                live_state["status"] = "Desconectado"
                broker.broadcast("live_status", live_state)

            ws = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message,
                on_close=on_close
            )
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            return
        except ImportError:
            print("[INFO] websocket-client não instalado. Operando em modo Servidor Local com simulador ativo.")
        except Exception as e:
            print(f"[ERRO EULER WS] {e}")

        # Se não houver bibliotecas externas instaladas, permanece em modo Simulação ativo
        live_state["connected"] = False
        live_state["status"] = "Modo Teste / Simulação Ativo"
        broker.broadcast("live_status", live_state)

euler_worker = TikTokLiveEulerWorker()

# Handler HTTP do Servidor B7 GAMES
class B7HTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silencia logs de requisições repetitivas
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Rota SSE para sincronização em tempo real
        if path == '/events':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            broker.add_client(self)
            # Envia status inicial
            init_msg = f"event: live_status\ndata: {json.dumps(live_state, ensure_ascii=False)}\n\n"
            try:
                self.wfile.write(init_msg.encode('utf-8'))
                self.wfile.flush()
                while True:
                    time.sleep(15)
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
            except Exception:
                broker.remove_client(self)
            return

        # Rota de Configuração
        if path == '/api/config':
            self.send_json(200, load_config())
            return

        # Rota de Status
        if path == '/api/status':
            self.send_json(200, live_state)
            return

        # Rota para OBS Studio (Tela 100% limpa vertical)
        if path == '/game':
            self.serve_index(obs_mode=True)
            return

        # Rota Principal (Painel Completo + Jogo)
        if path in ('/', '/index.html', '/painel'):
            self.serve_index(obs_mode=False)
            return

        # Caso tente acessar outro arquivo local
        safe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path.lstrip('/'))
        if os.path.isfile(safe_path):
            self.serve_file(safe_path)
            return

        self.send_error(404, "Arquivo não encontrado")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_len = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else '{}'
        
        try:
            body = json.loads(post_data) if post_data else {}
        except Exception:
            body = {}

        if path == '/api/config':
            cfg = load_config()
            cfg.update(body)
            save_config(cfg)
            broker.broadcast("config_updated", cfg)
            self.send_json(200, {"ok": True, "config": cfg})
            return

        if path == '/api/trigger_gift':
            # Dispara presente manualmente pelo Painel B7
            broker.broadcast("gift", body)
            self.send_json(200, {"ok": True, "triggered": body})
            return

        if path == '/api/toggle_ai':
            enabled = body.get("enabled", True)
            cfg = load_config()
            cfg["auto_ia"] = enabled
            save_config(cfg)
            broker.broadcast("toggle_ai", {"enabled": enabled})
            self.send_json(200, {"ok": True, "enabled": enabled})
            return

        if path == '/api/connect':
            user = body.get("username", "")
            key = body.get("euler_api_key", "")
            cfg = load_config()
            if user: cfg["username"] = user
            if key: cfg["euler_api_key"] = key
            save_config(cfg)
            euler_worker.start(user, key)
            self.send_json(200, {"ok": True, "status": "Iniciando conexão..."})
            return

        if path == '/api/disconnect':
            euler_worker.stop()
            self.send_json(200, {"ok": True, "status": "Desconectado"})
            return

        if path == '/api/reset':
            broker.broadcast("reset_game", {})
            self.send_json(200, {"ok": True})
            return

        self.send_error(404, "Endpoint não encontrado")

    def send_json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def serve_index(self, obs_mode=False):
        index_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
        if not os.path.exists(index_file):
            self.send_error(500, "Arquivo index.html não encontrado")
            return
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if obs_mode:
            content = content.replace('<body>', '<body class="obs-mode">')

        data = content.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def serve_file(self, filepath):
        with open(filepath, 'rb') as f:
            data = f.read()
        self.send_response(200)
        ext = os.path.splitext(filepath)[1].lower()
        content_types = {
            '.html': 'text/html; charset=utf-8',
            '.css': 'text/css; charset=utf-8',
            '.js': 'application/javascript; charset=utf-8',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.json': 'application/json'
        }
        self.send_header('Content-Type', content_types.get(ext, 'application/octet-stream'))
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

def run_server(port=8765):
    server = HTTPServer(('0.0.0.0', port), B7HTTPHandler)
    url = f"http://127.0.0.1:{port}"
    print("=" * 65)
    print(" 🐍 B7 GAMES • COBRINHA 2.5D INTERATIVA TIKTOK LIVE")
    print(f" 🌐 Painel do Jogo:    {url}")
    print(f" 🎬 Link OBS Studio:   {url}/game")
    print("=" * 65)
    print(" Pressione Ctrl + C para encerrar o servidor.")
    
    # Abre o navegador automaticamente
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[B7 GAMES] Servidor encerrado com sucesso.")
        server.server_close()

if __name__ == '__main__':
    port = 8765
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
