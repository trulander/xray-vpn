#!/bin/bash

echo "🔍 Диагностика nginx-proxy и SSL сертификатов"
echo "=============================================="

# Проверка переменных окружения
echo "1. Проверка переменных окружения:"
if [ -f .env ]; then
    echo "✅ .env файл существует"
    source .env
    echo "   Домен: ${DOMAIN:-не задан}"
    echo "   Email: ${EMAIL:-не задан}"
    echo "   IP сервера: ${SERVER_IP:-не задан}"
else
    echo "❌ .env файл не найден"
fi
echo

# Проверка статуса контейнеров nginx-proxy архитектуры
echo "2. Статус контейнеров:"
docker-compose ps
echo

# Проверка переменных окружения в контейнере demo-website
echo "3. Переменные окружения demo-website:"
docker-compose exec demo-website env | grep -E "(VIRTUAL_HOST|LETSENCRYPT)" || echo "❌ Контейнер demo-website не запущен"
echo

# Проверка сертификатов в новой структуре nginx-proxy
echo "4. SSL сертификаты (nginx-proxy структура):"
if [ -d "data/ssl" ]; then
    echo "✅ Папка data/ssl существует"
    if [ -n "${DOMAIN}" ]; then
        # Проверяем структуру nginx-proxy
        if [ -f "data/ssl/${DOMAIN}.crt" ] && [ -f "data/ssl/${DOMAIN}.key" ]; then
            echo "✅ Сертификаты nginx-proxy для ${DOMAIN} найдены:"
            ls -la "data/ssl/${DOMAIN}.*" 2>/dev/null
        elif [ -d "data/ssl/live/${DOMAIN}" ]; then
            echo "✅ Сертификаты Let's Encrypt для ${DOMAIN} найдены:"
            ls -la "data/ssl/live/${DOMAIN}/" 2>/dev/null
        else
            echo "❌ Сертификаты для домена ${DOMAIN} не найдены"
            echo "   Содержимое data/ssl:"
            ls -la data/ssl/ 2>/dev/null | head -10 || echo "   Папка пуста"
        fi
    else
        echo "❌ Домен не задан в переменных окружения"
    fi
else
    echo "❌ Папка data/ssl не существует"
fi
echo

# Проверка кастомных конфигураций nginx-proxy
echo "5. Кастомные конфигурации nginx-proxy:"
if [ -n "${DOMAIN}" ] && [ -f "config/nginx/${DOMAIN}_location" ]; then
    echo "✅ Кастомная конфигурация ${DOMAIN}_location существует"
    echo "   Размер: $(wc -l < config/nginx/${DOMAIN}_location) строк"
else
    echo "❌ Кастомная конфигурация ${DOMAIN}_location не найдена"
    echo "   Содержимое config/nginx/:"
    ls -la config/nginx/ 2>/dev/null || echo "   Папка не существует"
fi
echo

# Проверка логов nginx-proxy
echo "6. Логи nginx-proxy (последние 10 строк):"
docker-compose logs --tail=10 nginx-proxy 2>/dev/null || echo "❌ Контейнер nginx-proxy не запущен"
echo

# Проверка логов acme-companion
echo "7. Логи acme-companion (последние 10 строк):"
docker-compose logs --tail=10 acme-companion 2>/dev/null || echo "❌ Контейнер acme-companion не запущен"
echo

# Проверка сгенерированной конфигурации nginx-proxy
echo "8. Сгенерированная конфигурация nginx-proxy:"
docker-compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf 2>/dev/null | head -20 || echo "❌ Не удалось получить конфигурацию"
echo

# Проверка доступности Xray сервера
echo "9. Проверка доступности Xray сервера:"
docker-compose exec nginx-proxy nc -z xray-server 10001 && echo "✅ VMess WS порт 10001 доступен" || echo "❌ VMess WS порт 10001 недоступен"
docker-compose exec nginx-proxy nc -z xray-server 10002 && echo "✅ VLESS WS порт 10002 доступен" || echo "❌ VLESS WS порт 10002 недоступен"
docker-compose exec nginx-proxy nc -z xray-server 10003 && echo "✅ Trojan WS порт 10003 доступен" || echo "❌ Trojan WS порт 10003 недоступен"
docker-compose exec nginx-proxy nc -z xray-server 10011 && echo "✅ VMess gRPC порт 10011 доступен" || echo "❌ VMess gRPC порт 10011 недоступен"
docker-compose exec nginx-proxy nc -z xray-server 10012 && echo "✅ VLESS gRPC порт 10012 доступен" || echo "❌ VLESS gRPC порт 10012 недоступен"
docker-compose exec nginx-proxy nc -z xray-server 10013 && echo "✅ Trojan gRPC порт 10013 доступен" || echo "❌ Trojan gRPC порт 10013 недоступен"
echo

# Проверка demo-website
echo "10. Проверка demo-website:"
docker-compose exec nginx-proxy nc -z demo-website 80 && echo "✅ Demo website доступен" || echo "❌ Demo website недоступен"
echo

# Проверка HTTP/HTTPS
echo "11. Проверка HTTP/HTTPS:"
echo "HTTP (должен быть редирект на HTTPS):"
curl -s -I http://localhost 2>/dev/null | head -3 || echo "❌ HTTP недоступен"
echo

echo "HTTPS:"
curl -s -I -k https://localhost 2>/dev/null | head -3 || echo "❌ HTTPS недоступен"
echo

# Проверка DNS (если домен задан)
if [ -n "${DOMAIN}" ] && [ "${DOMAIN}" != "example.com" ]; then
    echo "12. Проверка DNS:"
    echo "Резолвинг домена ${DOMAIN}:"
    nslookup "${DOMAIN}" 2>/dev/null | grep -A 1 "Name:" || dig +short "${DOMAIN}" 2>/dev/null || echo "❌ Не удалось разрезолвить домен"
    echo
fi

echo "🎯 Рекомендации для nginx-proxy архитектуры:"
echo "1. Убедитесь, что DNS настроен: ${DOMAIN} → IP сервера"
echo "2. Проверьте логи: docker-compose logs nginx-proxy acme-companion"
echo "3. Переменные окружения: VIRTUAL_HOST, LETSENCRYPT_HOST, LETSENCRYPT_EMAIL"
echo "4. SSL сертификаты получаются автоматически (подождите до 5 минут)"
echo "5. Для перезапуска: docker-compose restart"
echo "6. Кастомные location блоки: config/nginx/\${DOMAIN}_location" 