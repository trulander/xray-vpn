[en](docs/en/templates.md)

# Шаблоны конфигураций

Все конфигурации в проекте создаются на основе Jinja2-шаблонов, что делает их гибкими и удобными для настройки.

## Структура шаблонов

```
templates/
├── env_multi.j2           # Шаблон .env файла для мульти-протокола
├── xray_server_multi.json.j2    # Серверная конфигурация Xray (все протоколы)
├── client_vmess_ws.json.j2      # VMess WebSocket клиент
├── client_vless_ws.json.j2      # VLESS WebSocket клиент  
├── client_trojan_ws.json.j2     # Trojan WebSocket клиент
├── client_vmess_grpc.json.j2    # VMess gRPC клиент
├── client_vless_grpc.json.j2    # VLESS gRPC клиент
├── client_trojan_grpc.json.j2   # Trojan gRPC клиент
├── nginx_custom.conf.j2         # Кастомные location блоки для nginx-proxy
├── demo_site.conf.j2            # Конфигурация демо сайта
├── index.html.j2                # Демо веб-сайт
└── robots.txt.j2                # Файл robots.txt
```

## Переменные шаблонов

Все шаблоны используют следующие переменные:

### Основные настройки
- `domain` - доменное имя сервера (например: `example.com`)
- `server_ip` - IP адрес сервера (например: `YOUR_SERVER_IP`)
- `email` - email для SSL сертификатов (например: `admin@example.com`)

### Мульти-протокольные настройки
- `vmess_uuid` - UUID для VMess протокола (генерируется автоматически)
- `vless_uuid` - UUID для VLESS протокола (генерируется автоматически)
- `trojan_password` - пароль для Trojan протокола (генерируется автоматически)

### Пути для WebSocket
- `vmess_ws_path` - путь для VMess WebSocket (например: `/api/v1/vmess`)
- `vless_ws_path` - путь для VLESS WebSocket (например: `/ws/vless`)
- `trojan_ws_path` - путь для Trojan WebSocket (например: `/stream/trojan`)

### Настройки gRPC
- `vmess_grpc_path` - путь для VMess gRPC (например: `/vmess/grpc`)
- `vless_grpc_path` - путь для VLESS gRPC (например: `/vless/grpc`)
- `trojan_grpc_path` - путь для Trojan gRPC (например: `/trojan/grpc`)
- `vmess_grpc_service` - имя сервиса VMess gRPC (например: `VmessService`)
- `vless_grpc_service` - имя сервиса VLESS gRPC (например: `VlessService`)
- `trojan_grpc_service` - имя сервиса Trojan gRPC (например: `TrojanService`)

### Безопасность и логирование
- `log_level` - уровень логирования (по умолчанию: `warning`)
- `enable_stats` - включение статистики (по умолчанию: `false`)

## Описание шаблонов

### env_multi.j2
Генерирует файл переменных окружения `.env` со всеми настройками для мульти-протокольной архитектуры.

**Использование:**
```python
template.render(
    domain='example.com',
    server_ip='YOUR_SERVER_IP',
    email='admin@example.com',
    vmess_uuid='...',
    vless_uuid='...',
    trojan_password='...',
    # ... остальные переменные
)
```

### xray_server_multi.json.j2
Серверная конфигурация Xray с поддержкой всех протоколов:
- VMess WebSocket (порт 10001)
- VLESS WebSocket (порт 10002)
- Trojan WebSocket (порт 10003)
- VMess gRPC (порт 10011)
- VLESS gRPC (порт 10012)
- Trojan gRPC (порт 10013)

**Особенности:**
- Условное включение статистики через `{% if enable_stats %}`
- Блокировка локального трафика
- Поддержка всех современных протоколов

### Клиентские шаблоны
Клиентские конфигурации для различных протоколов и транспортов:

**WebSocket клиенты:**
- `client_vmess_ws.json.j2` - VMess WebSocket
- `client_vless_ws.json.j2` - VLESS WebSocket
- `client_trojan_ws.json.j2` - Trojan WebSocket

**gRPC клиенты:**
- `client_vmess_grpc.json.j2` - VMess gRPC
- `client_vless_grpc.json.j2` - VLESS gRPC
- `client_trojan_grpc.json.j2` - Trojan gRPC

**Особенности:**
- SOCKS5 прокси (порт 1080)
- HTTP прокси (порт 1081)
- Прямое подключение для локального трафика
- Блокировка рекламы

### nginx_custom.conf.j2
Кастомная конфигурация для nginx-proxy с:
- Location блоками для всех VPN путей (WebSocket и gRPC)
- Правильной настройкой proxy headers
- Таймаутами для WebSocket подключений
- gRPC проксированием

**Особенности:**
- Подключается к nginx-proxy как `{domain}_location` файл
- Применяется автоматически при наличии переменных окружения
- Поддерживает все протоколы и транспорты

### demo_site.conf.j2
Конфигурация демо сайта с:
- Обслуживанием статических файлов
- Заголовками безопасности для маскировки
- Обработкой ошибок
- Кэшированием статических ресурсов

**Особенности:**
- Используется контейнером `demo-website`
- Служит fallback для обычного трафика
- Имитирует обычный веб-сайт

### index.html.j2
Демо веб-сайт с:
- Современным дизайном
- Адаптивной версткой
- CSS анимациями
- Профессиональным видом

**Особенности:**
- Полностью самодостаточный HTML файл
- Встроенные стили CSS
- Не требует внешних зависимостей

### robots.txt.j2
Файл robots.txt с:
- Разрешением индексации
- Ссылкой на sitemap

## [Архитектура nginx-proxy](../../docs/ru/nginx-proxy-architecture.md)

### Как работает nginx-proxy

1. **Автоматическое обнаружение** - nginx-proxy отслеживает запуск/остановку контейнеров
2. **Генерация конфигураций** - автоматически создает виртуальные хосты на основе переменных окружения
3. **SSL сертификаты** - acme-companion автоматически получает и обновляет сертификаты

### Переменные окружения для nginx-proxy

Контейнеры должны иметь следующие переменные:

```bash
VIRTUAL_HOST=example.com        # Домен для проксирования
LETSENCRYPT_HOST=example.com    # Домен для SSL сертификата
LETSENCRYPT_EMAIL=admin@example.com  # Email для Let's Encrypt
```

### Преимущества nginx-proxy архитектуры

- Автоматизация - SSL сертификаты получаются и обновляются автоматически
- Простота - не нужно вручную настраивать Nginx и Certbot
- Надежность - проверенное решение с активной поддержкой
- Масштабируемость - легко добавлять новые домены и сервисы
- Безопасность - автоматические обновления сертификатов

## Кастомизация шаблонов

### Изменение дизайна сайта
Отредактируйте `templates/index.html.j2`:
```bash
nano templates/index.html.j2
```

### Настройка nginx-proxy
Отредактируйте `templates/nginx_custom.conf.j2`:
```bash
nano templates/nginx_custom.conf.j2
```

### Изменение конфигурации Xray
Отредактируйте `templates/xray_server_multi.json.j2`:
```bash
nano templates/xray_server_multi.json.j2
```

### Добавление новых переменных
1. Добавьте переменную в `templates/env_multi.j2`
2. Обновите метод `get_env_vars()` в `src/config_generator.py`
3. Используйте переменную в нужных шаблонах

## Регенерация после изменений

После изменения шаблонов необходимо регенерировать конфигурации:

```bash
# Регенерация всех конфигураций
docker-compose --profile tools run --rm config-generator init \
  --domain your-domain.com \
  --email your@email.com \
  --server-ip your-ip

# Перезапуск сервисов
docker-compose restart
```

## Валидация шаблонов

### JSON шаблоны
Для проверки корректности JSON шаблонов можно использовать:
```bash
# Генерация и проверка JSON
docker-compose --profile tools run --rm config-generator generate
```

### Nginx шаблоны
Для проверки конфигурации nginx-proxy:
```bash
# Проверка сгенерированной конфигурации
docker-compose exec nginx-proxy nginx -t
```

## Примеры использования

### Создание кастомного location блока
```nginx
# Добавить в templates/nginx_custom.conf.j2
location /custom/path {
    proxy_pass http://xray-server:10001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### Использование в коде
```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('nginx_custom.conf.j2')
content = template.render(domain='example.com')
```

## Отладка nginx-proxy

### Проверка переменных окружения
```bash
# Проверка переменных контейнера
docker-compose exec demo-website env | grep -E "(VIRTUAL_HOST|LETSENCRYPT)"
```

### Проверка генерируемых конфигураций
```bash
# Просмотр сгенерированных конфигураций nginx-proxy
docker-compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf
```

### Логи nginx-proxy
```bash
# Логи nginx-proxy
docker-compose logs nginx-proxy

# Логи acme-companion
docker-compose logs acme-companion
```

## Лучшие практики

1. **Не изменяйте сгенерированные файлы** - всегда редактируйте шаблоны
2. **Делайте резервные копии** кастомизированных шаблонов
3. **Тестируйте изменения** перед применением в продакшене
4. **Используйте переменные** вместо хардкода значений
5. **Документируйте изменения** в комментариях шаблонов
6. **Следите за логами** nginx-proxy и acme-companion для отладки SSL
7. **Проверяйте переменные окружения** контейнеров для корректной работы автоматизации
