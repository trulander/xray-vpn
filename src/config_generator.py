"""
Генератор конфигураций для Xray и Nginx (мульти-протокольная архитектура с nginx-proxy)
"""

import urllib.parse
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any
from dotenv import load_dotenv

from key_generator import KeyGenerator


class ConfigGenerator:
    """Генератор конфигураций для VPN сервера с nginx-proxy архитектурой"""
    
    def __init__(self):
        # Сначала пытаемся загрузить .env файл (если существует)
        env_path = '/app/workspace/.env' if Path('/app/workspace/.env').exists() else '.env'
        if Path(env_path).exists():
            load_dotenv(env_path)
        
        self.key_gen = KeyGenerator()
        
        # Определяем путь к шаблонам (всегда в контейнере /app/workspace/templates)
        templates_path = '/app/workspace/templates' if Path('/app/workspace/templates').exists() else 'templates'
        self.env = Environment(loader=FileSystemLoader(templates_path))
    
    def reload_env_vars(self):
        """Принудительная перезагрузка переменных окружения из .env файла"""
        env_path = '/app/workspace/.env' if Path('/app/workspace/.env').exists() else '.env'
        if Path(env_path).exists():
            load_dotenv(env_path, override=True)
    
    def get_env_vars(self) -> Dict[str, Any]:
        """Получение переменных окружения"""
        return {
            # Основные настройки
            'domain': os.getenv('DOMAIN', 'example.com'),
            'server_ip': os.getenv('SERVER_IP', 'YOUR_SERVER_IP'),
            'email': os.getenv('EMAIL', 'admin@example.com'),
            
            # UUID для протоколов
            'vmess_uuid': os.getenv('VMESS_UUID') or '',
            'vless_uuid': os.getenv('VLESS_UUID') or '',
            
            # Пароль для Trojan
            'trojan_password': os.getenv('TROJAN_PASSWORD') or '',
            
            # Пути для WebSocket
            'vmess_ws_path': os.getenv('VMESS_WS_PATH') or '/vmess/ws',
            'vless_ws_path': os.getenv('VLESS_WS_PATH') or '/vless/ws',
            'trojan_ws_path': os.getenv('TROJAN_WS_PATH') or '/trojan/ws',
            
            # Пути для gRPC
            'vmess_grpc_path': os.getenv('VMESS_GRPC_PATH') or '/vmess/grpc',
            'vless_grpc_path': os.getenv('VLESS_GRPC_PATH') or '/vless/grpc',
            'trojan_grpc_path': os.getenv('TROJAN_GRPC_PATH') or '/trojan/grpc',
            
            # Сервисы для gRPC
            'vmess_grpc_service': os.getenv('VMESS_GRPC_SERVICE') or 'VmessService',
            'vless_grpc_service': os.getenv('VLESS_GRPC_SERVICE') or 'VlessService',
            'trojan_grpc_service': os.getenv('TROJAN_GRPC_SERVICE') or 'TrojanService',
            
            # Секретная страница конфигураций
            'secret_config_path': os.getenv('SECRET_CONFIG_PATH') or '/secret/configs',
            
            # Настройки логирования
            'log_level': os.getenv('LOG_LEVEL', 'warning'),
            'enable_stats': os.getenv('ENABLE_STATS', 'false').lower() == 'true',
            
            # Docker настройки
            'uid': os.getenv('UID', '1000'),
            'gid': os.getenv('GID', '1000')
        }
    
    def generate_xray_server_config(self) -> str:
        """Генерация серверной конфигурации Xray с множественными протоколами"""
        vars = self.get_env_vars()
        template = self.env.get_template('xray_server_multi.json.j2')
        return template.render(**vars)
    
    def generate_client_config(self, protocol: str = 'vless', transport: str = 'ws') -> str:
        """Генерация клиентской конфигурации для указанного протокола и транспорта"""
        vars = self.get_env_vars()
        
        template_name = f'client_{protocol}_{transport}.json.j2'
        
        try:
            template = self.env.get_template(template_name)
            return template.render(**vars)
        except Exception as e:
            raise ValueError(f"Неподдерживаемая комбинация протокола {protocol} и транспорта {transport}: {e}")
    
    def generate_all_client_configs(self) -> Dict[str, str]:
        """Генерация всех клиентских конфигураций"""
        configs = {}
        
        protocols = ['vmess', 'vless', 'trojan']
        transports = ['ws', 'grpc']
        
        for protocol in protocols:
            for transport in transports:
                try:
                    config_name = f'{protocol}_{transport}'
                    configs[config_name] = self.generate_client_config(protocol=protocol, transport=transport)
                except ValueError:
                    # Пропускаем неподдерживаемые комбинации
                    continue
        
        return configs
    
    def generate_vless_url(self, transport: str = 'ws') -> str:
        """Генерация VLESS URL для мобильных приложений"""
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
            raise ValueError(f"Неподдерживаемый транспорт: {transport}")
        
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        
        vless_url = f"vless://{vars['vless_uuid']}@{vars['domain']}:443?{param_string}#{urllib.parse.quote(f'Xray-VLESS-{transport.upper()}')}"
        
        return vless_url
    
    def generate_vmess_url(self, transport: str = 'ws') -> str:
        """Генерация VMess URL для мобильных приложений"""
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
            raise ValueError(f"Неподдерживаемый транспорт: {transport}")
        
        import json
        import base64
        
        vmess_json = json.dumps(vmess_config, separators=(',', ':'))
        vmess_b64 = base64.b64encode(vmess_json.encode()).decode()
        
        return f"vmess://{vmess_b64}"
    
    def generate_trojan_url(self, transport: str = 'ws') -> str:
        """Генерация Trojan URL для мобильных приложений"""
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
            raise ValueError(f"Неподдерживаемый транспорт: {transport}")
        
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        
        trojan_url = f"trojan://{vars['trojan_password']}@{vars['domain']}:443?{param_string}#{urllib.parse.quote(f'Xray-Trojan-{transport.upper()}')}"
        
        return trojan_url
    
    def generate_demo_site_config(self) -> str:
        """Генерация конфигурации демо сайта"""
        vars = self.get_env_vars()
        template = self.env.get_template('demo_site.conf.j2')
        return template.render(**vars)
    
    def generate_nginx_domain_config(self) -> str:
        """Генерация конфигурации домена для nginx-proxy с секретной страницей"""
        vars = self.get_env_vars()
        template = self.env.get_template('nginx_domain.conf.j2')
        return template.render(**vars)
    
    def generate_nginx_custom_config(self) -> str:
        """Генерация кастомной конфигурации для nginx-proxy"""
        vars = self.get_env_vars()
        template = self.env.get_template('nginx_custom.conf.j2')
        return template.render(**vars)
    
    def generate_nginx_default_config(self) -> str:
        """Генерация default конфигурации nginx для блокировки неавторизованных запросов"""
        vars = self.get_env_vars()
        template = self.env.get_template('nginx_default.conf.j2')
        return template.render(**vars)
    
    def generate_config_page(self) -> str:
        """Генерация HTML страницы для скачивания конфигураций"""
        vars = self.get_env_vars()
        
        # Генерируем VMess Base64 для URL
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
        """Генерация файлов конфигураций для веб-страницы"""
        # В контейнере всегда используем /app, локально - текущую директорию
        if Path('/app/workspace').exists():
            base_path = Path('/app')
        else:
            base_path = Path('.')
            
        # Создаем отдельную директорию для конфигураций вне www
        configs_dir = base_path / 'data' / 'secret-configs'
        configs_dir.mkdir(parents=True, exist_ok=True)
        
        # Генерация страницы конфигураций
        print("🔧 Генерация страницы конфигураций...")
        config_page_content = self.generate_config_page()
        with open(configs_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(config_page_content)
        
        # Копируем клиентские конфигурации в папку configs
        client_dir = base_path / 'config' / 'client'
        if client_dir.exists():
            print("🔧 Копирование клиентских конфигураций...")
            for config_file in client_dir.glob('*.json'):
                # Копируем файл в configs директорию
                with open(config_file, 'r', encoding='utf-8') as src:
                    with open(configs_dir / config_file.name, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
        
        print(f"✅ Секретная страница создана в: {configs_dir}")
    
    def generate_website_files(self) -> None:
        """Генерация файлов веб-сайта"""
        vars = self.get_env_vars()
        
        # В контейнере всегда используем /app, локально - текущую директорию
        if Path('/app/workspace').exists():
            base_path = Path('/app')
        else:
            base_path = Path('.')
            
        www_dir = base_path / 'data' / 'www'
        www_dir.mkdir(parents=True, exist_ok=True)
        
        # Генерация index.html
        template = self.env.get_template('index.html.j2')
        index_content = template.render(**vars)
        
        with open(www_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        # Генерация robots.txt
        template = self.env.get_template('robots.txt.j2')
        robots_content = template.render(**vars)
        
        with open(www_dir / 'robots.txt', 'w', encoding='utf-8') as f:
            f.write(robots_content)
    
    def generate_all_configs(self) -> None:
        """Генерация всех конфигураций для nginx-proxy архитектуры"""
        
        # В контейнере всегда используем /app, локально - текущую директорию  
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
        
        print(f"📁 Создание конфигураций в: {config_dir}")
        
        # Получаем домен для создания правильного имени файла
        vars = self.get_env_vars()
        domain = vars['domain']
        
        print(f"🔧 Генерация для домена: {domain}")
        
        # Генерация конфигурации Xray сервера
        print("🔧 Генерация конфигурации Xray сервера...")
        xray_config = self.generate_xray_server_config()
        with open(xray_dir / 'config.json', 'w', encoding='utf-8') as f:
            f.write(xray_config)
        
        # Генерация кастомной конфигурации для nginx-proxy
        print("🔧 Генерация кастомной конфигурации nginx-proxy...")
        nginx_custom_config = self.generate_nginx_custom_config()
        
        # nginx-proxy ищет файлы в формате {domain}_location
        location_file = nginx_dir / f'{domain}_location'
        with open(location_file, 'w', encoding='utf-8') as f:
            f.write(nginx_custom_config)
        print(f"✅ Создан файл: {location_file}")
        
        # Генерация конфигурации домена с секретной страницей
        print("🔧 Генерация конфигурации домена с секретной страницей...")
        nginx_domain_config = self.generate_nginx_domain_config()
        
        # nginx-proxy ищет файлы в формате {domain} для конфигурации всего домена
        domain_file = nginx_dir / domain
        with open(domain_file, 'w', encoding='utf-8') as f:
            f.write(nginx_domain_config)
        print(f"✅ Создан файл домена: {domain_file}")
        
        # Создаем конфигурацию по умолчанию для блокировки неавторизованных запросов
        print("🔧 Генерация default конфигурации nginx...")
        nginx_default_config = self.generate_nginx_default_config()
        
        # Создаем директорию conf.d если не существует
        conf_d_dir = nginx_dir / 'conf.d'
        conf_d_dir.mkdir(exist_ok=True)
        
        # Сохраняем default конфигурацию
        default_file = conf_d_dir / 'default.conf'
        with open(default_file, 'w', encoding='utf-8') as f:
            f.write(nginx_default_config)
        print(f"✅ Создан default файл: {default_file}")
        
        # Генерация конфигурации демо сайта
        print("🔧 Генерация конфигурации демо сайта...")
        demo_site_config = self.generate_demo_site_config()
        with open(nginx_dir / 'demo-site.conf', 'w', encoding='utf-8') as f:
            f.write(demo_site_config)
        
        # Генерация всех клиентских конфигураций
        print("🔧 Генерация клиентских конфигураций...")
        client_configs = self.generate_all_client_configs()
        for config_name, config_content in client_configs.items():
            with open(client_dir / f'{config_name}.json', 'w', encoding='utf-8') as f:
                f.write(config_content)
        
        # Генерация файлов веб-сайта
        print("🔧 Генерация файлов веб-сайта...")
        self.generate_website_files()
        
        # Генерация файлов конфигураций для веб-страницы
        self.generate_config_files()
        
        print("✅ Все конфигурации для nginx-proxy архитектуры сгенерированы!") 