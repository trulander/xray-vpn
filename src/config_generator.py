"""
Configuration generator for Xray and Nginx (multi-protocol architecture with nginx-proxy)
"""

import urllib.parse
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any
from dotenv import load_dotenv

from key_generator import KeyGenerator


class ConfigGenerator:
    """Configuration generator for VPN server with nginx-proxy architecture"""
    
    def __init__(self):
        # First, try to load the .env file (if it exists)
        env_path = '/app/workspace/.env' if Path('/app/workspace/.env').exists() else '.env'
        if Path(env_path).exists():
            load_dotenv(env_path)
        
        self.key_gen = KeyGenerator()
        
        # Define the path to templates (always in the container /app/workspace/templates)
        templates_path = '/app/workspace/templates' if Path('/app/workspace/.env').exists() else 'templates'
        self.env = Environment(loader=FileSystemLoader(templates_path))
    
    def reload_env_vars(self):
        """Force reload environment variables from .env file"""
        env_path = '/app/workspace/.env' if Path('/app/workspace/.env').exists() else '.env'
        if Path(env_path).exists():
            load_dotenv(env_path, override=True)
    
    def get_env_vars(self) -> Dict[str, Any]:
        """Get environment variables"""
        return {
            # Main settings
            'domain': os.getenv('DOMAIN', 'example.com'),
            'server_ip': os.getenv('SERVER_IP', 'YOUR_SERVER_IP'),
            'email': os.getenv('EMAIL', 'admin@example.com'),
            
            # UUID for protocols
            'vmess_uuid': os.getenv('VMESS_UUID') or '',
            'vless_uuid': os.getenv('VLESS_UUID') or '',
            
            # Password for Trojan
            'trojan_password': os.getenv('TROJAN_PASSWORD') or '',
            
            # Paths for WebSocket
            'vmess_ws_path': os.getenv('VMESS_WS_PATH') or '/vmess/ws',
            'vless_ws_path': os.getenv('VLESS_WS_PATH') or '/vless/ws',
            'trojan_ws_path': os.getenv('TROJAN_WS_PATH') or '/trojan/ws',
            
            # Paths for gRPC
            'vmess_grpc_path': os.getenv('VMESS_GRPC_PATH') or '/vmess/grpc',
            'vless_grpc_path': os.getenv('VLESS_GRPC_PATH') or '/vless/grpc',
            'trojan_grpc_path': os.getenv('TROJAN_GRPC_PATH') or '/trojan/grpc',
            
            # Services for gRPC
            'vmess_grpc_service': os.getenv('VMESS_GRPC_SERVICE') or 'VmessService',
            'vless_grpc_service': os.getenv('VLESS_GRPC_SERVICE') or 'VlessService',
            'trojan_grpc_service': os.getenv('TROJAN_GRPC_SERVICE') or 'TrojanService',
            
            # Secret configuration page
            'secret_config_path': os.getenv('SECRET_CONFIG_PATH') or '/secret/configs',
            
            # Logging settings
            'log_level': os.getenv('LOG_LEVEL', 'warning'),
            'enable_stats': os.getenv('ENABLE_STATS', 'false').lower() == 'true',
            
            # Docker settings
            'uid': os.getenv('UID', '1000'),
            'gid': os.getenv('GID', '1000')
        }
    
    def generate_xray_server_config(self) -> str:
        """Generate Xray server configuration with multiple protocols"""
        vars = self.get_env_vars()
        template = self.env.get_template('xray_server_multi.json.j2')
        return template.render(**vars)
    
    def generate_client_config(self, protocol: str = 'vless', transport: str = 'ws') -> str:
        """Generate client configuration for the specified protocol and transport"""
        vars = self.get_env_vars()
        
        template_name = f'client_{protocol}_{transport}.json.j2'
        
        try:
            template = self.env.get_template(template_name)
            return template.render(**vars)
        except Exception as e:
            raise ValueError(f"Unsupported protocol {protocol} and transport {transport} combination: {e}")
    
    def generate_all_client_configs(self) -> Dict[str, str]:
        """Generate all client configurations"""
        configs = {}
        
        protocols = ['vmess', 'vless', 'trojan']
        transports = ['ws', 'grpc']
        
        for protocol in protocols:
            for transport in transports:
                try:
                    config_name = f'{protocol}_{transport}'
                    configs[config_name] = self.generate_client_config(protocol=protocol, transport=transport)
                except ValueError:
                    # Skip unsupported combinations
                    continue
        
        return configs
    
    def generate_vless_url(self, transport: str = 'ws') -> str:
        """Generate VLESS URL for mobile applications"""
        vars = self.get_env_vars()
        
        if transport == 'ws':
            params = {
                'encryption': 'none',
                'security': 'tls',
                'sni': vars['domain'],
                'type': 'ws',
                'host': vars['domain'],
                'path': urllib.parse.quote(vars['vless_ws_path'])
            }
        elif transport == 'grpc':
            params = {
                'encryption': 'none',
                'security': 'tls',
                'sni': vars['domain'],
                'type': 'grpc',
                'serviceName': vars['vless_grpc_service']
            }
        else:
            raise ValueError(f"Unsupported transport: {transport}")
        
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        
        vless_url = f"vless://{vars['vless_uuid']}@{vars['domain']}:443?{param_string}#{urllib.parse.quote(f'Xray-VLESS-{transport.upper()}')}"
        
        return vless_url
    
    def generate_vmess_url(self, transport: str = 'ws') -> str:
        """Generate VMess URL for mobile applications"""
        vars = self.get_env_vars()
        
        if transport == 'ws':
            vmess_config = {
                'v': '2',
                'ps': f'Xray-VMess-{transport.upper()}',
                'add': vars['domain'],
                'port': '443',
                'id': vars['vmess_uuid'],
                'aid': '0',
                'scy': 'auto',
                'net': 'ws',
                'type': 'none',
                'host': vars['domain'],
                'path': vars['vmess_ws_path'],
                'tls': 'tls',
                'sni': vars['domain']
            }
        elif transport == 'grpc':
            vmess_config = {
                'v': '2',
                'ps': f'Xray-VMess-{transport.upper()}',
                'add': vars['domain'],
                'port': '443',
                'id': vars['vmess_uuid'],
                'aid': '0',
                'scy': 'auto',
                'net': 'grpc',
                'type': 'none',
                'host': vars['domain'],
                'path': vars['vmess_grpc_service'],
                'tls': 'tls',
                'sni': vars['domain']
            }
        else:
            raise ValueError(f"Unsupported transport: {transport}")
        
        import json
        import base64
        
        vmess_json = json.dumps(vmess_config, separators=(',', ':'))
        vmess_b64 = base64.b64encode(vmess_json.encode()).decode()
        
        return f"vmess://{vmess_b64}"
    
    def generate_trojan_url(self, transport: str = 'ws') -> str:
        """Generate Trojan URL for mobile applications"""
        vars = self.get_env_vars()
        
        if transport == 'ws':
            params = {
                'security': 'tls',
                'sni': vars['domain'],
                'type': 'ws',
                'host': vars['domain'],
                'path': urllib.parse.quote(vars['trojan_ws_path'])
            }
        elif transport == 'grpc':
            params = {
                'security': 'tls',
                'sni': vars['domain'],
                'type': 'grpc',
                'serviceName': vars['trojan_grpc_service']
            }
        else:
            raise ValueError(f"Unsupported transport: {transport}")
        
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        
        trojan_url = f"trojan://{vars['trojan_password']}@{vars['domain']}:443?{param_string}#{urllib.parse.quote(f'Xray-Trojan-{transport.upper()}')}"
        
        return trojan_url
    
    def generate_demo_site_config(self) -> str:
        """Generate demo site configuration"""
        vars = self.get_env_vars()
        template = self.env.get_template('demo_site.conf.j2')
        return template.render(**vars)
    
    def generate_nginx_domain_config(self) -> str:
        """Generate domain configuration for nginx-proxy with secret page"""
        vars = self.get_env_vars()
        template = self.env.get_template('nginx_domain.conf.j2')
        return template.render(**vars)
    
    def generate_nginx_custom_config(self) -> str:
        """Generate custom configuration for nginx-proxy"""
        vars = self.get_env_vars()
        template = self.env.get_template('nginx_custom.conf.j2')
        return template.render(**vars)
    
    def generate_config_page(self) -> str:
        """Generate HTML page for downloading configurations"""
        vars = self.get_env_vars()
        
        # Generate VMess Base64 for URL
        import json
        import base64
        
        vmess_config = {
            'v': '2',
            'ps': 'Xray-VMess-WS',
            'add': vars['domain'],
            'port': '443',
            'id': vars['vmess_uuid'],
            'aid': '0',
            'scy': 'auto',
            'net': 'ws',
            'type': 'none',
            'host': vars['domain'],
            'path': vars['vmess_ws_path'],
            'tls': 'tls',
            'sni': vars['domain']
        }
        
        vmess_json = json.dumps(vmess_config, separators=(',', ':'))
        vmess_b64 = base64.b64encode(vmess_json.encode()).decode()
        vars['vmess_b64_config'] = vmess_b64
        
        template = self.env.get_template('config_page.html.j2')
        return template.render(**vars)
    
    def generate_config_files(self) -> None:
        """Generate configuration files for the web page"""
        # In container always use /app, locally - current directory
        if Path('/app/workspace').exists():
            base_path = Path('/app')
        else:
            base_path = Path('.')
            
        # Create a separate directory for configurations outside www
        configs_dir = base_path / 'data' / 'secret-configs'
        configs_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate configuration page
        print("Generating configuration page...")
        config_page_content = self.generate_config_page()
        with open(configs_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(config_page_content)
        
        # Copy client configurations to the configs folder
        client_dir = base_path / 'config' / 'client'
        if client_dir.exists():
            print("Copying client configurations...")
            for config_file in client_dir.glob('*.json'):
                # Copy file to configs directory
                with open(config_file, 'r', encoding='utf-8') as src:
                    with open(configs_dir / config_file.name, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
        
        print(f"Secret page created in: {configs_dir}")
    
    def generate_website_files(self) -> None:
        """Generate website files"""
        vars = self.get_env_vars()
        
        # In container always use /app, locally - current directory
        if Path('/app/workspace').exists():
            base_path = Path('/app')
        else:
            base_path = Path('.')
            
        www_dir = base_path / 'data' / 'www'
        www_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate index.html
        template = self.env.get_template('index.html.j2')
        index_content = template.render(**vars)
        
        with open(www_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        # Generate robots.txt
        template = self.env.get_template('robots.txt.j2')
        robots_content = template.render(**vars)
        
        with open(www_dir / 'robots.txt', 'w', encoding='utf-8') as f:
            f.write(robots_content)
    
    def generate_all_configs(self) -> None:
        """Generate all configurations for nginx-proxy architecture"""
        
        # In container always use /app, locally - current directory  
        if Path('/app/workspace').exists():
            base_path = Path('/app')
        else:
            base_path = Path('.')
            
        config_dir = base_path / 'config'
        config_dir.mkdir(exist_ok=True)
        
        xray_dir = config_dir / 'xray'
        xray_dir.mkdir(exist_ok=True)
        
        nginx_dir = config_dir / 'nginx'
        nginx_dir.mkdir(exist_ok=True)
        
        client_dir = config_dir / 'client'
        client_dir.mkdir(exist_ok=True)
        
        print(f"Creating configurations in: {config_dir}")
        
        # Get domain to create correct file name
        vars = self.get_env_vars()
        domain = vars['domain']
        
        print(f"Generating for domain: {domain}")
        
        # Generate Xray server configuration
        print("Generating Xray server configuration...")
        xray_config = self.generate_xray_server_config()
        with open(xray_dir / 'config.json', 'w', encoding='utf-8') as f:
            f.write(xray_config)
        
        # Generate custom configuration for nginx-proxy
        print("Generating custom nginx-proxy configuration...")
        nginx_custom_config = self.generate_nginx_custom_config()
        
        # nginx-proxy looks for files in {domain}_location format
        location_file = nginx_dir / f'{domain}_location'
        with open(location_file, 'w', encoding='utf-8') as f:
            f.write(nginx_custom_config)
        print(f"File created: {location_file}")
        
        # Generate domain configuration with secret page
        print("Generating domain configuration with secret page...")
        nginx_domain_config = self.generate_nginx_domain_config()
        
        # nginx-proxy looks for files in {domain} format for the entire domain configuration
        domain_file = nginx_dir / domain
        with open(domain_file, 'w', encoding='utf-8') as f:
            f.write(nginx_domain_config)
        print(f"Domain file created: {domain_file}")
        
        # Generate demo site configuration
        print("Generating demo site configuration...")
        demo_site_config = self.generate_demo_site_config()
        with open(nginx_dir / 'demo-site.conf', 'w', encoding='utf-8') as f:
            f.write(demo_site_config)
        
        # Generate all client configurations
        print("Generating client configurations...")
        client_configs = self.generate_all_client_configs()
        for config_name, config_content in client_configs.items():
            with open(client_dir / f'{config_name}.json', 'w', encoding='utf-8') as f:
                f.write(config_content)
        
        # Generate website files
        print("Generating website files...")
        self.generate_website_files()
        
        # Generate configuration files for the web page
        self.generate_config_files()
        
        print("All configurations for nginx-proxy architecture generated!")