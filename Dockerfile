FROM ubuntu:22.04

# 避免交互式安裝彈窗打斷構建
ENV DEBIAN_FRONTEND=noninteractive

# 安裝基礎依賴、Python 以及官方 Tailscale
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    iptables \
    && curl -fsSL https://tailscale.com/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# 設置工作目錄
WORKDIR /app

# 安裝輕量 Web 框架 Flask
RUN pip3 install --no-cache-dir flask

# 將代碼複製到容器中
COPY app.py /app/app.py

# 暴露 Flask 的健康檢查埠（注意：Back4app 對外只看這個 Web 埠）
EXPOSE 8080

# 啟動命令
CMD ["python3", "app.py"]
