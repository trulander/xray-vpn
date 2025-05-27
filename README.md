# Xray VPN Server

Современный VPN сервер с маскировкой под обычный HTTPS сайт. Поддерживает множественные протоколы и транспорты.

## ⚡ Быстрый старт

### Требования
- Ubuntu/Debian сервер с публичным IP
- Docker и Docker Compose
- Домен, направленный на ваш сервер

### Развертывание

```bash
# 1. Клонирование
git clone <repository-url> xray-vpn
cd xray-vpn

# 2. Развертывание с автоматическим SSL
./deploy.sh example.com admin@example.com 203.0.113.10
```

**Готово!** Ваш VPN сервер работает на https://example.com

SSL сертификаты получаются **автоматически** через nginx-proxy + acme-companion.

## 🔧 Архитектура

```
Internet → nginx-proxy (80/443) → {
  /api/v1/vmess → xray-server:10001 (VMess WebSocket)
  /ws/vless → xray-server:10002 (VLESS WebSocket)  
  /stream/trojan → xray-server:10003 (Trojan WebSocket)
  /* → demo-website (маскировка)
}
```

### Автоматический SSL

- **nginx-proxy**: автоматически создает виртуальные хосты
- **acme-companion**: автоматически получает и обновляет SSL сертификаты
- **xray-server**: один сервер обрабатывает все протоколы (VMess, VLESS, Trojan)
- **Переменные окружения**: `VIRTUAL_HOST`, `LETSENCRYPT_HOST`, `LETSENCRYPT_EMAIL`

## 📱 Клиентские приложения

### Компьютер
- **V2rayN** (Windows)
- **V2rayU** (macOS)
- **Qv2ray** (Linux)

### Мобильные
- **V2rayNG** (Android)
- **Shadowrocket** (iOS)

### Конфигурации
После развертывания найдите файлы в `config/client/`:
- `vmess_ws.json` - VMess WebSocket
- `vless_ws.json` - VLESS WebSocket
- `trojan_ws.json` - Trojan WebSocket
- `vmess_grpc.json` - VMess gRPC
- `vless_grpc.json` - VLESS gRPC  
- `trojan_grpc.json` - Trojan gRPC

## 🛠️ Управление

```bash
# Статус сервисов
docker-compose ps

# Просмотр логов
docker-compose logs nginx-proxy
docker-compose logs acme-companion
docker-compose logs xray-server

# Перезапуск
docker-compose restart

# Остановка
docker-compose down

# Генерация новых клиентских конфигураций
docker-compose --profile tools run --rm config-generator generate-client vless ws

# Генерация URL для мобильных приложений
docker-compose --profile tools run --rm config-generator generate-client vless ws -u
```

## 🔒 Безопасность

- ✅ Маскировка под обычный HTTPS сайт
- ✅ Автоматические SSL сертификаты от Let's Encrypt
- ✅ Случайные UUID и пароли
- ✅ Рандомизированные пути и сервисы
- ✅ Fallback на реальный веб-сайт

## 🚨 Устранение неполадок

### Диагностика проблем

```bash
# Общая диагностика SSL и сервисов
./scripts/diagnose-ssl.sh

# Тестирование подключений
./scripts/test_connections.sh
```

### Проверка SSL сертификатов

```bash
# Статус nginx-proxy
docker-compose logs nginx-proxy

# Статус acme-companion
docker-compose logs acme-companion

# Проверка сертификатов
ls -la data/ssl/

# Проверка переменных окружения
docker-compose exec demo-website env | grep -E "(VIRTUAL_HOST|LETSENCRYPT)"
```

### Проверка сайта и VPN путей

```bash
# Проверка основного сайта
curl -I https://example.com

# Проверка конфигурации nginx-proxy
docker-compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf
```

### Подключение не работает
```bash
# Проверка конфигурации
docker-compose --profile tools run --rm config-generator status

# Проверка логов Xray
docker-compose logs xray-server

# Тест сайта
curl -I https://example.com
```

## 📋 Технологии

- **Xray-core** - VPN сервер с поддержкой VMess, VLESS, Trojan
- **nginx-proxy** - Автоматический reverse proxy
- **acme-companion** - Автоматические SSL сертификаты
- **Docker** - Контейнеризация
- **Let's Encrypt** - SSL сертификаты
- **Python** - Генератор конфигураций

## 📚 Документация

- [Быстрый старт](QUICK_START.md) - Краткие инструкции
- [Пример развертывания](EXAMPLE.md) - Пошаговый пример
- [Использование](USAGE.md) - Руководство пользователя
- [Шаблоны](docs/templates.md) - Кастомизация конфигураций
- [Архитектура nginx-proxy](docs/nginx-proxy-architecture.md) - Детали архитектуры

## 🔧 Скрипты

- `deploy.sh` - Основной скрипт развертывания
- `scripts/diagnose-ssl.sh` - Диагностика SSL и nginx-proxy
- `scripts/test_connections.sh` - Тестирование подключений
 