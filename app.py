import os
import time
import socket
import threading
import subprocess
import json
import urllib.request
import base64
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

# 👑 極輕量埠轉發器：0.0.0.0:11111 -> 127.0.0.1:11111
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
    print("=== [後台] 正在建立 Back4app 持久化網絡隧道 ===", flush=True)
    os.makedirs("/app/ts_state", exist_ok=True)
    os.makedirs("/app/ts_run", exist_ok=True)
    
    # 1. 拉起官方服務（指定使用持久化的 statedir）
    os.system("/usr/sbin/tailscaled --tun=userspace-networking --socks5-server=127.0.0.1:11111 --statedir=/app/ts_state --socket=/app/ts_run/tailscaled.sock > /dev/null 2>&1 &")
    time.sleep(3)
    
    # 2. 拉起流量橋樑
    threading.Thread(target=port_forwarding, daemon=True).start()
    
    auth_key = os.getenv("TAILSCALE_AUTHKEY", "")
    api_secret = os.getenv("TS_API_SECRET", "") 
    if not auth_key:
        print("❌ 未檢測到 TAILSCALE_AUTHKEY，終止啟動。", flush=True)
        return

    # 3. 連接 Tailscale，全面改名為 back4app-proxy
    print("🚀 發起初始網路衝鋒 [目標名稱: back4app-proxy]...", flush=True)
    os.system(f"/usr/bin/tailscale --socket=/app/ts_run/tailscaled.sock up --authkey={auth_key} --hostname=back4app-proxy --accept-dns=false")
    
    print("🚀 [智能自愈] 啟動 Back4app 專屬閉環重置監控...", flush=True)
    
    # 4. 針對 Back4app 獨立環境的奪名自愈邏輯
    for big_loop in range(1, 6):
        print(f"🔄 [大循環] 正在執行第 {big_loop} / 5 輪狀態確認...", flush=True)
        time.sleep(3)
        
        try:
            result = subprocess.run(
                ["/usr/bin/tailscale", "--socket=/app/ts_run/tailscaled.sock", "status", "--json"],
                capture_output=True, text=True, check=True
            )
            status_data = json.loads(result.stdout)
            full_status_name = status_data.get("Self", {}).get("DNSName", "").split(".")[0]
            
            if full_status_name == "back4app-proxy":
                print(f"🎉🎉🎉 【大獲全勝】本機名稱已完美鎖定為 [back4app-proxy]！", flush=True)
                break
                
            if "back4app-proxy-" in full_status_name:
                print(f"⚠️ 警報！本機當前叫: {full_status_name}。正統名字被霸佔，啟動奪名程序...", flush=True)
                
                peers = status_data.get("Peer", {})
                target_api_id = None
                for peer_id, peer_info in peers.items():
                    if peer_info.get("HostName", "") == "back4app-proxy":
                        target_api_id = peer_info.get("ID", "")
                        break
                
                if target_api_id and api_secret:
                    print(f"💥 找到老節點 ID: {target_api_id}，調用雲端 API 強制抹除...", flush=True)
                    url = f"https://api.tailscale.com/api/v2/device/{target_api_id}"
                    req = urllib.request.Request(url, method="DELETE")
                    auth_str = base64.b64encode(f":{api_secret}".encode()).decode()
                    req.add_header("Authorization", f"Basic {auth_str}")
                    
                    try:
                        with urllib.request.urlopen(req) as response:
                            if response.status in [200, 204]:
                                print("🗡️ API 擊殺成功，進入【回讀確認小循環】...", flush=True)
                    except Exception as api_err:
                        print(f"❌ API 擊殺請求異常: {str(api_err)}", flush=True)
                
                for verify_count in range(1, 7):
                    time.sleep(5)
                    v_result = subprocess.run(
                        ["/usr/bin/tailscale", "--socket=/app/ts_run/tailscaled.sock", "status", "--json"],
                        capture_output=True, text=True, check=True
                    )
                    v_status = json.loads(v_result.stdout)
                    v_peers = v_status.get("Peer", {})
                    still_exists = any(p.get("HostName", "") == "back4app-proxy" for p in v_peers.values())
                    if not still_exists:
                        print("💡 [驗證成功]：雲端老節點已徹底蒸發！", flush=True)
                        break
                
                subprocess.run(["/usr/bin/tailscale", "--socket=/app/ts_run/tailscaled.sock", "logout"], capture_output=True)
                time.sleep(3)
                os.system(f"/usr/bin/tailscale --socket=/app/ts_run/tailscaled.sock up --authkey={auth_key} --hostname=back4app-proxy --accept-dns=false")
                
        except Exception as e:
            print(f"❌ 自愈大循環執行異常: {str(e)}", flush=True)
            
    print("🏁 [限時自愈] 閉環驗證任務結束。", flush=True)

if __name__ == '__main__':
    threading.Thread(target=run_backend, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
