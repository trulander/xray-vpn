#!/bin/bash

set -e

# Проверка аргументов
if [ $# -lt 1 ]; then
    echo "❌ Использование: $0 <домен> [email]"
    echo "Пример: $0 vpn.example.com admin@example.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-"admin@$DOMAIN"}

echo "🔒 Настройка SSL сертификата для $DOMAIN"
echo "📧 Email: $EMAIL"

# Проверяем, что nginx запущен
if ! docker-compose ps nginx | grep -q "Up"; then
    echo "❌ Nginx не запущен. Запустите сначала: docker-compose up -d"
    exit 1
fi

# Создаем директорию для challenge
mkdir -p data/www/.well-known/acme-challenge

# Получаем сертификат
echo "🔄 Получение SSL сертификата от Let's Encrypt..."
docker-compose --profile tools run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/html \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --non-interactive \
    -d "$DOMAIN"

# Проверяем, что сертификат получен
if [ -f "data/ssl/live/$DOMAIN/fullchain.pem" ]; then
    echo "✅ SSL сертификат успешно получен"
    
    # Перезапускаем nginx
    echo "🔄 Перезапуск nginx..."
    docker-compose restart nginx
    
    echo "🎉 SSL настроен успешно!"
    echo "🌐 Сайт доступен по адресу: https://$DOMAIN"
else
    echo "❌ Ошибка получения SSL сертификата"
    exit 1
fi 