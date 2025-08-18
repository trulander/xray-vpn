[ru](../../docs/ru/nginx-proxy-architecture.md)

# Nginx-proxy + Acme-companion Architecture

## Overview

We use a combination of nginx-proxy and acme-companion for automatic SSL certificate management and traffic proxying.

## Components

### 1. nginx-proxy
**Container:** `nginxproxy/nginx-proxy:latest`

**Functions:**
- Automatically detects containers with the `VIRTUAL_HOST` variable
- Generates virtual hosts for each domain
- Proxies traffic to the corresponding containers
- Handles SSL termination

**How it works:**
1. Monitors Docker events via `/var/run/docker.sock`
2. Finds containers with `VIRTUAL_HOST=example.com`
3. Automatically creates nginx configuration
4. Proxies all traffic to this container

### 2. acme-companion
**Container:** `nginxproxy/acme-companion:latest`

**Functions:**
- Automatically obtains SSL certificates from Let's Encrypt
- Renews certificates every 12 hours
- Integrates with nginx-proxy

**How it works:**
1. Monitors containers with `LETSENCRYPT_HOST=example.com`
2. Uses ACME challenge via HTTP-01
3. Saves certificates to `/etc/nginx/certs`
4. Reloads nginx-proxy upon renewal

## Environment Variables

### Required for containers:
```bash
VIRTUAL_HOST=example.com        # Domain for nginx-proxy
LETSENCRYPT_HOST=example.com    # Domain for SSL certificate
LETSENCRYPT_EMAIL=admin@example.com  # Email for Let's Encrypt
```

### Nginx-proxy settings:
```bash
DEFAULT_HOST=example.com        # Default domain
TRUST_DOWNSTREAM_PROXY=false   # Do not trust headers from proxy
```

## File Structure

### Certificates
```
data/ssl/
├── live/
│   └── example.com/
│       ├── fullchain.pem      # Full certificate chain
│       ├── privkey.pem        # Private key
│       ├── cert.pem           # Primary certificate
│       └── chain.pem          # Intermediate certificates
└── accounts/                  # Let's Encrypt accounts
```

### Custom configurations
```
config/nginx/
├── example.com_location       # Custom location blocks for the domain
├── example.com_server         # Custom server settings for the domain
└── example.com               # Full virtual host replacement
```

## Customization

### Adding location blocks

File `config/nginx/example.com_location`:
```nginx
# VPN routes
location /api/v1/vmess {
    proxy_pass http://xray-server:10001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### Adding server settings

File `config/nginx/example.com_server`:
```nginx
# Additional server settings
client_max_body_size 50M;
proxy_read_timeout 300s;
```

### Full virtual host replacement

File `config/nginx/example.com`:
```nginx
server {
    listen 443 ssl http2;
    server_name example.com;
    
    # Full custom configuration
}
```

## Automatic Processes

### Certificate acquisition
1. **First run:** acme-companion detects `LETSENCRYPT_HOST`
2. **HTTP challenge:** Creates a temporary file in `/.well-known/acme-challenge/`
3. **Verification:** Let's Encrypt verifies the file via HTTP
4. **Certificate:** Saved to `data/ssl/live/domain/`
5. **Reload:** nginx-proxy reloads with new certificates

### Certificate renewal
- **Automatically:** Every 12 hours
- **Check:** 30 days before expiration
- **Renew:** If expiration is less than 30 days away
- **Reload:** nginx-proxy automatically reloads

## Troubleshooting

### Certificates not being obtained

1. **Check DNS:** Domain must point to the server
2. **Check port 80:** Must be accessible from outside
3. **Check logs:** `docker-compose logs acme-companion`
4. **Check variables:** `LETSENCRYPT_HOST` must match `VIRTUAL_HOST`

### HTTPS not working (502 error)

1. **Check container status:** `docker-compose ps`
2. **Check custom configurations:** Files in `config/nginx/`
3. **Check nginx-proxy logs:** `docker-compose logs nginx-proxy`
4. **Check backend accessibility:** nginx-proxy must be able to reach the container

### Custom locations not working

1. **Correct file name:** `{domain}_location`
2. **Correct syntax:** Valid nginx configuration
3. **Restart:** `docker-compose restart nginx-proxy`
4. **Check mounting:** Volume must be connected

## Logs and Monitoring

### Viewing logs
```bash
# nginx-proxy
docker-compose logs nginx-proxy

# acme-companion
docker-compose logs acme-companion

# All at once
docker-compose logs nginx-proxy acme-companion
```

### Checking generated configurations
```bash
# Main configuration
docker-compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf

# Custom configurations
docker-compose exec nginx-proxy ls -la /etc/nginx/vhost.d/

# Certificates
docker-compose exec nginx-proxy ls -la /etc/nginx/certs/
```

## Advantages of the approach

- Automation: SSL certificates are obtained and renewed automatically
- Simplicity: No need to configure nginx manually
- Reliability: Proven solution with active support
- Scalability: Easy to add new domains
- Security: Modern SSL settings by default

## Limitations

- HTTP-01 challenge: Requires port 80 accessibility
- Wildcard certificates: Requires DNS-01 challenge (more complex setup)
- Customization: Limited nginx configuration options
- Dependency: On Docker socket and internet connection