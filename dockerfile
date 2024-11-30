FROM python:3.9-slim

# Instalar OpenVPN e dependências
RUN apt-get update && apt-get install -y \
    openvpn \
    curl \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar arquivo VPN e configurações
COPY vpn.ovpn /etc/openvpn/
COPY . .

# Script de inicialização
COPY start.sh .
RUN chmod +x start.sh

# Variáveis de ambiente serão definidas no Render
ENV PORT=8080

CMD ["./start.sh"]
