[ru](../../docs/ru/README.md)

# Xray VPN Server

This VPN server masquerades as a regular HTTPS website and supports a variety of protocols and transports.

## Quick Start

### Requirements
- Ubuntu/Debian server with a public IP
- Docker and Docker Compose
- A domain pointed to your server

### Deployment

```bash
# 1. Clone
git clone <repository-url> xray-vpn
cd xray-vpn

# 2. Deploy with automatic SSL
./deploy.sh example.com admin@example.com 203.0.113.10
```

**Done!** Your VPN server is running and accessible at https://example.com

SSL certificates are automatically issued and renewed using nginx-proxy and acme-companion.

## Architecture

```
Internet → nginx-proxy (80/443) → {
  /api/v1/vmess → xray-server:10001 (VMess WebSocket)
  /ws/vless → xray-server:10002 (VLESS WebSocket)  
  /stream/trojan → xray-server:10003 (Trojan WebSocket)
  /* → demo-website (masking)
}
```

### Automatic SSL

- **nginx-proxy**: automatically creates virtual hosts
- **acme-companion**: automatically obtains and renews SSL certificates
- **xray-server**: one server handles all protocols (VMess, VLESS, Trojan)
- **Environment variables**: `VIRTUAL_HOST`, `LETSENCRYPT_HOST`, `LETSENCRYPT_EMAIL`

## Client Applications

### Desktop
- **V2rayN** (Windows)
- **V2rayU** (macOS)
- **Qv2ray** (Linux)

### Mobile
- **V2rayNG** (Android)
- **Shadowrocket** (iOS)

### Configurations
After deployment, find the files in `config/client/`:
- `vmess_ws.json` - VMess WebSocket
- `vless_ws.json` - VLESS WebSocket  
- `trojan_ws.json` - Trojan WebSocket
- `vmess_grpc.json` - VMess gRPC
- `vless_grpc.json` - VLESS gRPC  
- `trojan_grpc.json` - Trojan gRPC

## Secret Web Page

After deployment, you will get access to a **secret web page** where you can conveniently download configurations:

```bash
# Link is displayed at the end of deployment
./deploy.sh example.com admin@example.com
# Secret configurations page:
#    https://example.com/admin/a3b8c9d4e5f6...
```

### On the page you will find:
- Configuration download - all protocols and transports
- Mobile URL - ready-to-copy links
- Instructions - for all popular applications
- Security - random URL, protection from indexing

**Important:** Do not share this link! Save it in a safe place.

## Management

```bash
# Service status
docker-compose ps

# View logs
docker-compose logs nginx-proxy
docker-compose logs acme-companion
docker-compose logs xray-server

# Restart
docker-compose restart

# Stop
docker-compose down

# Generate new client configurations
docker-compose --profile tools run --rm config-generator generate-client vless ws

# Generate URL for mobile applications
docker-compose --profile tools run --rm config-generator generate-client vless ws -u
```

## Security

- Masquerading as a regular HTTPS website
- Automatic SSL certificates from Let's Encrypt
- Random UUIDs and passwords
- Randomized paths and services
- Fallback to a real website

## Troubleshooting

### Diagnosing Issues

```bash
# General SSL and service diagnostics
./scripts/diagnose-ssl.sh

# Testing connections
./scripts/test_connections.sh
```

### Checking SSL Certificates

```bash
# nginx-proxy status
docker-compose logs nginx-proxy

# acme-companion status
docker-compose logs acme-companion

# Check certificates
ls -la data/ssl/

# Check environment variables
docker-compose exec demo-website env | grep -E "(VIRTUAL_HOST|LETSENCRYPT)"
```

### Checking Website and VPN Paths

```bash
# Check main website
curl -I https://example.com

# Check nginx-proxy configuration
docker-compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf
```

### Connection Not Working
```bash
# Check configuration
docker-compose --profile tools run --rm config-generator status

# Check Xray logs
docker-compose logs xray-server

# Test website
curl -I https://example.com
```

## Technologies

- **Xray-core** - VPN server with VMess, VLESS, Trojan support
- **nginx-proxy** - Automatic reverse proxy
- **acme-companion** - Automatic SSL certificates
- **Docker** - Containerization
- **Let's Encrypt** - SSL certificates
- **Python** - Configuration generator

## Documentation

- [Quick Start](docs/en/QUICK_START.md) - Brief instructions
- [Deployment Example](docs/en/EXAMPLE.md) - Step-by-step example
- [Usage](docs/en/USAGE.md) - User guide
- [Templates](docs/en/templates.md) - Configuration customization
- [nginx-proxy Architecture](docs/en/nginx-proxy-architecture.md) - Architecture details

## Scripts

- `deploy.sh` - Main deployment script
- `scripts/diagnose-ssl.sh` - SSL and nginx-proxy diagnostics
- `scripts/test_connections.sh` - Connection testing