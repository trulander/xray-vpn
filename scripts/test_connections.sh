#!/bin/bash

echo "🧪 Тестирование Xray VPN Server (мульти-протокольная архитектура)"
echo "================================================================="

# Загружаем переменные окружения
if [ -f .env ]; then
    source .env
    echo "📋 Конфигурация:"
    echo "   Домен: ${DOMAIN:-не задан}"
    echo "   Email: ${EMAIL:-не задан}"
else
    echo "❌ .env файл не найден"
    exit 1
fi
echo

# Проверка основного сайта
echo "1. 🌐 Проверка основного сайта:"
echo "HTTP (должен быть редирект на HTTPS):"
curl -s -I "http://localhost" 2>/dev/null | head -3 || curl -s -I "http://${DOMAIN}" 2>/dev/null | head -3 || echo "❌ HTTP недоступен"

echo "HTTPS (должен показывать демо сайт):"
curl -s -I "https://localhost" 2>/dev/null | head -3 || curl -s -I "https://${DOMAIN}" 2>/dev/null | head -3 || echo "❌ HTTPS недоступен"
echo

# Проверка VPN путей (должны возвращать ошибки для обычных HTTP запросов)
echo "2. 🔒 Проверка VPN путей (случайные пути из конфигурации):"

# Читаем конфигурацию если доступна
if [ -f "config/nginx/${DOMAIN}_location" ]; then
    echo "📄 Анализ кастомных location блоков:"
    
    # Извлекаем пути из конфигурации
    WS_PATHS=$(grep -o "location [^{]*" "config/nginx/${DOMAIN}_location" | grep -v grpc | cut -d' ' -f2)
    GRPC_PATHS=$(grep -o "location [^{]*" "config/nginx/${DOMAIN}_location" | grep grpc | cut -d' ' -f2)
    
    echo "WebSocket пути:"
    for path in $WS_PATHS; do
        if [[ "$path" != *"grpc"* ]]; then
            echo "  Testing $path:"
            curl -s -I "https://localhost$path" 2>/dev/null | head -1 || curl -s -I "https://${DOMAIN}$path" 2>/dev/null | head -1 || echo "    ❌ Путь недоступен"
        fi
    done
    
    echo "gRPC пути:"
    for path in $GRPC_PATHS; do
        echo "  Testing $path:"
        curl -s -I "https://localhost$path" 2>/dev/null | head -1 || curl -s -I "https://${DOMAIN}$path" 2>/dev/null | head -1 || echo "    ❌ Путь недоступен"
    done
else
    echo "❌ Файл конфигурации nginx не найден: config/nginx/${DOMAIN}_location"
    echo "   Тестируем стандартные пути для демонстрации:"
    
    # Примеры стандартных путей
    TEST_PATHS=(
        "/api/v1/vmess"
        "/ws/vless" 
        "/stream/trojan"
        "/vmess/grpc"
        "/vless/grpc"
        "/trojan/grpc"
    )
    
    for path in "${TEST_PATHS[@]}"; do
        echo "  Testing $path:"
        curl -s -I "https://localhost$path" 2>/dev/null | head -1 || echo "    ❌ Путь недоступен"
    done
fi
echo

# Проверка статуса Docker контейнеров
echo "3. 🐳 Статус Docker контейнеров:"
docker-compose ps
echo

# Проверка внутренних портов Xray сервера
echo "4. 🔌 Проверка внутренних портов Xray сервера:"
if docker-compose ps | grep -q "xray-server.*Up"; then
    echo "Порты WebSocket:"
    docker-compose exec nginx-proxy nc -z xray-server 10001 && echo "  ✅ VMess WS: 10001" || echo "  ❌ VMess WS: 10001"
    docker-compose exec nginx-proxy nc -z xray-server 10002 && echo "  ✅ VLESS WS: 10002" || echo "  ❌ VLESS WS: 10002"
    docker-compose exec nginx-proxy nc -z xray-server 10003 && echo "  ✅ Trojan WS: 10003" || echo "  ❌ Trojan WS: 10003"
    
    echo "Порты gRPC:"
    docker-compose exec nginx-proxy nc -z xray-server 10011 && echo "  ✅ VMess gRPC: 10011" || echo "  ❌ VMess gRPC: 10011"
    docker-compose exec nginx-proxy nc -z xray-server 10012 && echo "  ✅ VLESS gRPC: 10012" || echo "  ❌ VLESS gRPC: 10012"
    docker-compose exec nginx-proxy nc -z xray-server 10013 && echo "  ✅ Trojan gRPC: 10013" || echo "  ❌ Trojan gRPC: 10013"
else
    echo "❌ Xray сервер не запущен"
fi
echo

# Проверка переменных окружения для автоматического SSL
echo "5. 🔐 Проверка настроек автоматического SSL:"
docker-compose exec demo-website env | grep -E "(VIRTUAL_HOST|LETSENCRYPT)" || echo "❌ Переменные окружения не найдены"
echo

# Проверка сертификатов
echo "6. 📜 SSL сертификаты:"
if [ -d "data/ssl" ]; then
    cert_count=$(find data/ssl -name "*.crt" -o -name "*.pem" | wc -l)
    echo "✅ Найдено $cert_count файлов сертификатов в data/ssl/"
    
    if [ -f "data/ssl/${DOMAIN}.crt" ]; then
        echo "✅ Сертификат nginx-proxy для ${DOMAIN} найден"
    elif [ -d "data/ssl/live/${DOMAIN}" ]; then
        echo "✅ Сертификат Let's Encrypt для ${DOMAIN} найден"
    else
        echo "⚠️  Сертификат для ${DOMAIN} не найден (может получаться автоматически)"
    fi
else
    echo "❌ Папка data/ssl не существует"
fi
echo

# Проверка логов (только ошибки)
echo "7. 📋 Проверка логов на ошибки:"
echo "nginx-proxy ошибки:"
docker-compose logs nginx-proxy 2>/dev/null | grep -i error | tail -3 || echo "  ✅ Ошибок не найдено"

echo "acme-companion ошибки:"
docker-compose logs acme-companion 2>/dev/null | grep -i error | tail -3 || echo "  ✅ Ошибок не найдено"

echo "xray-server ошибки:"
docker-compose logs xray-server 2>/dev/null | grep -i error | tail -3 || echo "  ✅ Ошибок не найдено"
echo

echo "🎉 Тестирование завершено!"
echo

# Информация о секретной странице
if [ -n "$SECRET_CONFIG_PATH" ]; then
    echo "🔐 Секретная страница конфигураций:"
    echo "   https://${DOMAIN}${SECRET_CONFIG_PATH}"
    echo "   ⚠️  Эта ссылка содержит ваши персональные конфигурации VPN!"
    echo
fi

echo "📁 Клиентские конфигурации доступны в:"
if [ -d "config/client" ]; then
    ls -1 config/client/*.json 2>/dev/null | while read file; do
        echo "  📄 $file"
    done
else
    echo "  ❌ Папка config/client не найдена"
    echo "  💡 Выполните: docker-compose --profile tools run --rm config-generator generate"
fi
echo
echo "🔧 Управление:"
echo "  - Статус: docker-compose ps"
echo "  - Логи: docker-compose logs nginx-proxy acme-companion xray-server"
echo "  - Диагностика: ./scripts/diagnose-ssl.sh"
echo "  - Перезапуск: docker-compose restart"
echo
echo "📱 Для генерации URL мобильных приложений:"
echo "  docker-compose --profile tools run --rm config-generator generate-client vless ws -u" 