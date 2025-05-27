# Архитектура nginx-proxy + acme-companion

## Обзор

В проекте используется связка nginx-proxy + acme-companion для автоматического управления SSL сертификатами и проксирования трафика.

## Компоненты

### 1. nginx-proxy
**Контейнер:** `nginxproxy/nginx-proxy:latest`

**Функции:**
- Автоматически обнаруживает контейнеры с переменной `VIRTUAL_HOST`
- Генерирует виртуальные хосты для каждого домена
- Проксирует трафик на соответствующие контейнеры
- Обрабатывает SSL терминацию

**Как работает:**
1. Отслеживает Docker события через `/var/run/docker.sock`
2. Находит контейнеры с `VIRTUAL_HOST=example.com`
3. Автоматически создает nginx конфигурацию
4. Проксирует весь трафик на этот контейнер

### 2. acme-companion
**Контейнер:** `nginxproxy/acme-companion:latest`

**Функции:**
- Автоматически получает SSL сертификаты от Let's Encrypt
- Обновляет сертификаты каждые 12 часов
- Интегрируется с nginx-proxy

**Как работает:**
1. Отслеживает контейнеры с `LETSENCRYPT_HOST=example.com`
2. Использует ACME challenge через HTTP-01
3. Сохраняет сертификаты в `/etc/nginx/certs`
4. Перезагружает nginx-proxy при обновлении

## Переменные окружения

### Обязательные для контейнеров:
```bash
VIRTUAL_HOST=example.com        # Домен для nginx-proxy
LETSENCRYPT_HOST=example.com    # Домен для SSL сертификата
LETSENCRYPT_EMAIL=admin@example.com  # Email для Let's Encrypt
```

### Настройки nginx-proxy:
```bash
DEFAULT_HOST=example.com        # Домен по умолчанию
TRUST_DOWNSTREAM_PROXY=false   # Не доверять заголовкам от proxy
```

## Структура файлов

### Сертификаты
```
data/ssl/
├── live/
│   └── example.com/
│       ├── fullchain.pem      # Полная цепочка сертификатов
│       ├── privkey.pem        # Приватный ключ
│       ├── cert.pem           # Основной сертификат
│       └── chain.pem          # Промежуточные сертификаты
└── accounts/                  # Аккаунты Let's Encrypt
```

### Кастомные конфигурации
```
config/nginx/
├── example.com_location       # Кастомные location блоки для домена
├── example.com_server         # Кастомные server настройки для домена
└── example.com               # Полная замена виртуального хоста
```

## Кастомизация

### Добавление location блоков

Файл `config/nginx/example.com_location`:
```nginx
# VPN маршруты
location /api/v1/vmess {
    proxy_pass http://xray-server:10001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### Добавление server настроек

Файл `config/nginx/example.com_server`:
```nginx
# Дополнительные настройки сервера
client_max_body_size 50M;
proxy_read_timeout 300s;
```

### Полная замена виртуального хоста

Файл `config/nginx/example.com`:
```nginx
server {
    listen 443 ssl http2;
    server_name example.com;
    
    # Полная кастомная конфигурация
}
```

## Автоматические процессы

### Получение сертификатов
1. **Первый запуск:** acme-companion обнаруживает `LETSENCRYPT_HOST`
2. **HTTP challenge:** Создает временный файл в `/.well-known/acme-challenge/`
3. **Проверка:** Let's Encrypt проверяет файл через HTTP
4. **Сертификат:** Сохраняется в `data/ssl/live/domain/`
5. **Reload:** nginx-proxy перезагружается с новыми сертификатами

### Обновление сертификатов
- **Автоматически:** Каждые 12 часов
- **Проверка:** За 30 дней до истечения
- **Обновление:** Если срок истекает менее чем через 30 дней
- **Перезагрузка:** nginx-proxy автоматически перезагружается

## Troubleshooting

### Сертификаты не получаются

1. **Проверить DNS:** Домен должен указывать на сервер
2. **Проверить порт 80:** Должен быть доступен извне
3. **Проверить логи:** `docker-compose logs acme-companion`
4. **Проверить переменные:** `LETSENCRYPT_HOST` должен совпадать с `VIRTUAL_HOST`

### HTTPS не работает (502 ошибка)

1. **Проверить статус контейнеров:** `docker-compose ps`
2. **Проверить кастомные конфигурации:** Файлы в `config/nginx/`
3. **Проверить логи nginx-proxy:** `docker-compose logs nginx-proxy`
4. **Проверить доступность backend:** nginx-proxy должен достучаться до контейнера

### Кастомные location не работают

1. **Правильное имя файла:** `{domain}_location`
2. **Правильный синтаксис:** Валидная nginx конфигурация
3. **Перезапуск:** `docker-compose restart nginx-proxy`
4. **Проверка монтирования:** Volume должен быть подключен

## Логи и мониторинг

### Просмотр логов
```bash
# nginx-proxy
docker-compose logs nginx-proxy

# acme-companion
docker-compose logs acme-companion

# Все сразу
docker-compose logs nginx-proxy acme-companion
```

### Проверка сгенерированных конфигураций
```bash
# Основная конфигурация
docker-compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf

# Кастомные конфигурации
docker-compose exec nginx-proxy ls -la /etc/nginx/vhost.d/

# Сертификаты
docker-compose exec nginx-proxy ls -la /etc/nginx/certs/
```

## Преимущества подхода

- ✅ **Автоматизация:** SSL сертификаты получаются и обновляются автоматически
- ✅ **Простота:** Не нужно настраивать nginx вручную
- ✅ **Надежность:** Проверенное решение с активной поддержкой
- ✅ **Масштабируемость:** Легко добавлять новые домены
- ✅ **Безопасность:** Современные SSL настройки по умолчанию

## Ограничения

- ❌ **HTTP-01 challenge:** Требует доступности порта 80
- ❌ **Wildcard сертификаты:** Нужен DNS-01 challenge (более сложная настройка)
- ❌ **Кастомизация:** Ограниченные возможности настройки nginx
- ❌ **Зависимость:** От Docker socket и интернет-соединения 