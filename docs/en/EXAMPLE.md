[ru](../../docs/ru/EXAMPLE.md)

# Deployment Example

## Scenario
You have a server with IP `203.0.113.10` and a domain `vpn.example.com`.

## Steps

### 1. DNS Setup
Create an A-record in DNS:
```
vpn.example.com → 203.0.113.10
```

### 2. Connect to the Server
```bash
ssh root@203.0.113.10
```

### 3. Install Docker (if not installed)
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 4. Deploy VPN
```bash
# Clone (replace <repository-url> with the actual URL of your repository)
git clone <repository-url> xray-vpn
cd xray-vpn

# Deploy (IP will be determined automatically)
# Note: The deploy.sh script automatically rebuilds the config-generator image to apply the latest changes.
./deploy.sh vpn.example.com admin@example.com

# Or with explicit IP
./deploy.sh vpn.example.com admin@example.com 203.0.113.10
```

**SSL certificates are issued and renewed automatically using nginx-proxy and acme-companion!**

### 5. Check Operation
```bash
# Check website (wait 2-5 minutes for SSL)
curl -I https://vpn.example.com

# Service status
docker-compose ps

# nginx-proxy and acme-companion logs
docker-compose logs nginx-proxy acme-companion

# Diagnostics (if needed)
./scripts/diagnose-ssl.sh
```

## Result

Website: https://vpn.example.com
Configurations: `config/client/`
Protocols: VMess, VLESS, Trojan (WebSocket + gRPC)
SSL: Automatic Let's Encrypt certificates
Secret page: https://vpn.example.com/admin/xyz123... (will be displayed in the console)
Nginx configuration: Custom file `config/nginx/{domain}_location` successfully created.

### Secret Web Page

After deployment, a link to the secret page will be shown in the console:

```
Secret configurations page:
   https://vpn.example.com/admin/a3b8c9d4e5f6g7h8
   Save this link in a safe place!
```

On this page you will find:
- All configuration files for download
- URLs for quick addition to mobile applications
- Step-by-step instructions for all devices

**Important:** This link is randomly generated and contains your personal VPN settings!

## Using Clients

### Android (V2rayNG)
1. Download the file `config/client/vless_ws.json`
2. In V2rayNG: 'plus' button → Import config from file
3. Select the downloaded file

### Windows (V2rayN)
1. Download the file `config/client/vmess_ws.json`
2. In V2rayN: Servers → Import bulk URL from clipboard
3. Copy the content of the file

### iOS (Shadowrocket)
1. Generate URL:
   ```bash
   docker-compose --profile tools run --rm config-generator generate-client vless ws -u
   ```
2. Copy the URL from the file `config/client/vless_ws_url.txt`
3. In Shadowrocket: 'plus' button → Paste from clipboard

## Management

```bash
# Restart
docker-compose restart

# Stop
docker-compose down

# Check SSL certificates (automatically renewed every 12 hours)
docker-compose logs acme-companion

# Test connections
./scripts/test_connections.sh
```