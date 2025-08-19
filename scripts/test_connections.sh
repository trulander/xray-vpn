#!/bin/bash

echo "Testing Xray VPN Server (multi-protocol architecture)"
echo "================================================================="

# Load environment variables
if [ -f .env ]; then
    source .env
    echo "Configuration:"
    echo "   Domain: ${DOMAIN:-not set}"
    echo "   Email: ${EMAIL:-not set}"
else
    echo ".env file not found"
    exit 1
fi
echo

# Check main website
echo "1. Checking main website:"
echo "HTTP (should redirect to HTTPS):"
curl -s -I "http://localhost" 2>/dev/null | head -3 || curl -s -I "http://${DOMAIN}" 2>/dev/null | head -3 || echo "HTTP unavailable"

echo "HTTPS (should show demo site):"
curl -s -I "https://localhost" 2>/dev/null | head -3 || curl -s -I "https://${DOMAIN}" 2>/dev/null | head -3 || echo "HTTPS unavailable"
echo

# Check VPN paths (should return errors for regular HTTP requests)
echo "2. Checking VPN paths (random paths from configuration):"

# Read configuration if available
if [ -f "config/nginx/${DOMAIN}_location" ]; then
    echo "Analyzing custom location blocks:"
    
    # Extract paths from configuration
    WS_PATHS=$(grep -o "location [^{]*" "config/nginx/${DOMAIN}_location" | grep -v grpc | cut -d' ' -f2)
    GRPC_PATHS=$(grep -o "location [^{]*" "config/nginx/${DOMAIN}_location" | grep grpc | cut -d' ' -f2)
    
    echo "WebSocket paths:"
    for path in $WS_PATHS; do
        if [[ "$path" != *"grpc"* ]]; then
            echo "  Testing $path:"
            curl -s -I "https://localhost$path" 2>/dev/null | head -1 || curl -s -I "https://${DOMAIN}$path" 2>/dev/null | head -1 || echo "    Path unavailable"
        fi
    done
    
    echo "gRPC paths:"
    for path in $GRPC_PATHS; do
        echo "  Testing $path:"
        curl -s -I "https://localhost$path" 2>/dev/null | head -1 || curl -s -I "https://${DOMAIN}$path" 2>/dev/null | head -1 || echo "    Path unavailable"
    done
else
    echo "Nginx configuration file not found: config/nginx/${DOMAIN}_location"
    echo "   Testing standard paths for demonstration:"
    
    # Examples of standard paths
    TEST_PATHS=(
        "/api/v1/vmess"
        "/ws/vless" 
        "/stream/trojan"
        "/vmess/grpc"
        "/vless/grpc"
        "/trojan/grpc"
    )
    
    for path in "${TEST_PATHS[@]}"; do
        echo "  Testing $path:"
        curl -s -I "https://localhost$path" 2>/dev/null | head -1 || echo "    Path unavailable"
    done
fi
echo

# Check Docker container status
echo "3. Docker container status:"
docker-compose ps
echo

# Check Xray server internal ports
echo "4. Checking Xray server internal ports:"
if docker-compose ps | grep -q "xray-server.*Up"; then
    echo "WebSocket ports:"
    docker-compose exec nginx-proxy nc -z xray-server 10001 && echo "  VMess WS: 10001" || echo "  VMess WS: 10001 (unavailable)"
    docker-compose exec nginx-proxy nc -z xray-server 10002 && echo "  VLESS WS: 10002" || echo "  VLESS WS: 10002 (unavailable)"
    docker-compose exec nginx-proxy nc -z xray-server 10003 && echo "  Trojan WS: 10003" || echo "  Trojan WS: 10003 (unavailable)"
    
    echo "gRPC ports:"
    docker-compose exec nginx-proxy nc -z xray-server 10011 && echo "  VMess gRPC: 10011" || echo "  VMess gRPC: 10011 (unavailable)"
    docker-compose exec nginx-proxy nc -z xray-server 10012 && echo "  VLESS gRPC: 10012" || echo "  VLESS gRPC: 10012 (unavailable)"
    docker-compose exec nginx-proxy nc -z xray-server 10013 && echo "  Trojan gRPC: 10013" || echo "  Trojan gRPC: 10013 (unavailable)"
else
    echo "Xray server is not running"
fi
echo

# Check environment variables for automatic SSL
echo "5. Checking automatic SSL settings:"
docker-compose exec demo-website env | grep -E "(VIRTUAL_HOST|LETSENCRYPT)" || echo "Environment variables not found"
echo

# Check certificates
echo "6. SSL certificates:"
if [ -d "data/ssl" ]; then
    cert_count=$(find data/ssl -name "*.crt" -o -name "*.pem" | wc -l)
    echo "Found $cert_count certificate files in data/ssl/"
    
    if [ -f "data/ssl/${DOMAIN}.crt" ]; then
        echo "nginx-proxy certificate for ${DOMAIN} found"
    elif [ -d "data/ssl/live/${DOMAIN}" ]; then
        echo "Let's Encrypt certificate for ${DOMAIN} found"
    else
        echo "Certificate for ${DOMAIN} not found (may be obtained automatically)"
    fi
else
    echo "data/ssl folder does not exist"
fi
echo

# Check logs (errors only)
echo "7. Checking logs for errors:"
echo "nginx-proxy errors:"
docker-compose logs nginx-proxy 2>/dev/null | grep -i error | tail -3 || echo "  No errors found"

echo "acme-companion errors:"
docker-compose logs acme-companion 2>/dev/null | grep -i error | tail -3 || echo "  No errors found"

echo "xray-server errors:"
docker-compose logs xray-server 2>/dev/null | grep -i error | tail -3 || echo "  No errors found"
echo

echo "Testing complete!"
echo

# Secret page information
if [ -n "$SECRET_CONFIG_PATH" ]; then
    echo "Secret configurations page:"
    echo "   https://${DOMAIN}${SECRET_CONFIG_PATH}"
    echo "   This link contains your personal VPN configurations!"
    echo
fi

echo "Client configurations available in:"
if [ -d "config/client" ]; then
    ls -1 config/client/*.json 2>/dev/null | while read file; do
        echo "  $file"
    done
else
    echo "  config/client folder not found"
    echo "  Run: docker-compose --profile tools run --rm config-generator generate"
fi
echo
echo "Management:"
echo "  - Status: docker-compose ps"
echo "  - Logs: docker-compose logs nginx-proxy acme-companion xray-server"
echo "  - Diagnostics: ./scripts/diagnose-ssl.sh"
echo "  - Restart: docker-compose restart"
echo
echo "To generate URL for mobile applications:"
echo "  docker-compose --profile tools run --rm config-generator generate-client vless ws -u"