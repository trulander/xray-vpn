#!/bin/bash

set -e

echo "Automatic Xray VPN Server Deployment"
echo "================================================"

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <domain> [email] [server-ip]"
    echo "Example: $0 vpn.example.com admin@example.com 203.0.113.10"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-"admin@$DOMAIN"}
SERVER_IP=${3:-$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "127.0.0.1")}

echo "Deployment parameters:"
echo "   Domain: $DOMAIN"
echo "   Email: $EMAIL"
echo "   Server IP: $SERVER_IP"
echo

# Create directories
echo "Creating directories..."
mkdir -p config/{xray,nginx,client} data/{www,ssl,xray/logs}

# Rebuild config-generator image to apply fixes
echo "Rebuilding config-generator image..."
docker-compose build config-generator

# Generate configurations
echo "Generating configurations..."
docker-compose --profile tools run --rm config-generator init --domain "$DOMAIN" --email "$EMAIL" --server-ip "$SERVER_IP"

# Check if the correct file is created
if [ -f "config/nginx/${DOMAIN}_location" ]; then
    echo "Custom configuration created: ${DOMAIN}_location"
else
    echo "Custom configuration not found, check logs"
fi

# Start services
echo "Starting services..."
docker-compose up -d --remove-orphans

# Check status
echo "Checking service status..."
sleep 5
docker-compose ps

echo
echo "Basic deployment complete!"
echo
echo "Next steps:"
echo "1. Configure DNS: $DOMAIN → Your server's IP"
echo "2. SSL certificates will be obtained automatically (wait 2-5 minutes)"
echo "3. Check website: curl -I https://$DOMAIN"
echo

# Get secret path from .env file
SECRET_PATH=$(grep "SECRET_CONFIG_PATH=" .env | cut -d'=' -f2)
if [ -n "$SECRET_PATH" ]; then
    echo "Secret configurations page:"
    echo "   https://$DOMAIN$SECRET_PATH"
    echo "   Save this link in a safe place!"
    echo
fi

echo "Management:"
echo "   - Status: docker-compose ps"
echo "   - Logs: docker-compose logs nginx-proxy acme-companion"
echo "   - Diagnostics: ./scripts/diagnose-ssl.sh"
echo "   - Testing: ./scripts/test_connections.sh"
echo "   - Stop: docker-compose down"