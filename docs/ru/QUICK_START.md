[en](../../docs/en/QUICK_START.md)

## Быстрый старт

## Автоматическое развертывание с SSL

```bash
# 1. Клонирование репозитория (замените <repository-url> на актуальный URL вашего репозитория)
git clone <repository-url> xray-vpn
cd xray-vpn

# 2. Запуск развертывания
./deploy.sh example.com admin@example.com 203.0.113.10
```

**Готово!** SSL-сертификаты выдаются и обновляются автоматически.

## Что происходит

1. **nginx-proxy** автоматически создает виртуальные хосты
2. **acme-companion** автоматически получает SSL сертификаты
3. **xray-server** запускается и обрабатывает все протоколы (VMess, VLESS, Trojan)
4. **demo-website** служит маскировкой

## Проверка работы

```bash
# Статус сервисов
docker-compose ps

# Проверка SSL
curl -I https://example.com

# Логи
docker-compose logs nginx-proxy
docker-compose logs acme-companion
```

## Клиентские конфигурации

После развертывания найдите файлы в `config/client/`:
- `vmess_ws.json` - VMess WebSocket
- `vless_ws.json` - VLESS WebSocket  
- `trojan_ws.json` - Trojan WebSocket

## Преимущества nginx-proxy

- Автоматический SSL - сертификаты получаются и обновляются автоматически
- Нет проблемы "курицы и яйца" - nginx-proxy запускается без SSL, затем получает сертификаты
- Простота - не нужно вручную настраивать nginx и certbot
- Надежность - проверенное решение с активной поддержкой

## Устранение неполадок

```bash
# Если что-то не работает
docker-compose down
docker-compose up -d

# Проверка переменных окружения
docker-compose exec demo-website env | grep -E "(VIRTUAL_HOST|LETSENCRYPT)"
```

## Готово!

Ваш VPN сервер готов к работе:

- **Сайт:** https://vpn.example.com
- **Клиентские конфигурации:** `config/client/`
- **Поддерживаемые протоколы:** VMess, VLESS, Trojan (WebSocket + gRPC)

## Клиентские приложения

### Для компьютера
- **V2rayN** (Windows)
- **V2rayU** (macOS) 
- **Qv2ray** (Linux)

### Для мобильных
- **V2rayNG** (Android)
- **Shadowrocket** (iOS)

Используйте файлы из папки `config/client/`:
- `vmess_ws.json` - VMess WebSocket
- `vless_ws.json` - VLESS WebSocket  
- `trojan_ws.json` - Trojan WebSocket

## Управление

```bash
# Статус сервисов
docker-compose ps

# Просмотр логов
docker-compose logs xray-server

# Перезапуск
docker-compose restart

# Остановка
docker-compose down
```

## Устранение неполадок

### Проблемы с SSL
```bash
# Проверка статуса сертификата
docker-compose --profile tools run --rm config-generator ssl-status

# Принудительное обновление сертификата
docker-compose --profile tools run --rm certbot renew --force-renewal
docker-compose restart nginx-proxy
```

### Проблемы с подключением
```bash
# Проверка конфигурации
docker-compose --profile tools run --rm config-generator status

# Проверка логов Xray
docker-compose logs xray-server

# Тест подключения
curl -I https://vpn.example.com
```

## Безопасность

- Все UUID и пароли генерируются случайно
- Пути WebSocket и имена gRPC сервисов рандомизированы
- VPN трафик маскируется под обычный HTTPS
- Fallback на реальный веб-сайт для обычного трафика