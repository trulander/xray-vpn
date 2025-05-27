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

### 5. Настройка SSL
```bash
# После того как DNS заработал (может занять до 24 часов)
./scripts/setup-ssl.sh vpn.example.com admin@example.com
```

### 6. Проверка
```bash
# Проверка сайта
curl -I https://vpn.example.com

# Статус сервисов
docker-compose ps

# Логи
docker-compose logs xray-server
```

## Результат

✅ **Сайт:** https://vpn.example.com  
✅ **Конфигурации:** `config/client/`  
✅ **Протоколы:** VMess, VLESS, Trojan (WebSocket + gRPC)

## Использование клиентов

### Android (V2rayNG)
1. Скачайте файл `config/client/vless-ws.json`
2. В V2rayNG: ➕ → Import config from file
3. Выберите скачанный файл

### Windows (V2rayN)
1. Скачайте файл `config/client/vmess-ws.json`
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

# Обновление SSL (автоматически каждые 12 часов)
docker-compose --profile tools run --rm certbot renew
``` 