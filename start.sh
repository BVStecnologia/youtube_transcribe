#!/bin/sh
# Configurar DNS
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 8.8.4.4" >> /etc/resolv.conf

# Configurar VPN
echo "$PROTON_USERNAME" > /auth.txt
echo "$PROTON_PASSWORD" >> /auth.txt

# Iniciar VPN
openvpn --config /etc/openvpn/vpn.ovpn --auth-user-pass /auth.txt --daemon

# Esperar VPN iniciar
sleep 10

# Iniciar aplicação
uvicorn api:app --host 0.0.0.0 --port $PORT