# bakc4app-wechattrans
借助bakc4app平台，搭建Tailscale转发程序，穿透微信登录限制


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
