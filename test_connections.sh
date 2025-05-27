#!/bin/bash

echo "=== Тестирование Xray VPN Server ==="
echo

# Проверка основного сайта
echo "1. Проверка основного сайта:"
curl -s -k -I https://localhost | head -1
echo

# Проверка HTTP редиректа
echo "2. Проверка HTTP редиректа:"
curl -s -I http://localhost | grep Location
echo

# Проверка VPN путей (должны возвращать 400 для обычных HTTP запросов)
echo "3. Проверка VPN путей:"
echo "VMess WebSocket (/api/v1/vmess):"
curl -s -k -I https://localhost/api/v1/vmess | head -1

echo "VLESS WebSocket (/ws/vless):"
curl -s -k -I https://localhost/ws/vless | head -1

echo "Trojan WebSocket (/tunnel/trojan):"
curl -s -k -I https://localhost/tunnel/trojan | head -1

echo "VMess gRPC (/vmess/grpc):"
curl -s -k -I https://localhost/vmess/grpc | head -1

echo "VLESS gRPC (/vless/grpc):"
curl -s -k -I https://localhost/vless/grpc | head -1

echo "Trojan gRPC (/trojan/grpc):"
curl -s -k -I https://localhost/trojan/grpc | head -1
echo

# Проверка статуса контейнеров
echo "4. Статус Docker контейнеров:"
docker-compose ps
echo

# Проверка логов Xray
echo "5. Последние логи Xray сервера:"
docker-compose logs --tail=5 xray-server
echo

echo "=== Тестирование завершено ==="
echo
echo "Клиентские конфигурации доступны в:"
echo "- config/client/vmess-ws.json (SOCKS порт 1080)"
echo "- config/client/vless-ws.json (SOCKS порт 1081)"
echo "- config/client/trojan-ws.json (SOCKS порт 1082)"
echo
echo "Для тестирования подключения используйте:"
echo "xray -config config/client/vmess-ws.json" 