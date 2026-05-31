# bakc4app-wechattrans
借助bakc4app平台，搭建Tailscale转发程序，穿透微信登录限制

把上面三个文件<app.py,requirements.txt,Dockerfile>Push 到你的GitHub 新仓库后，登入Back4app 控制台执行以下配置：

创建项目：点击New App ➡️ 选择Containers (EaaS) ➡️ 连动你的GitHub 仓库。

配置环境变量(Environment Variables)：

在配置页面找到Environment Variables，添加一组：

Key :TAILSCALE_AUTHKEY

Value : （填入你在Tailscale 控制台生成的Key，建议设为Reusable 且永不过期）

配置通用设置(General Settings)：

Port : 填写8080（必须与我们代码中Flask 监听的连接埠一致，否则Back4app 会判定健康检查失败而无限重启）。

👑 最核心步骤：配置外置存储(Volumes)：

在项目设置中找到Volumes区域，点击Create Volume：

Volume Name :ts-data

Size : 选择最小值（如1 GB即可）

Mount Path (挂载路径) : 必须填写/app/ts_state

点击储存。

本地批处理唤醒bat
@echo off
chcp 65001 >nul
cls

echo ===================================================
echo 🚀 正在啟動微信專線 - Back4App 智能日間保活版
echo ===================================================

:: 【配置 1】：換成你在 Back4App 的真實公網網址
set "BACK4APP_URL=https://你的應用名.b4a.run"

:: 【配置 2】：換成你電腦上真實的微信主程序路徑
set "WECHAT_PATH=C:\Program Files\Tencent\WeChat\WeChat.exe"


echo 📡 1. 正在隔空喚醒 Back4App 容器...
curl -s -m 5 "%BACK4APP_URL%" >nul

echo ⏳ 2. 專線正在連接，請等待 15 秒讓 Tailscale 就緒...
timeout /t 15 /nobreak >nul

echo 🟢 3. 隧道已打通！正在拉起微信程序...
start "" "%WECHAT_PATH%"

echo ===================================================
echo 🛡️ 微信已啟動！腳本已切換至「日間工作保活模式」
echo 💡 請勿關閉此窗口，它將在後台每 10 分鐘自動維持專線清醒。
echo 🚪 下封鎖工直接關閉此窗口，服務將自動進入夜間休眠省額度。
echo ===================================================

:KEEP_ALIVE
:: 倒計時 600 秒（10分鐘）
timeout /t 600 /nobreak >nul
:: 悄悄請求微量保活接口
curl -s -m 5 "%BACK4APP_URL%/ping" >nul
goto KEEP_ALIVE
