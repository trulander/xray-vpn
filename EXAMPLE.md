# Пример развертывания

## Сценарий
У вас есть сервер с IP `203.0.113.10` и домен `vpn.example.com`.

## Шаги

### 1. Настройка DNS
Создайте A-запись в DNS:
```
vpn.example.com → 203.0.113.10
```

### 2. Подключение к серверу
```bash
ssh root@203.0.113.10
```

### 3. Установка Docker (если не установлен)
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установка Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 4. Развертывание VPN
```bash
# Клонирование
git clone <repository-url> xray-vpn
cd xray-vpn

# Развертывание (IP будет определен автоматически)
./deploy.sh vpn.example.com admin@example.com

# Или с явным указанием IP
./deploy.sh vpn.example.com admin@example.com 203.0.113.10
```

**SSL сертификаты получаются автоматически через nginx-proxy + acme-companion!**

### 5. Проверка работы
```bash
# Проверка сайта (подождите 2-5 минут для получения SSL)
curl -I https://vpn.example.com

# Статус сервисов
docker-compose ps

# Логи nginx-proxy и acme-companion
docker-compose logs nginx-proxy acme-companion

# Диагностика (если нужно)
./scripts/diagnose-ssl.sh
```

## Результат

✅ **Сайт:** https://vpn.example.com  
✅ **Конфигурации:** `config/client/`  
✅ **Протоколы:** VMess, VLESS, Trojan (WebSocket + gRPC)  
✅ **SSL:** Автоматические сертификаты Let's Encrypt

## Использование клиентов

### Android (V2rayNG)
1. Скачайте файл `config/client/vless_ws.json`
2. В V2rayNG: ➕ → Import config from file
3. Выберите скачанный файл

### Windows (V2rayN)
1. Скачайте файл `config/client/vmess_ws.json`
2. В V2rayN: Servers → Import bulk URL from clipboard
3. Скопируйте содержимое файла

### iOS (Shadowrocket)
1. Сгенерируйте URL:
   ```bash
   docker-compose --profile tools run --rm config-generator generate-client vless ws -u
   ```
2. Скопируйте URL из файла `config/client/vless_ws_url.txt`
3. В Shadowrocket: ➕ → Paste from clipboard

## Управление

```bash
# Перезапуск
docker-compose restart

# Остановка
docker-compose down

# Проверка SSL сертификатов (обновляются автоматически каждые 12 часов)
docker-compose logs acme-companion

# Тестирование подключений
./scripts/test_connections.sh
``` 