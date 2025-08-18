[en](../../docs/en/USAGE.md)

# Руководство по использованию Xray VPN Server

## Содержание

1. [Быстрый старт](#быстрый-старт)
2. [Подробная настройка](#подробная-настройка)
3. [Управление конфигурациями](#управление-конфигурациями)
4. [Настройка клиентов](#настройка-клиентов)
5. [Мониторинг и диагностика](#мониторинг-и-диагностика)
6. [Безопасность](#безопасность)
7. [Устранение неполадок](#устранение-неполадок)

## Быстрый старт

### Минимальная настройка

1. **Клонирование и инициализация**
```bash
git clone <repository-url> # Замените <repository-url> на актуальный URL вашего репозитория
cd xray-vpn
python src/main.py init --domain your-domain.com --server-ip YOUR_SERVER_IP
```

2. **Настройка домена**
```bash
# Отредактируйте .env файл (для изменения значений после первоначальной настройки)
nano .env

# Укажите ваши данные:
DOMAIN=your-domain.com
SERVER_IP=YOUR_SERVER_IP
EMAIL=your-email@example.com
```

3. **Генерация конфигураций**
```bash
python src/main.py generate
```

4. **Получение SSL сертификата**
```bash
docker-compose --profile tools run --rm certbot certonly --webroot -w /var/www/html -d your-domain.com
```

5. **Запуск сервера**
```bash
docker-compose up -d
```

6. **Создание клиентской конфигурации**
```bash
python src/main.py generate-client vless ws -u
```

## Подробная настройка

### Переменные окружения

Файл `.env` содержит все основные настройки:

```bash
# Основные настройки
DOMAIN=your-domain.com          # Ваш домен
SERVER_IP=YOUR_SERVER_IP        # IP адрес сервера
EMAIL=your-email@example.com    # Email для SSL сертификатов

# UUID для протоколов (генерируются автоматически)
VMESS_UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
VLESS_UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Пароль для Trojan (генерируется автоматически)
TROJAN_PASSWORD=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Пути для WebSocket (генерируются автоматически)
VMESS_WS_PATH=/api/v1/vmess
VLESS_WS_PATH=/ws/vless
TROJAN_WS_PATH=/tunnel/trojan

# Пути для gRPC (генерируются автоматически)
VMESS_GRPC_PATH=/vmess/grpc
VLESS_GRPC_PATH=/vless/grpc
TROJAN_GRPC_PATH=/trojan/grpc

# Сервисы для gRPC (генерируются автоматически)
VMESS_GRPC_SERVICE=VmessService
VLESS_GRPC_SERVICE=VlessService
TROJAN_GRPC_SERVICE=TrojanService

# Настройки логирования
LOG_LEVEL=warning               # debug, info, warning, error
ENABLE_STATS=false             # Включение статистики

# Docker настройки
UID=1000
GID=1000
```

### Кастомизация путей и сервисов

Вы можете изменить пути и имена сервисов для дополнительной безопасности:

```bash
# Примеры безопасных путей
VMESS_WS_PATH=/api/v2/stream
VLESS_WS_PATH=/websocket/data
TROJAN_WS_PATH=/live/updates

# Примеры имен gRPC сервисов
VMESS_GRPC_SERVICE=DataStreamService
VLESS_GRPC_SERVICE=ApiGatewayService
TROJAN_GRPC_SERVICE=NotificationService
```

## Управление конфигурациями

### Генерация конфигураций

```bash
# Генерация всех конфигураций
python src/main.py generate

# Генерация конкретной клиентской конфигурации
python src/main.py generate-client vless ws
python src/main.py generate-client vmess grpc
python src/main.py generate-client trojan ws

# Генерация с URL для мобильных приложений
python src/main.py generate-client vless ws -u
```

### Структура конфигураций

После генерации вы увидите следующую структуру файлов:

```
config/
├── xray/
│   └── config.json           # Серверная конфигурация Xray
├── nginx/
│   ├── nginx.conf           # Основная конфигурация Nginx
│   └── demo-site.conf       # Конфигурация демо сайта
└── client/
    ├── vless_ws.json        # VLESS WebSocket клиент
    ├── vless_grpc.json      # VLESS gRPC клиент
    ├── vmess_ws.json        # VMess WebSocket клиент
    ├── vmess_grpc.json      # VMess gRPC клиент
    ├── trojan_ws.json       # Trojan WebSocket клиент
    ├── trojan_grpc.json     # Trojan gRPC клиент
    └── *_url.txt            # URL для мобильных приложений
```

## Настройка клиентов

### Поддерживаемые приложения

| Платформа | Приложение | Поддерживаемые протоколы |
|-----------|------------|---------------------------|
| **Android** | v2rayNG | VMess, VLESS, Trojan |
| | SagerNet | VMess, VLESS, Trojan |
| **iOS** | Shadowrocket | VMess, VLESS, Trojan |
| | Quantumult X | VMess, VLESS |
| **Windows** | v2rayN | VMess, VLESS, Trojan |
| | Qv2ray | VMess, VLESS |
| **macOS** | V2RayXS | VMess, VLESS, Trojan |
| | Qv2ray | VMess, VLESS |
| **Linux** | v2ray | VMess, VLESS, Trojan |
| | Qv2ray | VMess, VLESS |

### Настройка через JSON конфигурацию

1. **Скопируйте конфигурацию**
```bash
cat config/client/vless_ws.json
```

2. **Импортируйте в клиент**
   - v2rayN: Servers → Add server → Import from clipboard
   - Qv2ray: Import → Import from file
   - v2rayNG: + → Import config from clipboard

### Настройка через URL

1. **Получите URL**
```bash
python src/main.py generate-client vless ws -u
cat config/client/vless_ws_url.txt
```

2. **Импортируйте URL**
   - Скопируйте URL в буфер обмена
   - В мобильном приложении: кнопка 'плюс' → Import from clipboard
   - Или отсканируйте QR код (если поддерживается)

### Ручная настройка

Если автоматический импорт не работает, настройте вручную:

**VLESS WebSocket:**
- Адрес: ваш-домен.com
- Порт: 443
- UUID: из переменной VLESS_UUID
- Шифрование: none
- Транспорт: WebSocket
- Путь: из переменной VLESS_WS_PATH
- Host: ваш-домен.com
- TLS: включен
- SNI: ваш-домен.com

**VMess gRPC:**
- Адрес: ваш-домен.com
- Порт: 443
- UUID: из переменной VMESS_UUID
- Шифрование: auto
- Транспорт: gRPC
- Сервис: из переменной VMESS_GRPC_SERVICE
- TLS: включен
- SNI: ваш-домен.com

## Мониторинг и диагностика

### Проверка статуса

```bash
# Общий статус сервера
python src/main.py status

# Статус SSL сертификатов
python src/main.py ssl-status

# Статус Docker контейнеров
docker-compose ps

# Использование ресурсов
docker stats
```

### Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f nginx
docker-compose logs -f xray-server
docker-compose logs -f demo-website

# Логи за последний час
docker-compose logs --since 1h

# Последние 100 строк
docker-compose logs --tail 100
```

### Тестирование подключения

```bash
# Проверка доступности сервера
curl -I https://ваш-домен.com

# Проверка SSL сертификата
openssl s_client -connect ваш-домен.com:443 -servername ваш-домен.com

# Проверка DNS
nslookup ваш-домен.com
dig ваш-домен.com
```

## Безопасность

### Рекомендации по безопасности

1. **Используйте сильные пароли**
2. **Настройте файрвол**
3. **Регулярно обновляйте систему**
4. **Мониторьте логи**
5. **Используйте SSH ключи**

### Настройка файрвола (UFW)

```bash
# Сброс правил
sudo ufw --force reset

# Разрешение SSH
sudo ufw allow 22

# Разрешение HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Включение файрвола
sudo ufw enable

# Проверка статуса
sudo ufw status
```

### Настройка SSH

```bash
# Генерация SSH ключа (на локальной машине)
ssh-keygen -t ed25519 -C "your-email@example.com"

# Копирование ключа на сервер
ssh-copy-id user@your-server-ip

# Отключение парольной аутентификации
sudo nano /etc/ssh/sshd_config
# Установите: PasswordAuthentication no
sudo systemctl restart ssh
```

### Обновление системы

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# Обновление Docker образов
docker-compose pull
docker-compose up -d
```

## Устранение неполадок

### Проблемы с SSL сертификатами

**Симптомы:**
- Ошибка "SSL certificate problem"
- Браузер показывает "Not secure"

**Решение:**
```bash
# Проверка статуса сертификатов
python src/main.py ssl-status

# Принудительное получение сертификата
docker-compose --profile tools run --rm certbot certonly --webroot -w /var/www/html -d ваш-домен.com --force-renewal

# Перезапуск Nginx
docker-compose restart nginx-proxy
```

### Проблемы с подключением клиентов

**Симптомы:**
- Клиент не может подключиться
- Таймауты соединения

**Диагностика:**
```bash
# Проверка доступности сервера
telnet ваш-домен.com 443

# Проверка логов Xray
docker-compose logs xray-server

# Проверка конфигурации Nginx
docker-compose exec nginx nginx -t
```

**Решение:**
1. Убедитесь, что домен указывает на ваш сервер
2. Проверьте открытость портов 80 и 443
3. Проверьте правильность конфигурации клиента
4. Попробуйте другой протокол/транспорт

### Проблемы с производительностью

**Симптомы:**
- Медленная скорость соединения
- Высокая загрузка CPU

**Диагностика:**
```bash
# Проверка загрузки системы
htop
iostat 1

# Проверка сетевой активности
iftop
ss -tuln
```

**Оптимизация:**
1. Увеличьте ресурсы сервера
2. Используйте gRPC вместо WebSocket
3. Настройте лимиты в конфигурации Xray
4. Оптимизируйте настройки Nginx

### Проблемы с Docker

**Симптомы:**
- Контейнеры не запускаются
- Ошибки при сборке

**Решение:**
```bash
# Очистка Docker
docker system prune -a

# Пересборка контейнеров
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Проверка логов
docker-compose logs
```

### Восстановление после сбоя

```bash
# Остановка всех сервисов
docker-compose down

# Резервное копирование конфигураций
cp -r config config.backup
cp .env .env.backup

# Регенерация конфигураций
python src/main.py generate

# Запуск сервисов
docker-compose up -d
```

## Получение помощи

Если проблема не решается:

1. **Проверьте логи:** `docker-compose logs`
2. **Проверьте статус:** `python src/main.py status`
3. **Проверьте документацию:** [Xray Documentation](https://xtls.github.io/)
4. **Проверьте сетевые настройки:** DNS, файрвол, порты

## Регулярное обслуживание

### Еженедельно
- Проверка логов на ошибки
- Мониторинг использования ресурсов
- Проверка статуса SSL сертификатов

### Ежемесячно
- Обновление системы и Docker образов
- Резервное копирование конфигураций
- Проверка безопасности

### По необходимости
- Ротация ключей и паролей
- Изменение путей и сервисов
- Масштабирование ресурсов