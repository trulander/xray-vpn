#!/bin/bash

# Тестирование генерации конфигураций Xray VPN Server

set -e

echo "🧪 Тестирование генерации конфигураций..."

# Переходим в корневую директорию проекта
cd "$(dirname "$0")/.."

# Проверяем наличие Python и зависимостей
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден"
    exit 1
fi

# Создаем тестовый .env файл
cat > .env.test << EOF
DOMAIN=test.example.com
SERVER_IP=203.0.113.10
EMAIL=admin@test.example.com
VMESS_UUID=12345678-1234-1234-1234-123456789abc
VLESS_UUID=87654321-4321-4321-4321-cba987654321
TROJAN_PASSWORD=test_password_123
VMESS_WS_PATH=/test/vmess/ws
VLESS_WS_PATH=/test/vless/ws
TROJAN_WS_PATH=/test/trojan/ws
VMESS_GRPC_PATH=/test/vmess/grpc
VLESS_GRPC_PATH=/test/vless/grpc
TROJAN_GRPC_PATH=/test/trojan/grpc
VMESS_GRPC_SERVICE=TestVmessService
VLESS_GRPC_SERVICE=TestVlessService
TROJAN_GRPC_SERVICE=TestTrojanService
LOG_LEVEL=info
ENABLE_STATS=true
UID=1000
GID=1000
EOF

# Копируем тестовый .env как основной
cp .env.test .env

echo "✅ Тестовый .env файл создан"

# Создаем тестовые директории
mkdir -p config/test/{xray,nginx,client}
mkdir -p data/test/www

echo "✅ Тестовые директории созданы"

# Тестируем генерацию конфигураций
echo "🔧 Тестирование генерации конфигураций..."

if python3 -m src.main generate; then
    echo "✅ Генерация конфигураций прошла успешно"
else
    echo "❌ Ошибка при генерации конфигураций"
    exit 1
fi

# Проверяем созданные файлы
echo "📁 Проверка созданных файлов..."

files_to_check=(
    "config/xray/config.json"
    "config/nginx/nginx.conf"
    "config/nginx/nginx_custom.conf"
    "config/nginx/demo-site.conf"
    "config/client/vmess_ws.json"
    "config/client/vless_ws.json"
    "config/client/trojan_ws.json"
    "config/client/vmess_grpc.json"
    "config/client/vless_grpc.json"
    "config/client/trojan_grpc.json"
    "data/www/index.html"
    "data/www/robots.txt"
)

missing_files=()

for file in "${files_to_check[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file"
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -eq 0 ]]; then
    echo "✅ Все файлы созданы успешно"
else
    echo "❌ Отсутствуют файлы: ${missing_files[*]}"
    exit 1
fi

# Проверяем валидность JSON файлов
echo "🔍 Проверка валидности JSON файлов..."

json_files=(
    "config/xray/config.json"
    "config/client/vmess_ws.json"
    "config/client/vless_ws.json"
    "config/client/trojan_ws.json"
    "config/client/vmess_grpc.json"
    "config/client/vless_grpc.json"
    "config/client/trojan_grpc.json"
)

for json_file in "${json_files[@]}"; do
    if python3 -c "import json; json.load(open('$json_file'))" 2>/dev/null; then
        echo "  ✅ $json_file - валидный JSON"
    else
        echo "  ❌ $json_file - невалидный JSON"
        exit 1
    fi
done

# Проверяем содержимое nginx_custom.conf
echo "🔍 Проверка nginx_custom.conf..."

if [[ -f "config/nginx/nginx_custom.conf" ]]; then
    if grep -q "location /test/vmess/ws" config/nginx/nginx_custom.conf; then
        echo "  ✅ nginx_custom.conf содержит правильные location блоки"
    else
        echo "  ❌ nginx_custom.conf не содержит ожидаемые location блоки"
        exit 1
    fi
else
    echo "  ❌ nginx_custom.conf не создан"
    exit 1
fi

# Тестируем генерацию URL
echo "🔗 Тестирование генерации URL..."

if python3 -m src.main generate-client vless ws -u; then
    echo "✅ Генерация VLESS URL прошла успешно"
else
    echo "❌ Ошибка при генерации VLESS URL"
    exit 1
fi

# Очистка
echo "🧹 Очистка тестовых файлов..."
rm -f .env.test
rm -rf config/test
rm -rf data/test

echo "🎉 Все тесты прошли успешно!"
echo ""
echo "📋 Результаты тестирования:"
echo "  ✅ Генерация конфигураций работает"
echo "  ✅ Все необходимые файлы создаются"
echo "  ✅ JSON файлы валидны"
echo "  ✅ nginx_custom.conf создается правильно"
echo "  ✅ Генерация URL работает"
echo ""
echo "🚀 Конфигурация готова к использованию!" 