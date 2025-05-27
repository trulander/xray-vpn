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
else
    echo "❌ .env файл не найден"
fi
echo

# Проверка статуса контейнеров
echo "2. Статус контейнеров:"
docker-compose ps
echo

# Проверка переменных окружения в контейнерах
echo "3. Переменные окружения demo-website:"
docker-compose exec demo-website env | grep -E "(VIRTUAL_HOST|LETSENCRYPT)" || echo "❌ Контейнер не запущен"
echo

# Проверка сертификатов
echo "4. SSL сертификаты:"
if [ -d "data/ssl" ]; then
    echo "✅ Папка data/ssl существует"
    if [ -n "${DOMAIN}" ] && [ -d "data/ssl/live/${DOMAIN}" ]; then
        echo "✅ Сертификаты для ${DOMAIN} найдены:"
        ls -la "data/ssl/live/${DOMAIN}/" 2>/dev/null || echo "❌ Папка пуста"
    else
        echo "❌ Сертификаты для домена ${DOMAIN} не найдены"
        echo "   Содержимое data/ssl:"
        find data/ssl -name "*.pem" 2>/dev/null || echo "   Сертификаты не найдены"
    fi
else
    echo "❌ Папка data/ssl не существует"
fi
echo

# Проверка конфигураций nginx-proxy
echo "5. Конфигурации nginx-proxy:"
if [ -f "config/nginx/${DOMAIN}_location" ]; then
    echo "✅ Кастомная конфигурация ${DOMAIN}_location существует"
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
docker-compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf 2>/dev/null || echo "❌ Не удалось получить конфигурацию"
echo

# Проверка доступности Xray сервера
echo "9. Проверка доступности Xray сервера:"
docker-compose exec nginx-proxy nc -z xray-server 10001 && echo "✅ Порт 10001 доступен" || echo "❌ Порт 10001 недоступен"
docker-compose exec nginx-proxy nc -z xray-server 10002 && echo "✅ Порт 10002 доступен" || echo "❌ Порт 10002 недоступен"
docker-compose exec nginx-proxy nc -z xray-server 10003 && echo "✅ Порт 10003 доступен" || echo "❌ Порт 10003 недоступен"
echo

# Проверка HTTP/HTTPS
echo "10. Проверка HTTP/HTTPS:"
echo "HTTP (должен быть редирект):"
curl -I http://localhost 2>/dev/null | head -3 || echo "❌ HTTP недоступен"

echo "HTTPS:"
curl -I -k https://localhost 2>/dev/null | head -3 || echo "❌ HTTPS недоступен"
echo

echo "🎯 Рекомендации:"
echo "1. Убедитесь, что DNS настроен: ${DOMAIN} → IP сервера"
echo "2. Проверьте логи: docker-compose logs nginx-proxy acme-companion"
echo "3. Перезапустите сервисы: docker-compose restart"
echo "4. Если сертификаты не получены, подождите несколько минут" 