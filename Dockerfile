FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    curl python3 python3-pip iptables \
    && curl -fsSL https://tailscale.com/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip3 install --no-cache-dir flask
COPY app.py /app/app.py
EXPOSE 8080
CMD ["python3", "app.py"]
