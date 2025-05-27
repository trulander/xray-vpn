"""
Генератор ключей для Xray VPN сервера
"""

import uuid
import secrets
import base64
import string
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from typing import Tuple


class KeyGenerator:
    """Генератор ключей и идентификаторов для Xray"""
    
    def generate_uuid(self) -> str:
        """Генерация UUID для клиента"""
        return str(uuid.uuid4())
    
    def generate_x25519_keys(self) -> Tuple[str, str]:
        """Генерация пары ключей X25519 для REALITY"""
        
        # Генерация приватного ключа
        private_key = x25519.X25519PrivateKey.generate()
        
        # Получение публичного ключа
        public_key = private_key.public_key()
        
        # Сериализация в base64
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        # Используем base64.urlsafe_b64encode без padding для REALITY
        private_key_b64 = base64.urlsafe_b64encode(private_key_bytes).decode('ascii').rstrip('=')
        public_key_b64 = base64.urlsafe_b64encode(public_key_bytes).decode('ascii').rstrip('=')
        
        return private_key_b64, public_key_b64
    
    def generate_short_id(self, length: int = 8) -> str:
        """Генерация короткого ID для REALITY"""
        
        # Генерируем случайные байты
        random_bytes = secrets.token_bytes(length // 2)
        
        # Конвертируем в hex строку
        return random_bytes.hex()
    
    def generate_trojan_password(self, length: int = 32) -> str:
        """Генерация пароля для Trojan"""
        
        # Используем буквы и цифры для пароля
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_ws_path(self, protocol: str = 'generic') -> str:
        """Генерация случайного пути для WebSocket"""
        
        protocol_paths = {
            'vmess': [
                '/vmess/ws',
                '/api/v1/vmess',
                '/ws/vmess',
                '/stream/vmess',
                '/tunnel/vmess'
            ],
            'vless': [
                '/vless/ws',
                '/api/v1/vless',
                '/ws/vless',
                '/stream/vless',
                '/tunnel/vless'
            ],
            'trojan': [
                '/trojan/ws',
                '/api/v1/trojan',
                '/ws/trojan',
                '/stream/trojan',
                '/tunnel/trojan'
            ],
            'generic': [
                '/api/v1/data',
                '/ws/chat',
                '/socket.io/',
                '/api/websocket',
                '/live/stream',
                '/api/updates',
                '/ws/notifications',
                '/realtime/data'
            ]
        }
        
        paths = protocol_paths.get(protocol, protocol_paths['generic'])
        return secrets.choice(paths)
    
    def generate_grpc_service_name(self, protocol: str = 'generic') -> str:
        """Генерация имени сервиса для gRPC"""
        
        protocol_services = {
            'vmess': [
                'VmessService',
                'VmessDataService',
                'VmessProxyService',
                'VmessStreamService',
                'VmessTunnelService'
            ],
            'vless': [
                'VlessService',
                'VlessDataService', 
                'VlessProxyService',
                'VlessStreamService',
                'VlessTunnelService'
            ],
            'trojan': [
                'TrojanService',
                'TrojanDataService',
                'TrojanProxyService', 
                'TrojanStreamService',
                'TrojanTunnelService'
            ],
            'generic': [
                'TunnelService',
                'ProxyService',
                'StreamService',
                'DataService',
                'ApiService'
            ]
        }
        
        services = protocol_services.get(protocol, protocol_services['generic'])
        return secrets.choice(services)
    
    def generate_grpc_path(self, service_name: str) -> str:
        """Генерация пути для gRPC на основе имени сервиса"""
        
        # Преобразуем имя сервиса в путь
        path_name = service_name.replace('Service', '').lower()
        return f'/{path_name}/grpc'
    
    def generate_path(self) -> str:
        """Генерация случайного пути для WebSocket (обратная совместимость)"""
        return self.generate_ws_path('generic')
    
    def generate_spider_x(self) -> str:
        """Генерация spider X параметра для REALITY"""
        
        paths = [
            '/',
            '/search',
            '/api',
            '/about',
            '/contact',
            '/news',
            '/products',
            '/services'
        ]
        
        params = [
            '?q=search',
            '?page=1',
            '?lang=en',
            '?category=tech',
            '?sort=date',
            '?filter=new',
            '?view=list',
            '?limit=10'
        ]
        
        path = secrets.choice(paths)
        param = secrets.choice(params) if secrets.randbelow(2) else ''
        
        return f"{path}{param}"
    
    def generate_secret_path(self) -> str:
        """Генерация секретного пути для страницы конфигураций"""
        
        # Генерируем случайный 16-символьный путь
        alphabet = string.ascii_lowercase + string.digits
        random_part = ''.join(secrets.choice(alphabet) for _ in range(16))
        
        # Случайные префиксы для маскировки
        prefixes = [
            '/admin',
            '/panel', 
            '/dashboard',
            '/config',
            '/settings',
            '/manage',
            '/control',
            '/secure',
            '/private',
            '/internal'
        ]
        
        prefix = secrets.choice(prefixes)
        return f"{prefix}/{random_part}" 