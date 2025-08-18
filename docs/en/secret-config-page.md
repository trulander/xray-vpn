[ru](../../docs/ru/secret-config-page.md)

# Secret Web Page for Configurations

## Overview

The secret web page provides secure access to client VPN configurations. You can access it via a randomly generated URL, where you will find all the necessary files and instructions for setting up VPN clients.

## Functionality

### Security
- **Random URL**: The path is generated automatically (e.g., `/admin/a3b8c9d4e5f6g7h8`)
- **Protection from Indexing**: `robots.txt` blocks search engines
- **Security Headers**: `X-Frame-Options`, `X-Content-Type-Options`
- **Warnings**: Explicit instructions not to share the link

### Configuration Files
The page provides access to all client configurations:

**VMess (recommended)**
- WebSocket (`vmess_ws.json`)
- gRPC (`vmess_grpc.json`)

**VLESS (fast)**
- WebSocket (`vless_ws.json`)
- gRPC (`vless_grpc.json`)

**Trojan (stealth)**
- WebSocket (`trojan_ws.json`)
- gRPC (`trojan_grpc.json`)

### URLs for Mobile Applications
Ready-to-use URLs for quick addition to mobile applications:
- **VLESS WebSocket**: `vless://uuid@domain:443?...`
- **VMess WebSocket**: `vmess://base64config`
- **Trojan WebSocket**: `trojan://password@domain:443?...`

### Usage Instructions
Detailed instructions for all popular VPN clients:
- Android (V2rayNG)
- iOS (Shadowrocket)
- Windows (V2rayN)
- macOS (V2rayU)
- Linux (Qv2ray)

## Technical Details

### URL Generation
The URL is generated in the `KeyGenerator.generate_secret_path()` module:
- Random prefixes: `/admin`, `/panel`, `/dashboard`, etc.
- 16-character random string: `a-z0-9`
- Final format: `/admin/a3b8c9d4e5f6g7h8`

### Nginx Configuration
The secret page is served via nginx-proxy:

```nginx
# Secret configuration page
location {{ secret_config_path }} {
    alias /usr/share/nginx/html/configs/;
    try_files $uri $uri/ /configs/index.html;
    
    # Security Headers
    add_header X-Robots-Tag "noindex, nofollow" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Configuration Caching
    location ~* \.(json)$ {
        add_header Content-Disposition "attachment";
        add_header Content-Type "application/json";
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
}
```

### File Structure
```
data/www/configs/
├── index.html          # Main page
├── vmess_ws.json       # VMess WebSocket configuration
├── vmess_grpc.json     # VMess gRPC configuration
├── vless_ws.json       # VLESS WebSocket configuration
├── vless_grpc.json     # VLESS gRPC configuration
├── trojan_ws.json      # Trojan WebSocket configuration
└── trojan_grpc.json    # Trojan gRPC configuration
```

## Usage

### Getting the Link
After deployment, the link is displayed in the console:
```bash
./deploy.sh example.com admin@example.com

# Output:
Secret configuration page:
   https://example.com/admin/a3b8c9d4e5f6g7h8
   Save this link in a safe place!
```

### Viewing in .env file
The secret path is also saved in `.env`:
```bash
SECRET_CONFIG_PATH=/admin/a3b8c9d4e5f6g7h8
```

### Testing
Check page accessibility:
```bash
# Connection testing includes checking the secret page
./scripts/test_connections.sh
```

## Page Interface

### Design
- **Modern Interface**: Gradient design with animations
- **Responsiveness**: Correct display on all devices
- **Convenience**: Grouping by protocols, clear navigation

### JavaScript Functions
- **URL Copying**: Buttons for copying mobile URLs
- **Animations**: Smooth appearance of elements
- **Feedback**: Copy notifications

### Protocol Grouping
Each protocol has its own colored badge:
- **VMess**: Blue badge "Recommended"
- **VLESS**: Green badge "Fast"
- **Trojan**: Red badge "Stealth"

## Security

### Recommendations
1. **Do not share the link** - it contains personal settings
2. **Save in a safe place** - for example, in a password manager
3. **Restrict access** - only trusted users
4. **Regularly check** - monitor for unauthorized access

### Protective Measures
- Random URL 16+ characters long
- No links from the main site
- Frame protection headers
- Blocking search engine indexing

## Troubleshooting

### Page Not Opening
```bash
# Check nginx configuration
docker-compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf | grep -A5 "location.*admin"

# Check files
ls -la data/www/configs/

# nginx-proxy logs
docker-compose logs nginx-proxy | grep -i error
```

### Incorrect URL
```bash
# Check environment variable
grep SECRET_CONFIG_PATH .env

# Regenerate configurations
docker-compose --profile tools run --rm config-generator init --domain your-domain.com
```

### Missing Configuration Files
```bash
# Force regeneration
docker-compose --profile tools run --rm config-generator generate

# Check file copying
ls -la config/client/
ls -la data/www/configs/
```

## Customization

### Changing Design
Edit `templates/config_page.html.j2`:
```bash
nano templates/config_page.html.j2
```

### Changing URL
Edit `.env` or regenerate:
```bash
# Manual change
nano .env
# SECRET_CONFIG_PATH=/my/custom/path

# Automatic regeneration
docker-compose --profile tools run --rm config-generator init --domain your-domain.com
```

### Adding Functions
Add new functions to `src/config_generator.py`:
```python
def generate_config_page(self) -> str:
    # Your additions
    pass
```

## Integration with Other Systems

### API Access
The secret page can be integrated with management systems:
```bash
# Get configurations via API
curl -s https://domain.com/admin/xyz123/vmess_ws.json

# Programmatic download
wget https://domain.com/admin/xyz123/configs/
```

### Access Monitoring
Logs of access to the secret page in nginx-proxy:
```bash
docker-compose logs nginx-proxy | grep "GET.*admin"
```

## Best Practices

1. **Regular updates** - periodically regenerate the URL
2. **Access monitoring** - monitor logs
3. **Backup** - save the link in multiple places
4. **Documentation** - keep records of used configurations
5. **Testing** - regularly check page functionality