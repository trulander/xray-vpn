[ru](../../docs/ru/USAGE.md)

# Xray VPN Server Usage Guide

## Table of Contents

1.  [Quick Start](#quick-start)
2.  [Detailed Configuration](#detailed-configuration)
3.  [Managing Configurations](#managing-configurations)
4.  [Client Setup](#client-setup)
5.  [Monitoring and Diagnostics](#monitoring-and-diagnostics)
6.  [Security](#security)
7.  [Troubleshooting](#troubleshooting)

## Quick Start

### Minimal Setup

1.  **Clone and Initialize**
    ```bash
    git clone <repository-url> # Replace <repository-url> with the actual URL of your repository
    cd xray-vpn
    python src/main.py init --domain your-domain.com --server-ip YOUR_SERVER_IP
    ```

2.  **Domain Configuration**
    ```bash
    # Edit the .env file (to change values after initial setup)
    nano .env

    # Specify your data:
    DOMAIN=your-domain.com
    SERVER_IP=YOUR_SERVER_IP
    EMAIL=your-email@example.com
    ```

3.  **Generate Configurations**
    ```bash
    python src/main.py generate
    ```

4.  **Obtain SSL Certificate**
    ```bash
    docker-compose --profile tools run --rm certbot certonly --webroot -w /var/www/html -d your-domain.com
    ```

5.  **Start Server**
    ```bash
    docker-compose up -d
    ```

6.  **Create Client Configuration**
    ```bash
    python src/main.py generate-client vless ws -u
    ```

## Detailed Configuration

### Environment Variables

The `.env` file contains all main settings:

```bash
# Main settings
DOMAIN=your-domain.com          # Your domain
SERVER_IP=YOUR_SERVER_IP        # Server IP address
EMAIL=your-email@example.com    # Email for SSL certificates

# UUID for protocols (automatically generated)
VMESS_UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
VLESS_UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Password for Trojan (automatically generated)
TROJAN_PASSWORD=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Paths for WebSocket (automatically generated)
VMESS_WS_PATH=/api/v1/vmess
VLESS_WS_PATH=/ws/vless
TROJAN_WS_PATH=/tunnel/trojan

# Paths for gRPC (automatically generated)
VMESS_GRPC_PATH=/vmess/grpc
VLESS_GRPC_PATH=/vless/grpc
TROJAN_GRPC_PATH=/trojan/grpc

# Services for gRPC (automatically generated)
VMESS_GRPC_SERVICE=VmessService
VLESS_GRPC_SERVICE=VlessService
TROJAN_GRPC_SERVICE=TrojanService

# Logging settings
LOG_LEVEL=warning               # debug, info, warning, error
ENABLE_STATS=false             # Enable statistics

# Docker settings
UID=1000
GID=1000
```

### Customizing Paths and Services

You can change paths and service names for additional security:

```bash
# Examples of secure paths
VMESS_WS_PATH=/api/v2/stream
VLESS_WS_PATH=/websocket/data
TROJAN_WS_PATH=/live/updates

# Examples of gRPC service names
VMESS_GRPC_SERVICE=DataStreamService
VLESS_GRPC_SERVICE=ApiGatewayService
TROJAN_GRPC_SERVICE=NotificationService
```

## Managing Configurations

### Generating Configurations

```bash
# Generate all configurations
python src/main.py generate

# Generate a specific client configuration
python src/main.py generate-client vless ws
python src/main.py generate-client vmess grpc
python src/main.py generate-client trojan ws

# Generate with URL for mobile applications
python src/main.py generate-client vless ws -u
```

### Configuration Structure

After generation, you will see the following file structure:

```
config/
├── xray/
│   └── config.json           # Xray server configuration
├── nginx/
│   ├── nginx.conf           # Main Nginx configuration
│   └── demo-site.conf       # Demo site configuration
└── client/
    ├── vless_ws.json        # VLESS WebSocket client
    ├── vless_grpc.json      # VLESS gRPC client
    ├── vmess_ws.json        # VMess WebSocket client
    ├── vmess_grpc.json      # VMess gRPC client
    ├── trojan_ws.json       # Trojan WebSocket client
    ├── trojan_grpc.json     # Trojan gRPC client
    └── *_url.txt            # URLs for mobile applications
```

## Client Setup

### Supported Applications

| Platform | Application | Supported Protocols |
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

### Setup via JSON Configuration

1.  **Copy the configuration**
    ```bash
    cat config/client/vless_ws.json
    ```

2.  **Import into client**
    -   v2rayN: Servers → Add server → Import from clipboard
    -   Qv2ray: Import → Import from file
    -   v2rayNG: + → Import config from clipboard

### Setup via URL

1.  **Get the URL**
    ```bash
    python src/main.py generate-client vless ws -u
    cat config/client/vless_ws_url.txt
    ```

2.  **Import the URL**
    -   Copy the URL to the clipboard
    -   In the mobile app: 'plus' button → Import from clipboard
    -   Or scan the QR code (if supported)

### Manual Setup

If automatic import does not work, set up manually:

**VLESS WebSocket:**
-   Address: your-domain.com
-   Port: 443
-   UUID: from VLESS_UUID variable
-   Encryption: none
-   Transport: WebSocket
-   Path: from VLESS_WS_PATH variable
-   Host: your-domain.com
-   TLS: enabled
-   SNI: your-domain.com

**VMess gRPC:**
-   Address: your-domain.com
-   Port: 443
-   UUID: from VMESS_UUID variable
-   Encryption: auto
-   Transport: gRPC
-   Service: from VMESS_GRPC_SERVICE variable
-   TLS: enabled
-   SNI: your-domain.com

## Monitoring and Diagnostics

### Check Status

```bash
# Overall server status
python src/main.py status

# SSL certificate status
python src/main.py ssl-status

# Docker container status
docker-compose ps

# Resource usage
docker stats
```

### View Logs

```bash
# All logs
docker-compose logs -f

# Logs of a specific service
docker-compose logs -f nginx
docker-compose logs -f xray-server
docker-compose logs -f demo-website

# Logs for the last hour
docker-compose logs --since 1h

# Last 100 lines
docker-compose logs --tail 100
```

### Test Connection

```bash
# Check server availability
curl -I https://your-domain.com

# Check SSL certificate
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Check DNS
nslookup your-domain.com
dig your-domain.com
```

## Security

### Security Recommendations

1.  **Use strong passwords**
2.  **Configure firewall**
3.  **Regularly update the system**
4.  **Monitor logs**
5.  **Use SSH keys**

### Firewall Configuration (UFW)

```bash
# Reset rules
sudo ufw --force reset

# Allow SSH
sudo ufw allow 22

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### SSH Configuration

```bash
# Generate SSH key (on local machine)
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy key to server
ssh-copy-id user@your-server-ip

# Disable password authentication
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart ssh
```

### System Update

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d
```

## Troubleshooting

### SSL Certificate Issues

**Symptoms:**
-   "SSL certificate problem" error
-   Browser shows "Not secure"

**Solution:**
```bash
# Check certificate status
python src/main.py ssl-status

# Force certificate renewal
docker-compose --profile tools run --rm certbot certonly --webroot -w /var/www/html -d your-domain.com --force-renewal

# Restart Nginx
docker-compose restart nginx-proxy
```

### Client Connection Issues

**Symptoms:**
-   Client cannot connect
-   Connection timeouts

**Diagnostics:**
```bash
# Check server availability
telnet your-domain.com 443

# Check Xray logs
docker-compose logs xray-server

# Check Nginx configuration
docker-compose exec nginx nginx -t
```

**Solution:**
1.  Ensure the domain points to your server
2.  Check if ports 80 and 443 are open
3.  Verify the client configuration is correct
4.  Try a different protocol/transport

### Performance Issues

**Symptoms:**
-   Slow connection speed
-   High CPU usage

**Diagnostics:**
```bash
# Check system load
htop
iostat 1

# Check network activity
iftop
ss -tuln
```

**Optimization:**
1.  Increase server resources
2.  Use gRPC instead of WebSocket
3.  Configure limits in Xray configuration
4.  Optimize Nginx settings

### Docker Issues

**Symptoms:**
-   Containers not starting
-   Build errors

**Solution:**
```bash
# Clean Docker
docker system prune -a

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs
```

### Recovery After Failure

```bash
# Stop all services
docker-compose down

# Backup configurations
cp -r config config.backup
cp .env .env.backup

# Regenerate configurations
python src/main.py generate

# Start services
docker-compose up -d
```

## Getting Help

If the problem is not resolved:

1.  **Check logs:** `docker-compose logs`
2.  **Check status:** `python src/main.py status`
3.  **Check documentation:** [Xray Documentation](https://xtls.github.io/)
4.  **Check network settings:** DNS, firewall, ports

## Regular Maintenance

### Weekly
-   Check logs for errors
-   Monitor resource usage
-   Check SSL certificate status

### Monthly
-   Update system and Docker images
-   Backup configurations
-   Security check

### As Needed
-   Key and password rotation
-   Changing paths and services
-   Scaling resources