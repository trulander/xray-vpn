#!/usr/bin/env python3
"""
Xray VPN Server - Configuration Generator
Supports multiple protocols: VMess, VLESS, Trojan
Transports: WebSocket, gRPC
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any

# Add path to modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_generator import ConfigGenerator
from key_generator import KeyGenerator
from utils import setup_logging, check_dependencies, create_directories


def init_project(args: argparse.Namespace) -> None:
    """Initialize project with key and configuration generation"""
    
    domain = args.domain
    email = args.email or f"admin@{domain}"
    server_ip = args.server_ip
    
    print("Initializing Xray VPN Server...")
    print(f"Domain: {domain}")
    print(f"Email: {email}")
    print(f"Server IP: {server_ip}")
    
    # Check dependencies
    if not check_dependencies():
        print("Not all dependencies are installed")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Generate keys
    key_gen = KeyGenerator()
    config_gen = ConfigGenerator()
    
    # Get existing variables or generate new ones
    env_vars = config_gen.get_env_vars()
    
    # Set domain, email, and server IP
    env_vars['domain'] = domain
    env_vars['email'] = email
    env_vars['server_ip'] = server_ip
    
    # Generate new keys if they are not set
    if not env_vars['vmess_uuid']:
        env_vars['vmess_uuid'] = key_gen.generate_uuid()
        print(f"Generated VMess UUID: {env_vars['vmess_uuid']}")
    
    if not env_vars['vless_uuid']:
        env_vars['vless_uuid'] = key_gen.generate_uuid()
        print(f"Generated VLESS UUID: {env_vars['vless_uuid']}")
    
    if not env_vars['trojan_password']:
        env_vars['trojan_password'] = key_gen.generate_trojan_password()
        print(f"Generated Trojan password: {env_vars['trojan_password']}")
    
    # Generate paths if they are not set
    if not env_vars['vmess_ws_path'] or env_vars['vmess_ws_path'] == '/vmess/ws':
        env_vars['vmess_ws_path'] = key_gen.generate_ws_path('vmess')
        print(f"Generated VMess WS path: {env_vars['vmess_ws_path']}")
    
    if not env_vars['vless_ws_path'] or env_vars['vless_ws_path'] == '/vless/ws':
        env_vars['vless_ws_path'] = key_gen.generate_ws_path('vless')
        print(f"Generated VLESS WS path: {env_vars['vless_ws_path']}")
    
    if not env_vars['trojan_ws_path'] or env_vars['trojan_ws_path'] == '/trojan/ws':
        env_vars['trojan_ws_path'] = key_gen.generate_ws_path('trojan')
        print(f"Generated Trojan WS path: {env_vars['trojan_ws_path']}")
    
    # Generate gRPC services if they are not set
    used_grpc_paths = set()
    used_grpc_services = set()
    
    # Account for already existing values
    if env_vars['vmess_grpc_path'] and env_vars['vmess_grpc_path'] != '/vmess/grpc':
        used_grpc_paths.add(env_vars['vmess_grpc_path'])
    if env_vars['vmess_grpc_service'] and env_vars['vmess_grpc_service'] != 'VmessService':
        used_grpc_services.add(env_vars['vmess_grpc_service'])
    if env_vars['vless_grpc_path'] and env_vars['vless_grpc_path'] != '/vless/grpc':
        used_grpc_paths.add(env_vars['vless_grpc_path'])
    if env_vars['vless_grpc_service'] and env_vars['vless_grpc_service'] != 'VlessService':
        used_grpc_services.add(env_vars['vless_grpc_service'])
    if env_vars['trojan_grpc_path'] and env_vars['trojan_grpc_path'] != '/trojan/grpc':
        used_grpc_paths.add(env_vars['trojan_grpc_path'])
    if env_vars['trojan_grpc_service'] and env_vars['trojan_grpc_service'] != 'TrojanService':
        used_grpc_services.add(env_vars['trojan_grpc_service'])
    
    if not env_vars['vmess_grpc_service'] or env_vars['vmess_grpc_service'] == 'VmessService':
        env_vars['vmess_grpc_service'] = key_gen.generate_grpc_service_name('vmess')
        env_vars['vmess_grpc_path'] = key_gen.generate_grpc_path(env_vars['vmess_grpc_service'])
        used_grpc_paths.add(env_vars['vmess_grpc_path'])
        used_grpc_services.add(env_vars['vmess_grpc_service'])
        print(f"Generated VMess gRPC service: {env_vars['vmess_grpc_service']}")
    
    if not env_vars['vless_grpc_service'] or env_vars['vless_grpc_service'] == 'VlessService':
        # Regenerate if path/service is already in use
        attempts = 0
        while attempts < 10:
            service_name = key_gen.generate_grpc_service_name('vless')
            service_path = key_gen.generate_grpc_path(service_name)
            if service_path not in used_grpc_paths and service_name not in used_grpc_services:
                env_vars['vless_grpc_service'] = service_name
                env_vars['vless_grpc_path'] = service_path
                used_grpc_paths.add(service_path)
                used_grpc_services.add(service_name)
                break
            attempts += 1
        print(f"Generated VLESS gRPC service: {env_vars['vless_grpc_service']}")
    
    if not env_vars['trojan_grpc_service'] or env_vars['trojan_grpc_service'] == 'TrojanService':
        # Regenerate if path/service is already in use
        attempts = 0
        while attempts < 10:
            service_name = key_gen.generate_grpc_service_name('trojan')
            service_path = key_gen.generate_grpc_path(service_name)
            if service_path not in used_grpc_paths and service_name not in used_grpc_services:
                env_vars['trojan_grpc_service'] = service_name
                env_vars['trojan_grpc_path'] = service_path
                used_grpc_paths.add(service_path)
                used_grpc_services.add(service_name)
                break
            attempts += 1
        print(f"Generated Trojan gRPC service: {env_vars['trojan_grpc_service']}")
    
    # Generate secret path if it is not set
    if not env_vars['secret_config_path'] or env_vars['secret_config_path'] == '/secret/configs':
        env_vars['secret_config_path'] = key_gen.generate_secret_path()
        print(f"Generated secret path: {env_vars['secret_config_path']}")
    
    # Save .env file
    env_content = config_gen.env.get_template('env_multi.j2').render(**env_vars)
    
    env_path = '/app/workspace/.env' if Path('/app/workspace').exists() else '.env'
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("File .env created/updated")
    
    # Reload environment variables in existing ConfigGenerator
    config_gen.reload_env_vars()
    
    # Generate all configurations
    config_gen.generate_all_configs()
    print("All configurations generated")
    
    print("\nInitialization complete!")
    print(f"\nProject ready for domain: {domain}")
    print("\nTo start, run:")
    print("   docker-compose up -d")


def generate_configs(args: argparse.Namespace) -> None:
    """Generate configurations"""
    
    print("Generating configurations...")
    
    config_gen = ConfigGenerator()
    # Reload environment variables to use current values
    config_gen.reload_env_vars()
    config_gen.generate_all_configs()
    
    print("Configurations generated in config/ folder")


def generate_client_config(args: argparse.Namespace) -> None:
    """Generate client configuration"""
    
    config_gen = ConfigGenerator()
    
    try:
        # Generate JSON configuration
        client_config = config_gen.generate_client_config(
            protocol=args.protocol,
            transport=args.transport
        )
        
        # Save to file
        config_dir = Path('config/client')
        config_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f'{args.protocol}_{args.transport}.json'
        filepath = config_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(client_config)
        
        print(f"Client configuration saved: {filepath}")
        
        # Generate URL for mobile applications
        if args.url:
            try:
                if args.protocol == 'vless':
                    url = config_gen.generate_vless_url(transport=args.transport)
                elif args.protocol == 'vmess':
                    url = config_gen.generate_vmess_url(transport=args.transport)
                elif args.protocol == 'trojan':
                    url = config_gen.generate_trojan_url(transport=args.transport)
                else:
                    raise ValueError(f"URL generation is not supported for protocol {args.protocol}")
                
                print(f"\nURL for mobile application:")
                print(url)
                
                # Save URL to file
                url_file = config_dir / f'{args.protocol}_{args.transport}_url.txt'
                with open(url_file, 'w', encoding='utf-8') as f:
                    f.write(url)
                
                print(f"URL saved to file: {url_file}")
                
            except Exception as e:
                print(f"Error generating URL: {e}")
        
    except Exception as e:
        print(f"Error generating client configuration: {e}")
        sys.exit(1)


def show_status(args: argparse.Namespace) -> None:
    """Show server status"""
    
    print("Xray VPN Server Status")
    print("=" * 50)
    
    # Check configuration files
    config_files = [
        'config/xray/config.json',
        'config/nginx/nginx.conf',
        'config/nginx/demo-site.conf',
        '.env'
    ]
    
    print("\nConfiguration files:")
    for file_path in config_files:
        if Path(file_path).exists():
            print(f"  {file_path}")
        else:
            print(f"  {file_path} (missing)")
    
    # Check client configurations
    client_dir = Path('config/client')
    if client_dir.exists():
        client_configs = list(client_dir.glob('*.json'))
        print(f"\nClient configurations ({len(client_configs)}):")
        for config_file in client_configs:
            print(f"  {config_file.name}")
    else:
        print("\nClient configurations: not found")
    
    # Check environment variables
    config_gen = ConfigGenerator()
    env_vars = config_gen.get_env_vars()
    
    print("\nMain settings:")
    print(f"  Domain: {env_vars['domain']}")
    print(f"  Server IP: {env_vars['server_ip']}")
    print(f"  Email: {env_vars['email']}")
    print(f"  Logging level: {env_vars['log_level']}")
    
    print("\nProtocols:")
    print(f"  VMess UUID: {env_vars['vmess_uuid'][:8]}...")
    print(f"  VLESS UUID: {env_vars['vless_uuid'][:8]}...")
    print(f"  Trojan password: {env_vars['trojan_password'][:8]}...")


def show_ssl_status(args: argparse.Namespace) -> None:
    """Show SSL certificate status"""
    
    print("SSL Certificate Status")
    print("=" * 50)
    
    config_gen = ConfigGenerator()
    env_vars = config_gen.get_env_vars()
    domain = env_vars['domain']
    
    ssl_dir = Path(f'data/ssl/live/{domain}')
    
    if ssl_dir.exists():
        cert_files = ['fullchain.pem', 'privkey.pem', 'cert.pem', 'chain.pem']
        
        print(f"\nCertificates for domain {domain}:")
        for cert_file in cert_files:
            cert_path = ssl_dir / cert_file
            if cert_path.exists():
                print(f"  {cert_file}")
            else:
                print(f"  {cert_file} (missing)")
        
        # Check certificate expiration date
        cert_path = ssl_dir / 'cert.pem'
        if cert_path.exists():
            try:
                import subprocess
                result = subprocess.run([
                    'openssl', 'x509', '-in', str(cert_path), '-noout', '-dates'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"\nCertificate Information:")
                    for line in result.stdout.strip().split('\n'):
                        print(f"  {line}")
                
            except Exception as e:
                print(f"Could not check certificate expiration date: {e}")
    else:
        print(f"\nCertificates for domain {domain} not found")
        print("\nTo obtain a certificate, run:")
        print(f"docker-compose --profile tools run --rm certbot certonly --webroot -w /var/www/html -d {domain}")


def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(
        description='Xray VPN Server - Configuration Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  python -m src.main init                           # Initialize project
  python -m src.main generate                       # Generate all configurations
  python -m src.main generate-client vless ws       # Generate VLESS WebSocket client configuration
  python -m src.main generate-client vmess grpc -u  # Generate VMess gRPC with URL
  python -m src.main status                         # Show status
  python -m src.main ssl-status                     # Show SSL status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize project')
    init_parser.add_argument('--domain', required=True, help='Server domain (e.g.: vpn.example.com)')
    init_parser.add_argument('--email', help='Email for Let\'s Encrypt (default: admin@domain)')
    init_parser.add_argument('--server-ip', '-i', required=True, help='Server IP address')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate all configurations')
    
    # Generate-client command
    client_parser = subparsers.add_parser('generate-client', help='Generate client configuration')
    client_parser.add_argument('protocol', choices=['vmess', 'vless', 'trojan'], help='Protocol')
    client_parser.add_argument('transport', choices=['ws', 'grpc'], help='Transport')
    client_parser.add_argument('-u', '--url', action='store_true', help='Generate URL for mobile applications')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show server status')
    
    # Ssl-status command
    ssl_parser = subparsers.add_parser('ssl-status', help='Show SSL certificate status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Configure logging
    setup_logging()
    
    # Execute commands
    if args.command == 'init':
        init_project(args)
    elif args.command == 'generate':
        generate_configs(args)
    elif args.command == 'generate-client':
        generate_client_config(args)
    elif args.command == 'status':
        show_status(args)
    elif args.command == 'ssl-status':
        show_ssl_status(args)


if __name__ == '__main__':
    main()