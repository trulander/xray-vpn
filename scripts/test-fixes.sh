#!/bin/bash

echo "🔧 Тестирование исправлений nginx-proxy"
echo "========================================"

# Проверка .env файла
if [ ! -f .env ]; then
    echo "❌ .env файл не найден!"
    echo "Создайте .env файл или запустите: ./deploy.sh your-domain.com"
    exit 1
fi

source .env
echo "📋 Найденные переменные:"
echo "   DOMAIN: ${DOMAIN:-не задан}"
echo "   EMAIL: ${EMAIL:-не задан}"
echo "   SERVER_IP: ${SERVER_IP:-не задан}"
echo

# Остановка сервисов
echo "🛑 Остановка сервисов..."
docker-compose down

# Очистка старых конфигураций nginx
echo "🧹 Очистка старых конфигураций..."
rm -f config/nginx/*_location
rm -f config/nginx/nginx_custom.conf

# Пересборка образа config-generator
echo "🔨 Пересборка образа config-generator..."
docker-compose build config-generator

# Генерация новых конфигураций
echo "⚙️  Генерация конфигураций..."
docker-compose --profile tools run --rm config-generator generate

# Проверка созданных файлов
echo "📁 Проверка созданных файлов:"
if [ -f "config/nginx/${DOMAIN}_location" ]; then
    echo "✅ Файл ${DOMAIN}_location создан"
    echo "   Размер: $(wc -l < config/nginx/${DOMAIN}_location) строк"
else
    echo "❌ Файл ${DOMAIN}_location НЕ создан"
    echo "   Содержимое config/nginx/:"
    ls -la config/nginx/ || echo "   Папка пуста"
fi

# Запуск сервисов
echo "🐳 Запуск сервисов..."
docker-compose up -d

# Ожидание запуска
echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка статуса
echo "📊 Статус сервисов:"
docker-compose ps

# Проверка переменных окружения в контейнере
echo "🔍 Проверка переменных окружения demo-website:"
docker-compose exec demo-website env | grep -E "(VIRTUAL_HOST|LETSENCRYPT)" || echo "❌ Контейнер не отвечает"

# Проверка логов nginx-proxy
echo "📜 Логи nginx-proxy (последние 5 строк):"
docker-compose logs --tail=5 nginx-proxy

echo
echo "🎯 Следующие шаги:"
echo "1. Проверьте что DNS настроен: ${DOMAIN} → IP сервера"
echo "2. Подождите получения SSL сертификатов (до 5 минут)"
echo "3. Проверьте сайт: curl -I https://${DOMAIN}"
echo "4. Для детальной диагностики: ./scripts/diagnose-ssl.sh" 