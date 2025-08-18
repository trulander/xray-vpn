[ru](../../docs/ru/QUICK_START.md)

## Quick Start

## Automatic Deployment with SSL

```bash
# 1. Clone the repository (replace <repository-url> with the actual URL of your repository)
git clone <repository-url> xray-vpn
cd xray-vpn

# 2. Start deployment
./deploy.sh example.com admin@example.com 203.0.113.10
```

**Done!** SSL certificates are issued and renewed automatically.

## What's Happening

1.  **nginx-proxy** automatically creates virtual hosts
2.  **acme-companion** automatically obtains SSL certificates
3.  **xray-server** starts and handles all protocols (VMess, VLESS, Trojan)
4.  **demo-website** serves as a disguise

## Checking Operation

```bash
# Service status
docker-compose ps

# SSL check
curl -I https://example.com

# Logs
docker-compose logs nginx-proxy
docker-compose logs acme-companion
```

## Client Configurations

After deployment, find the files in `config/client/`:
- `vmess_ws.json` - VMess WebSocket
- `vless_ws.json` - VLESS WebSocket  
- `trojan_ws.json` - Trojan WebSocket

## Advantages of nginx-proxy

- Automatic SSL - certificates are obtained and renewed automatically
- No "chicken and egg" problem - nginx-proxy starts without SSL, then obtains certificates
- Simplicity - no need to manually configure nginx and certbot
- Reliability - a proven solution with active support

## Troubleshooting

```bash
# If something isn't working
docker-compose down
docker-compose up -d

# Check environment variables
docker-compose exec demo-website env | grep -E "(VIRTUAL_HOST|LETSENCRYPT)"
```

## Done!

Your VPN server is ready to use:

- **Website:** https://vpn.example.com
- **Client configurations:** `config/client/`
- **Supported protocols:** VMess, VLESS, Trojan (WebSocket + gRPC)

## Client Applications

### For Desktop
- **V2rayN** (Windows)
- **V2rayU** (macOS)
- **Qv2ray** (Linux)

### For Mobile
- **V2rayNG** (Android)
- **Shadowrocket** (iOS)

Use files from the `config/client/` folder:
- `vmess_ws.json` - VMess WebSocket
- `vless_ws.json` - VLESS WebSocket  
- `trojan_ws.json` - Trojan WebSocket

## Management

```bash
# Service status
docker-compose ps

# View logs
docker-compose logs xray-server

# Restart
docker-compose restart

# Stop
docker-compose down
```

## Troubleshooting

### SSL Issues
```bash
# Check certificate status
docker-compose --profile tools run --rm config-generator ssl-status

# Force certificate renewal
docker-compose --profile tools run --rm certbot renew --force-renewal
docker-compose restart nginx-proxy
```

### Connection Issues
```bash
# Check configuration
docker-compose --profile tools run --rm config-generator status

# Check Xray logs
docker-compose logs xray-server

# Test connection
curl -I https://vpn.example.com
```

## Security

- All UUIDs and passwords are randomly generated
- WebSocket paths and gRPC service names are randomized
- VPN traffic is disguised as regular HTTPS
- Fallback to a real website for regular traffic