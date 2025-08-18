[ru](../../docs/ru/templates.md)

# Configuration Templates

All configurations in the project are created based on Jinja2 templates, which makes them flexible and convenient for customization.

## Template Structure

```
templates/
├── env_multi.j2           # .env file template for multi-protocol
├── xray_server_multi.json.j2    # Xray server configuration (all protocols)
├── client_vmess_ws.json.j2      # VMess WebSocket client
├── client_vless_ws.json.j2      # VLESS WebSocket client
├── client_trojan_ws.json.j2     # Trojan WebSocket client
├── client_vmess_grpc.json.j2    # VMess gRPC client
├── client_vless_grpc.json.j2    # VLESS gRPC client
├── client_trojan_grpc.json.j2   # Trojan gRPC client
├── nginx_custom.conf.j2         # Custom location blocks for nginx-proxy
├── demo_site.conf.j2            # Demo site configuration
├── index.html.j2                # Demo website
└── robots.txt.j2                # robots.txt file
```

## Template Variables

All templates use the following variables:

### Core Settings
- `domain` - server domain name (e.g.: `example.com`)
- `server_ip` - server IP address (e.g.: `YOUR_SERVER_IP`)
- `email` - email for SSL certificates (e.g.: `admin@example.com`)

### Multi-Protocol Settings
- `vmess_uuid` - UUID for VMess protocol (automatically generated)
- `vless_uuid` - UUID for VLESS protocol (automatically generated)
- `trojan_password` - password for Trojan protocol (automatically generated)

### WebSocket Paths
- `vmess_ws_path` - path for VMess WebSocket (e.g.: `/api/v1/vmess`)
- `vless_ws_path` - path for VLESS WebSocket (e.g.: `/ws/vless`)
- `trojan_ws_path` - path for Trojan WebSocket (e.g.: `/stream/trojan`)

### gRPC Settings
- `vmess_grpc_path` - path for VMess gRPC (e.g.: `/vmess/grpc`)
- `vless_grpc_path` - path for VLESS gRPC (e.g.: `/vless/grpc`)
- `trojan_grpc_path` - path for Trojan gRPC (e.g.: `/trojan/grpc`)
- `vmess_grpc_service` - VMess gRPC service name (e.g.: `VmessService`)
- `vless_grpc_service` - VLESS gRPC service name (e.g.: `VlessService`)
- `trojan_grpc_service` - Trojan gRPC service name (e.g.: `TrojanService`)

### Security and Logging
- `log_level` - logging level (default: `warning`)
- `enable_stats` - enable statistics (default: `false`)

## Template Descriptions

### env_multi.j2
Generates an `.env` environment variables file with all settings for a multi-protocol architecture.

**Usage:**
```python
template.render(
    domain='example.com',
    server_ip='YOUR_SERVER_IP',
    email='admin@example.com',
    vmess_uuid='...', 
    vless_uuid='...', 
    trojan_password='...', 
    # ... other variables
)
```

### xray_server_multi.json.j2
Xray server configuration with support for all protocols:
- VMess WebSocket (port 10001)
- VLESS WebSocket (port 10002)
- Trojan WebSocket (port 10003)
- VMess gRPC (port 10011)
- VLESS gRPC (port 10012)
- Trojan gRPC (port 10013)

**Features:**
- Conditional enabling of statistics via `{% if enable_stats %}`
- Local traffic blocking
- Support for all modern protocols

### Client Templates
Client configurations for various protocols and transports:

**WebSocket Clients:**
- `client_vmess_ws.json.j2` - VMess WebSocket
- `client_vless_ws.json.j2` - VLESS WebSocket
- `client_trojan_ws.json.j2` - Trojan WebSocket

**gRPC Clients:**
- `client_vmess_grpc.json.j2` - VMess gRPC
- `client_vless_grpc.json.j2` - VLESS gRPC
- `client_trojan_grpc.json.j2` - Trojan gRPC

**Features:**
- SOCKS5 proxy (port 1080)
- HTTP proxy (port 1081)
- Direct connection for local traffic
- Ad blocking

### nginx_custom.conf.j2
Custom configuration for nginx-proxy with:
- Location blocks for all VPN paths (WebSocket and gRPC)
- Correct proxy headers setup
- Timeouts for WebSocket connections
- gRPC proxying

**Features:**
- Connects to nginx-proxy as a `{domain}_location` file
- Automatically applied when environment variables are present
- Supports all protocols and transports

### demo_site.conf.j2
Demo site configuration with:
- Serving static files
- Security headers for masking
- Error handling
- Caching static resources

**Features:**
- Used by the `demo-website` container
- Serves as a fallback for regular traffic
- Mimics a regular website

### index.html.j2
Demo website with:
- Modern design
- Responsive layout
- CSS animations
- Professional appearance

**Features:**
- Fully self-contained HTML file
- Embedded CSS styles
- No external dependencies required

### robots.txt.j2
robots.txt file with:
- Indexing allowed
- Link to sitemap

## [nginx-proxy Architecture](../../docs/en/nginx-proxy-architecture.md)

### How nginx-proxy works

1. **Automatic discovery** - nginx-proxy monitors container startup/shutdown
2. **Configuration generation** - automatically creates virtual hosts based on environment variables
3. **SSL certificates** - acme-companion automatically obtains and renews certificates

### Environment variables for nginx-proxy

Containers must have the following variables:

```bash
VIRTUAL_HOST=example.com        # Domain for proxying
LETSENCRYPT_HOST=example.com    # Domain for SSL certificate
LETSENCRYPT_EMAIL=admin@example.com  # Email for Let's Encrypt
```

### Advantages of nginx-proxy architecture

- Automation - SSL certificates are obtained and renewed automatically
- Simplicity - no need to manually configure Nginx and Certbot
- Reliability - a proven solution with active support
- Scalability - easily add new domains and services
- Security - automatic certificate renewals

## Customizing Templates

### Changing Site Design
Edit `templates/index.html.j2`:
```bash
nano templates/index.html.j2
```

### Configuring nginx-proxy
Edit `templates/nginx_custom.conf.j2`:
```bash
nano templates/nginx_custom.conf.j2
```

### Changing Xray Configuration
Edit `templates/xray_server_multi.json.j2`: 
```bash
nano templates/xray_server_multi.json.j2
```

### Adding New Variables
1. Add the variable to `templates/env_multi.j2`
2. Update the `get_env_vars()` method in `src/config_generator.py`
3. Use the variable in the necessary templates

## Regeneration After Changes

After changing templates, you need to regenerate configurations:

```bash
# Regenerate all configurations
docker-compose --profile tools run --rm config-generator init \
  --domain your-domain.com \
  --email your@email.com \
  --server-ip your-ip

# Restart services
docker-compose restart
```

## Template Validation

### JSON Templates
To check the correctness of JSON templates, you can use:
```bash
# Generate and validate JSON
docker-compose --profile tools run --rm config-generator generate
```

### Nginx Templates
To check the nginx-proxy configuration:
```bash
# Check generated configuration
docker-compose exec nginx-proxy nginx -t
```

## Usage Examples

### Creating a Custom Location Block
```nginx
# Add to templates/nginx_custom.conf.j2
location /custom/path {
    proxy_pass http://xray-server:10001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### Usage in Code
```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('nginx_custom.conf.j2')
content = template.render(domain='example.com')
```

## Debugging nginx-proxy

### Checking Environment Variables
```bash
# Check container variables
docker-compose exec demo-website env | grep -E "(VIRTUAL_HOST|LETSENCRYPT)"
```

### Checking Generated Configurations

```bash
# View generated nginx-proxy configurations
docker-compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf
```

### nginx-proxy Logs

```bash
# nginx-proxy logs
docker-compose logs nginx-proxy

# acme-companion logs
docker-compose logs acme-companion
```

## Best Practices

1. **Do not modify generated files** - always edit templates
2. **Backup** customized templates
3. **Test changes** before applying them in production
4. **Use variables** instead of hardcoding values
5. **Document changes** in template comments
6. **Monitor nginx-proxy and acme-companion logs** for SSL debugging
7. **Check container environment variables** for correct automation operation
```