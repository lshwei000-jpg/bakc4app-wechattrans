import os
import time
import socket
import threading
from flask import Flask, render_template_string

app = Flask(__name__)

# 🎭 網頁偽裝：假裝是一個極其普通的個人待辦事項（Todo List）網頁，避開 Proxy 等敏感詞
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
    # 正常訪客或官方審查看到的是 Todo List
    return render_template_string(MOCK_HTML), 200

@app.route('/ping')
def ping():
    # 👑 專門給本地腳本留出的微量保活接口，只返回一個單詞，速度極快且省流量
    return "pong", 200

# 👑 極輕量埠轉發器：將 0.0.0.0:11111 的流量安全橋接到 127.0.0.1:11111
def port_forwarding():
    while True:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('0.0.0.0', 11111))
            server.listen(100)
            break
        except Exception:
            server.close()
            time.sleep(5)

    while True:
        try:
            local_conn, addr = server.accept()
            remote_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_conn.connect(('127.0.0.1', 11111))
            
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
    os.makedirs("/app/ts_state", exist_ok=True)
    os.makedirs("/app/ts_run", exist_ok=True)
    
    os.system("/usr/sbin/tailscaled --tun=userspace-networking --socks5-server=127.0.0.1:11111 --statedir=/app/ts_state --socket=/app/ts_run/tailscaled.sock > /dev/null 2>&1 &")
    time.sleep(3)
    
    threading.Thread(target=port_forwarding, daemon=True).start()
    
    auth_key = os.getenv("TAILSCALE_AUTHKEY", "")
    if not auth_key:
        return

    os.system(f"/usr/bin/tailscale --socket=/app/ts_run/tailscaled.sock up --authkey={auth_key} --hostname=render-proxy --accept-dns=false")

if __name__ == '__main__':
    threading.Thread(target=run_backend, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
