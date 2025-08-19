"""
Key generator for Xray VPN server
"""

import uuid
import secrets
import base64
import string
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from typing import Tuple


class KeyGenerator:
    """Key and ID generator for Xray"""
    
    def generate_uuid(self) -> str:
        """Generate UUID for client"""
        return str(uuid.uuid4())
    
    def generate_x25519_keys(self) -> Tuple[str, str]:
        """Generate X25519 key pair for REALITY"""
        
        # Generate private key
        private_key = x25519.X25519PrivateKey.generate()
        
        # Get public key
        public_key = private_key.public_key()
        
        # Serialize to base64
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        # Use base64.urlsafe_b64encode without padding for REALITY
        private_key_b64 = base64.urlsafe_b64encode(private_key_bytes).decode('ascii').rstrip('=')
        public_key_b64 = base64.urlsafe_b64encode(public_key_bytes).decode('ascii').rstrip('=')
        
        return private_key_b64, public_key_b64
    
    def generate_short_id(self, length: int = 8) -> str:
        """Generate short ID for REALITY"""
        
        # Generate random bytes
        random_bytes = secrets.token_bytes(length // 2)
        
        # Convert to hex string
        return random_bytes.hex()
    
    def generate_trojan_password(self, length: int = 32) -> str:
        """Generate password for Trojan"""
        
        # Use letters and digits for the password
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_ws_path(self, protocol: str = 'generic') -> str:
        """Generate random path for WebSocket"""
        
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
        """Generate service name for gRPC"""
        
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
        """Generate gRPC path based on service name"""
        
        # Convert service name to path
        path_name = service_name.replace('Service', '').lower()
        return f'/{path_name}/grpc'
    
    def generate_path(self) -> str:
        """Generate random path for WebSocket (backward compatibility)"""
        return self.generate_ws_path('generic')
    
    def generate_spider_x(self) -> str:
        """Generate spider X parameter for REALITY"""
        
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
        """Generate secret path for configuration page"""
        
        # Generate a random 16-character path
        alphabet = string.ascii_lowercase + string.digits
        random_part = ''.join(secrets.choice(alphabet) for _ in range(16))
        
        # Random prefixes for masquerading
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