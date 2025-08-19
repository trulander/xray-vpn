#!/bin/bash

echo "Diagnosing nginx-proxy and SSL certificates"
echo "================================================"

# Check environment variables
echo "1. Checking environment variables:"
if [ -f .env ]; then
    echo ".env file exists"
    source .env
    echo "   Domain: ${DOMAIN:-not set}"
    echo "   Email: ${EMAIL:-not set}"
    echo "   Server IP: ${SERVER_IP:-not set}"
else
    echo ".env file not found"
fi
echo

# Check status of nginx-proxy architecture containers
echo "2. Container status:"
docker-compose ps
echo

# Check demo-website container environment variables
echo "3. demo-website environment variables:"
docker-compose exec demo-website env | grep -E "(VIRTUAL_HOST|LETSENCRYPT)" || echo "demo-website container is not running"
echo

# Check certificates in the new nginx-proxy structure
echo "4. SSL certificates (nginx-proxy structure):"
if [ -d "data/ssl" ]; then
    echo "data/ssl folder exists"
    if [ -n "${DOMAIN}" ]; then
        # Check nginx-proxy structure
        if [ -f "data/ssl/${DOMAIN}.crt" ] && [ -f "data/ssl/${DOMAIN}.key" ]; then
            echo "nginx-proxy certificates for ${DOMAIN} found:"
            ls -la "data/ssl/${DOMAIN}.*" 2>/dev/null
        elif [ -d "data/ssl/live/${DOMAIN}" ]; then
            echo "Let's Encrypt certificates for ${DOMAIN} found:"
            ls -la "data/ssl/live/${DOMAIN}/" 2>/dev/null
        else
            echo "Certificates for domain ${DOMAIN} not found"
            echo "   Contents of data/ssl:"
            ls -la data/ssl/ 2>/dev/null | head -10 || echo "   Folder is empty"
        fi
    else
        echo "Domain not set in environment variables"
    fi
else
    echo "data/ssl folder does not exist"
fi
echo

# Check custom nginx-proxy configurations
echo "5. Custom nginx-proxy configurations:"
if [ -n "${DOMAIN}" ] && [ -f "config/nginx/${DOMAIN}_location" ]; then
    echo "Custom configuration ${DOMAIN}_location exists"
    echo "   Size: $(wc -l < config/nginx/${DOMAIN}_location) lines"
else
    echo "Custom configuration ${DOMAIN}_location not found"
    echo "   Contents of config/nginx/:"
    ls -la config/nginx/ 2>/dev/null || echo "   Folder does not exist"
fi
echo

# Check nginx-proxy logs
echo "6. nginx-proxy logs (last 10 lines):"
docker-compose logs --tail=10 nginx-proxy 2>/dev/null || echo "nginx-proxy container is not running"
echo

# Check acme-companion logs
echo "7. acme-companion logs (last 10 lines):"
docker-compose logs --tail=10 acme-companion 2>/dev/null || echo "acme-companion container is not running"
echo

# Check generated nginx-proxy configuration
echo "8. Generated nginx-proxy configuration:"
docker-compose exec nginx-proxy cat /etc/nginx/conf.d/default.conf 2>/dev/null | head -20 || echo "Failed to get configuration"
echo

# Check Xray server availability
echo "9. Checking Xray server availability:"
docker-compose exec nginx-proxy nc -z xray-server 10001 && echo "VMess WS port 10001 available" || echo "VMess WS port 10001 unavailable"
docker-compose exec nginx-proxy nc -z xray-server 10002 && echo "VLESS WS port 10002 available" || echo "VLESS WS port 10002 unavailable"
docker-compose exec nginx-proxy nc -z xray-server 10003 && echo "Trojan WS port 10003 available" || echo "Trojan WS port 10003 unavailable"
docker-compose exec nginx-proxy nc -z xray-server 10011 && echo "VMess gRPC port 10011 available" || echo "VMess gRPC port 10011 unavailable"
docker-compose exec nginx-proxy nc -z xray-server 10012 && echo "VLESS gRPC port 10012 available" || echo "VLESS gRPC port 10012 unavailable"
docker-compose exec nginx-proxy nc -z xray-server 10013 && echo "Trojan gRPC port 10013 available" || echo "Trojan gRPC port 10013 unavailable"
echo

# Check demo-website
echo "10. Checking demo-website:"
docker-compose exec nginx-proxy nc -z demo-website 80 && echo "Demo website available" || echo "Demo website unavailable"
echo

# Check HTTP/HTTPS
echo "11. Checking HTTP/HTTPS:"
echo "HTTP (should redirect to HTTPS):"
curl -s -I http://localhost 2>/dev/null | head -3 || echo "HTTP unavailable"
echo

echo "HTTPS:"
curl -s -I -k https://localhost 2>/dev/null | head -3 || echo "HTTPS unavailable"
echo

# Check DNS (if domain is set)
if [ -n "${DOMAIN}" ] && [ "${DOMAIN}" != "example.com" ]; then
    echo "12. Checking DNS:"
    echo "Resolving domain ${DOMAIN}:"
    nslookup "${DOMAIN}" 2>/dev/null | grep -A 1 "Name:" || dig +short "${DOMAIN}" 2>/dev/null || echo "Failed to resolve domain"
    echo
fi

echo "Recommendations for nginx-proxy architecture:"
echo "1. Ensure DNS is configured: ${DOMAIN} → Server IP"
echo "2. Check logs: docker-compose logs nginx-proxy acme-companion"
echo "3. Environment variables: VIRTUAL_HOST, LETSENCRYPT_HOST, LETSENCRYPT_EMAIL"
echo "4. SSL certificates are obtained automatically (wait up to 5 minutes)"
echo "5. To restart: docker-compose restart"
echo "6. Custom location blocks: config/nginx/${DOMAIN}_location"