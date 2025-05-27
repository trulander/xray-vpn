#!/bin/bash

set -e

echo "🚀 Автоматическое развертывание Xray VPN Server"
echo "================================================"

# Проверка аргументов
if [ $# -lt 1 ]; then
    echo "❌ Использование: $0 <домен> [email] [server-ip]"
    echo "Пример: $0 vpn.example.com admin@example.com 203.0.113.10"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-"admin@$DOMAIN"}
SERVER_IP=${3:-$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "127.0.0.1")}

echo "📋 Параметры развертывания:"
echo "   Домен: $DOMAIN"
echo "   Email: $EMAIL"
echo "   IP сервера: $SERVER_IP"
echo

# Создание директорий
echo "📁 Создание директорий..."
mkdir -p config/{xray,nginx,client} data/{www,ssl,xray/logs}

# Пересборка образа config-generator для применения исправлений
echo "🔨 Пересборка образа config-generator..."
docker-compose build config-generator

# Генерация конфигураций
echo "⚙️  Генерация конфигураций..."
docker-compose --profile tools run --rm config-generator init --domain "$DOMAIN" --email "$EMAIL" --server-ip "$SERVER_IP"

# Проверка что правильный файл создан
if [ -f "config/nginx/${DOMAIN}_location" ]; then
    echo "✅ Кастомная конфигурация создана: ${DOMAIN}_location"
else
    echo "⚠️  Кастомная конфигурация не найдена, проверьте логи"
fi

# Запуск сервисов
echo "🐳 Запуск сервисов..."
docker-compose up -d --remove-orphans

# Проверка статуса
echo "✅ Проверка статуса сервисов..."
sleep 5
docker-compose ps

echo
echo "🎉 Базовое развертывание завершено!"
echo
echo "📋 Следующие шаги:"
echo "1. Настройте DNS: $DOMAIN → IP вашего сервера"
echo "2. SSL сертификаты получатся автоматически (подождите 2-5 минут)"
echo "3. Проверьте сайт: curl -I https://$DOMAIN"
echo
echo "📊 Управление:"
echo "   - Статус: docker-compose ps"
echo "   - Логи: docker-compose logs nginx-proxy acme-companion"
echo "   - Диагностика: ./scripts/diagnose-ssl.sh"
echo "   - Тестирование: ./scripts/test_connections.sh"
echo "   - Остановка: docker-compose down" 