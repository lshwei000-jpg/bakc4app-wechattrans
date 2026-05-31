import os
import time
import socket
import threading
from flask import Flask, render_template_string

app = Flask(__name__)

# 🎭 網頁偽裝：假裝是一個極其普通的個人待辦事項網頁
MOCK_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>My Personal Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; padding: 50px; color: #333; }
        .container { max-width: 500px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin: 0 auto; }
        h2 { color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }
        ul { list-style: none; padding: 0; }
        li { padding: 12px; background: #fafafa; margin-bottom: 8px; border-left: 4px solid #3498db; border-radius: 3px; font-size: 14px; }
        .time { font-size: 12px; color: #95a5a6; text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📋 Daily Todo List</h2>
        <ul>
            <li>✅ Review project design specifications</li>
            <li>📌 Sync network documentation with team</li>
            <li>📝 Optimize backend database query index</li>
            <li>⏳ Backup local workplace environment server</li>
        </ul>
        <div class="time">System status: Normal | Sync time: Auto</div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(MOCK_HTML), 200

@app.route('/ping')
def ping():
    return "pong", 200

# 👑 輕量埠轉發器：將外部 11111 流量安全橋接到內部的 11112 
def port_forwarding():
    print("🔌 [橋樑] 埠轉發線程已啟動...", flush=True)
    while True:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('0.0.0.0', 11111))
            server.listen(100)
            print("🟢 [橋樑] 成功監聽 0.0.0.0:11111 端口！", flush=True)
            break
        except Exception as e:
            print(f"⚠️ [橋樑] 綁定 11111 失敗: {e}，5秒後重試...", flush=True)
            server.close()
            time.sleep(5)

    while True:
        try:
            local_conn, addr = server.accept()
            remote_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_conn.connect(('127.0.0.1', 11112)) # 導向內部真正的 Socks5
            
            def pipe(src, dst):
                try:
                    while True:
                        data = src.recv(4096)
                        if not data: break
                        dst.sendall(data)
                except: pass
                finally:
                    src.close()
                    dst.close()
            
            threading.Thread(target=pipe, args=(local_conn, remote_conn), daemon=True).start()
            threading.Thread(target=pipe, args=(remote_conn, local_conn), daemon=True).start()
        except Exception:
            time.sleep(1)

def run_backend():
    print("=== [後台] 正在建立 Back4app 持久化網絡隧道 ===", flush=True)
    os.makedirs("/app/ts_state", exist_ok=True)
    os.makedirs("/app/ts_run", exist_ok=True)
    
    # 1. 拉起官方服務（讓官方 Socks5 監聽 11112，徹底避開與轉發器的 11111 衝突）
    os.system("/usr/sbin/tailscaled --tun=userspace-networking --socks5-server=127.0.0.1:11112 --statedir=/app/ts_state --socket=/app/ts_run/tailscaled.sock > /dev/null 2>&1 &")
    time.sleep(3)
    
    # 2. 拉起流量橋樑
    threading.Thread(target=port_forwarding, daemon=True).start()
    
    auth_key = os.getenv("TAILSCALE_AUTHKEY", "")
    if not auth_key:
        print("❌ 未檢測到 TAILSCALE_AUTHKEY，終止啟動。", flush=True)
        return

    # 3. 連接 Tailscale（名字固定為 back4app-proxy，有持久化存儲，重啟也是這個名字）
    print("🚀 正在啟動/恢復 Tailscale 網絡連接...", flush=True)
    os.system(f"/usr/bin/tailscale --socket=/app/ts_run/tailscaled.sock up --authkey={auth_key} --hostname=back4app-proxy --accept-dns=false")
    print("🏁 Tailscale 網絡已完全就緒！", flush=True)

if __name__ == '__main__':
    threading.Thread(target=run_backend, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
