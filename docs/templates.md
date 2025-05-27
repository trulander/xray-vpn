# Шаблоны конфигураций

Все конфигурации в проекте генерируются из Jinja2 шаблонов, что обеспечивает гибкость и удобство настройки.

## Структура шаблонов

```
templates/
├── env.j2                 # Шаблон .env файла
├── xray_server.json.j2    # Серверная конфигурация Xray
├── xray_client.json.j2    # Клиентская конфигурация Xray
├── nginx_custom.conf.j2   # Кастомная конфигурация nginx-proxy
├── demo_site.conf.j2      # Конфигурация демо сайта
├── index.html.j2          # Демо веб-сайт
└── robots.txt.j2          # Файл robots.txt
```

## Переменные шаблонов

Все шаблоны используют следующие переменные:

### Основные настройки
- `domain` - доменное имя сервера (например: `example.com`)
- `server_ip` - IP адрес сервера (например: `YOUR_SERVER_IP`)
- `email` - email для SSL сертификатов (например: `admin@example.com`)

### Xray настройки
- `uuid` - UUID клиента (генерируется автоматически)
- `private_key` - приватный ключ X25519 для REALITY (генерируется автоматически)
- `public_key` - публичный ключ X25519 для REALITY (генерируется автоматически)
- `short_id` - короткий ID для REALITY (генерируется автоматически)
- `spider_x` - параметр spider X для клиентской конфигурации (генерируется автоматически)

### Fallback настройки
- `fallback_sni` - SNI для fallback (по умолчанию: `www.microsoft.com`)
- `fallback_dest` - назначение fallback (по умолчанию: `www.microsoft.com:443`)

### Безопасность и логирование
- `log_level` - уровень логирования (по умолчанию: `warning`)
- `enable_stats` - включение статистики (по умолчанию: `false`)

## Описание шаблонов

### env.j2
Генерирует файл переменных окружения `.env` со всеми необходимыми настройками.

**Использование:**
```python
template.render(
    domain='example.com',
    server_ip='YOUR_SERVER_IP',
    email='admin@example.com',
    # ... остальные переменные
)
```

### xray_server.json.j2
Серверная конфигурация Xray с поддержкой:
- VLESS протокол
- XTLS+Vision шифрование
- REALITY маскировка
- Fallback на демо сайт
- Опциональная статистика

**Особенности:**
- Условное включение статистики через `{% if enable_stats %}`
- Блокировка локального трафика
- Настройка REALITY с приватным ключом
- Fallback на контейнер `xray-demo-website:80`

### xray_client.json.j2
Клиентская конфигурация Xray с поддержкой:
- SOCKS5 прокси (порт 10808)
- HTTP прокси (порт 10809)
- VLESS+REALITY подключение
- Прямое подключение для локального трафика

**Особенности:**
- Автоматическая генерация `spider_x` параметра
- Настройка fingerprint для Chrome
- Маршрутизация локального трафика

### nginx_custom.conf.j2
Кастомная конфигурация для nginx-proxy с:
- Оптимизацией производительности (Gzip сжатие)
- Заголовками безопасности
- Настройками таймаутов и буферизации
- Скрытием версии сервера

**Особенности:**
- Подключается к nginx-proxy как дополнительная конфигурация
- Применяется ко всем виртуальным хостам
- Улучшает безопасность и производительность

### demo_site.conf.j2
Конфигурация демо сайта с:
- Обслуживанием статических файлов
- Заголовками безопасности для маскировки
- Обработкой ошибок
- Кэшированием статических ресурсов

**Особенности:**
- Используется контейнером `xray-demo-website`
- Служит fallback для Xray трафика
- Имитирует обычный веб-сайт

### index.html.j2
Демо веб-сайт игрового портала с:
- Современным дизайном
- Адаптивной версткой
- CSS анимациями
- Игровой тематикой

**Особенности:**
- Полностью самодостаточный HTML файл
- Встроенные стили CSS
- Не требует внешних зависимостей

### robots.txt.j2
Файл robots.txt с:
- Разрешением индексации
- Ссылкой на sitemap

## Архитектура nginx-proxy

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

### Преимущества новой архитектуры

- ✅ **Автоматизация** - SSL сертификаты получаются и обновляются автоматически
- ✅ **Простота** - не нужно вручную настраивать Nginx и Certbot
- ✅ **Надежность** - проверенное решение с активной поддержкой
- ✅ **Масштабируемость** - легко добавлять новые домены и сервисы
- ✅ **Безопасность** - автоматические обновления сертификатов

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
Отредактируйте `templates/xray_server.json.j2` или `templates/xray_client.json.j2`:
```bash
nano templates/xray_server.json.j2
nano templates/xray_client.json.j2
```

### Добавление новых переменных
1. Добавьте переменную в `templates/env.j2`
2. Обновите метод `get_env_vars()` в `src/config_generator.py`
3. Используйте переменную в нужных шаблонах

## Регенерация после изменений

После изменения шаблонов необходимо регенерировать конфигурации:

```bash
# Регенерация всех конфигураций
python -m src.main init \
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
python -c "
from src.config_generator import ConfigGenerator
import json
cg = ConfigGenerator()
json.loads(cg.generate_xray_server_config())
json.loads(cg.generate_client_config())
print('JSON шаблоны корректны')
"
```

### Nginx шаблоны
Для проверки конфигурации Nginx:
```bash
# Проверка синтаксиса nginx-proxy
docker run --rm -v $(pwd)/config/nginx:/etc/nginx/conf.d nginx:alpine nginx -t
```

## Примеры использования

### Создание кастомного шаблона
```jinja2
# templates/custom.conf.j2
# Дополнительные настройки безопасности
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

### Использование в коде
```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('custom.conf.j2')
content = template.render(domain='example.com')
```

## Отладка nginx-proxy

### Проверка переменных окружения
```bash
# Проверка переменных контейнера
docker exec xray-demo-website env | grep -E "(VIRTUAL_HOST|LETSENCRYPT)"
```

### Проверка генерируемых конфигураций
```bash
# Просмотр сгенерированных конфигураций nginx-proxy
docker exec xray-nginx-proxy cat /etc/nginx/conf.d/default.conf
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