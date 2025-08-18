[en](../../docs/en/secret-config-page.md)

# Секретная веб-страница для конфигураций

## Обзор

Секретная веб-страница предоставляет защищенный доступ к клиентским конфигурациям VPN. Вы можете получить к ней доступ по случайно сгенерированному URL, где найдете все необходимые файлы и инструкции для настройки VPN-клиентов.

## Функциональность

### Безопасность
- **Случайный URL**: Путь генерируется автоматически (например: `/admin/a3b8c9d4e5f6g7h8`)
- **Защита от индексации**: `robots.txt` блокирует поисковые системы
- **Заголовки безопасности**: `X-Frame-Options`, `X-Content-Type-Options`
- **Предупреждения**: Явные указания не делиться ссылкой

### Конфигурационные файлы
Страница предоставляет доступ ко всем клиентским конфигурациям:

**VMess (рекомендуется)**
- WebSocket (`vmess_ws.json`)
- gRPC (`vmess_grpc.json`)

**VLESS (быстрый)**
- WebSocket (`vless_ws.json`)
- gRPC (`vless_grpc.json`)

**Trojan (скрытность)**
- WebSocket (`trojan_ws.json`)
- gRPC (`trojan_grpc.json`)

### URL для мобильных приложений
Готовые URL для быстрого добавления в мобильные приложения:
- **VLESS WebSocket**: `vless://uuid@domain:443?...`
- **VMess WebSocket**: `vmess://base64config`
- **Trojan WebSocket**: `trojan://password@domain:443?...`

### Инструкции по использованию
Подробные инструкции для всех популярных VPN клиентов:
- Android (V2rayNG)
- iOS (Shadowrocket)
- Windows (V2rayN)
- macOS (V2rayU)
- Linux (Qv2ray)

## Технические детали

### Генерация URL
URL генерируется в модуле `KeyGenerator.generate_secret_path()`:
- Случайные префиксы: `/admin`, `/panel`, `/dashboard`, etc.
- 16-символьная случайная строка: `a-z0-9`
- Итоговый формат: `/admin/a3b8c9d4e5f6g7h8`

### Nginx конфигурация
Секретная страница обслуживается через nginx-proxy:

```nginx
# Секретная страница конфигураций
location {{ secret_config_path }} {
    alias /usr/share/nginx/html/configs/;
    try_files $uri $uri/ /configs/index.html;
    
    # Заголовки безопасности
    add_header X-Robots-Tag "noindex, nofollow" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Кэширование конфигураций
    location ~* \.(json)$ {
        add_header Content-Disposition "attachment";
        add_header Content-Type "application/json";
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
}
```

### Структура файлов
```
data/www/configs/
├── index.html          # Главная страница
├── vmess_ws.json       # VMess WebSocket конфигурация
├── vmess_grpc.json     # VMess gRPC конфигурация
├── vless_ws.json       # VLESS WebSocket конфигурация
├── vless_grpc.json     # VLESS gRPC конфигурация
├── trojan_ws.json      # Trojan WebSocket конфигурация
└── trojan_grpc.json    # Trojan gRPC конфигурация
```

## Использование

### Получение ссылки
После развертывания ссылка выводится в консоли:
```bash
./deploy.sh example.com admin@example.com

# Вывод:
Секретная страница конфигураций:
   https://example.com/admin/a3b8c9d4e5f6g7h8
   Сохраните эту ссылку в безопасном месте!
```

### Просмотр в .env файле
Секретный путь также сохраняется в `.env`:
```bash
SECRET_CONFIG_PATH=/admin/a3b8c9d4e5f6g7h8
```

### Тестирование
Проверить доступность страницы:
```bash
# Тестирование подключений включает проверку секретной страницы
./scripts/test_connections.sh
```

## Интерфейс страницы

### Дизайн
- **Современный интерфейс**: Градиентный дизайн с анимациями
- **Адаптивность**: Корректное отображение на всех устройствах
- **Удобство**: Группировка по протоколам, четкая навигация

### Функции JavaScript
- **Копирование URL**: Кнопки для копирования мобильных URL
- **Анимации**: Плавное появление элементов
- **Обратная связь**: Уведомления о копировании

### Группировка протоколов
Каждый протокол имеет свой цветовой бейдж:
- **VMess**: Синий бейдж "Рекомендуется"
- **VLESS**: Зеленый бейдж "Быстрый"
- **Trojan**: Красный бейдж "Скрытность"

## Безопасность

### Рекомендации
1. **Не делитесь ссылкой** - она содержит персональные настройки
2. **Сохраните в безопасном месте** - например, в менеджере паролей
3. **Ограничьте доступ** - только доверенные пользователи
4. **Регулярно проверяйте** - следите за несанкционированным доступом

### Защитные меры
- Случайный URL длиной 16+ символов
- Отсутствие ссылок с основного сайта
- Заголовки защиты от фреймов
- Блокировка индексации поисковиками

## Устранение неполадок

### Страница не открывается
```bash
# Проверка nginx конфигурации
docker-compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf | grep -A5 "location.*admin"

# Проверка файлов
ls -la data/www/configs/

# Логи nginx-proxy
docker-compose logs nginx-proxy | grep -i error
```

### Неправильный URL
```bash
# Проверка переменной окружения
grep SECRET_CONFIG_PATH .env

# Регенерация конфигураций
docker-compose --profile tools run --rm config-generator init --domain your-domain.com
```

### Отсутствуют файлы конфигураций
```bash
# Принудительная регенерация
docker-compose --profile tools run --rm config-generator generate

# Проверка копирования файлов
ls -la config/client/
ls -la data/www/configs/
```

## Кастомизация

### Изменение дизайна
Отредактируйте `templates/config_page.html.j2`:
```bash
nano templates/config_page.html.j2
```

### Изменение URL
Отредактируйте `.env` или перегенерируйте:
```bash
# Ручное изменение
nano .env
# SECRET_CONFIG_PATH=/my/custom/path

# Автоматическая регенерация
docker-compose --profile tools run --rm config-generator init --domain your-domain.com
```

### Добавление функций
Добавьте новые функции в `src/config_generator.py`:
```python
def generate_config_page(self) -> str:
    # Ваши дополнения
    pass
```

## Интеграция с другими системами

### API доступ
Секретная страница может быть интегрирована с системами управления:
```bash
# Получение конфигураций через API
curl -s https://domain.com/admin/xyz123/vmess_ws.json

# Программное скачивание
wget https://domain.com/admin/xyz123/configs/
```

### Мониторинг доступа
Логи доступа к секретной странице в nginx-proxy:
```bash
docker-compose logs nginx-proxy | grep "GET.*admin"
```

## Лучшие практики

1. **Регулярное обновление** - периодически регенерируйте URL
2. **Мониторинг доступа** - следите за логами
3. **Резервное копирование** - сохраняйте ссылку в нескольких местах
4. **Документирование** - ведите записи об используемых конфигурациях
5. **Тестирование** - регулярно проверяйте работоспособность страницы