"""
Утилиты для Xray VPN Server
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any


def setup_logging(level: str = 'INFO') -> None:
    """Настройка логирования"""
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('xray-vpn.log')
        ]
    )


def check_dependencies() -> bool:
    """Проверка наличия необходимых зависимостей"""
    
    # Если мы внутри контейнера, пропускаем проверку
    if os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER'):
        return True
    
    dependencies = [
        'docker',
        'docker-compose'
    ]
    
    missing = []
    
    for dep in dependencies:
        try:
            subprocess.run([dep, '--version'], 
                         capture_output=True, 
                         check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(dep)
    
    if missing:
        print(f"❌ Отсутствуют зависимости: {', '.join(missing)}")
        return False
    
    return True


def create_directories() -> None:
    """Создание необходимых директорий"""
    
    directories = [
        'config',
        'config/xray',
        'config/nginx',
        'config/nginx/conf.d',
        'config/client',
        'data',
        'data/www',
        'data/ssl',
        'data/xray',
        'data/xray/logs',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Созданы директории: {len(directories)} шт.")


def validate_domain(domain: str) -> bool:
    """Валидация доменного имени"""
    
    import re
    
    # Простая проверка формата домена
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    
    if not re.match(pattern, domain):
        return False
    
    # Проверка длины
    if len(domain) > 253:
        return False
    
    return True


def validate_email(email: str) -> bool:
    """Валидация email адреса"""
    
    import re
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_ip(ip: str) -> bool:
    """Валидация IP адреса"""
    
    import ipaddress
    
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def get_system_info() -> Dict[str, Any]:
    """Получение информации о системе"""
    
    import platform
    import psutil
    
    return {
        'os': platform.system(),
        'os_version': platform.release(),
        'architecture': platform.machine(),
        'cpu_count': psutil.cpu_count(),
        'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
        'disk_free_gb': round(psutil.disk_usage('/').free / (1024**3), 2)
    }


def check_port_availability(port: int, host: str = 'localhost') -> bool:
    """Проверка доступности порта"""
    
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0  # Порт свободен если connect_ex возвращает не 0
    except Exception:
        return False


def get_docker_status() -> Dict[str, Any]:
    """Получение статуса Docker контейнеров"""
    
    try:
        # Проверка статуса контейнеров
        result = subprocess.run([
            'docker-compose', 'ps', '--format', 'json'
        ], capture_output=True, text=True, check=True)
        
        import json
        containers = []
        
        for line in result.stdout.strip().split('\n'):
            if line:
                containers.append(json.loads(line))
        
        return {
            'status': 'running',
            'containers': containers,
            'count': len(containers)
        }
        
    except subprocess.CalledProcessError:
        return {
            'status': 'error',
            'containers': [],
            'count': 0
        }
    except FileNotFoundError:
        return {
            'status': 'docker_not_found',
            'containers': [],
            'count': 0
        }


def generate_random_string(length: int = 16, charset: str = None) -> str:
    """Генерация случайной строки"""
    
    import secrets
    import string
    
    if charset is None:
        charset = string.ascii_letters + string.digits
    
    return ''.join(secrets.choice(charset) for _ in range(length))


def format_bytes(bytes_value: int) -> str:
    """Форматирование размера в байтах"""
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    
    return f"{bytes_value:.1f} PB"


def get_ssl_cert_info(cert_path: str) -> Dict[str, Any]:
    """Получение информации о SSL сертификате"""
    
    try:
        result = subprocess.run([
            'openssl', 'x509', '-in', cert_path, '-noout', '-text'
        ], capture_output=True, text=True, check=True)
        
        cert_info = {}
        
        # Парсинг вывода openssl
        for line in result.stdout.split('\n'):
            line = line.strip()
            
            if 'Not Before:' in line:
                cert_info['not_before'] = line.split('Not Before: ')[1]
            elif 'Not After :' in line:
                cert_info['not_after'] = line.split('Not After : ')[1]
            elif 'Subject:' in line and 'CN=' in line:
                cn_part = line.split('CN=')[1].split(',')[0]
                cert_info['common_name'] = cn_part
        
        return cert_info
        
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        return {}


def backup_config(backup_name: str = None) -> str:
    """Создание резервной копии конфигураций"""
    
    import shutil
    import datetime
    
    if backup_name is None:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'backup_{timestamp}'
    
    backup_dir = Path('backups') / backup_name
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Копирование конфигураций
    config_dir = Path('config')
    if config_dir.exists():
        shutil.copytree(config_dir, backup_dir / 'config', dirs_exist_ok=True)
    
    # Копирование .env файла
    env_file = Path('.env')
    if env_file.exists():
        shutil.copy2(env_file, backup_dir / '.env')
    
    return str(backup_dir)


def restore_config(backup_name: str) -> bool:
    """Восстановление конфигураций из резервной копии"""
    
    import shutil
    
    backup_dir = Path('backups') / backup_name
    
    if not backup_dir.exists():
        return False
    
    try:
        # Восстановление конфигураций
        config_backup = backup_dir / 'config'
        if config_backup.exists():
            config_dir = Path('config')
            if config_dir.exists():
                shutil.rmtree(config_dir)
            shutil.copytree(config_backup, config_dir)
        
        # Восстановление .env файла
        env_backup = backup_dir / '.env'
        if env_backup.exists():
            shutil.copy2(env_backup, '.env')
        
        return True
        
    except Exception:
        return False


def list_backups() -> List[str]:
    """Получение списка резервных копий"""
    
    backups_dir = Path('backups')
    
    if not backups_dir.exists():
        return []
    
    return [backup.name for backup in backups_dir.iterdir() if backup.is_dir()]


def cleanup_old_backups(keep_count: int = 5) -> int:
    """Очистка старых резервных копий"""
    
    import shutil
    
    backups = list_backups()
    
    if len(backups) <= keep_count:
        return 0
    
    # Сортируем по времени создания
    backups_with_time = []
    for backup in backups:
        backup_path = Path('backups') / backup
        backups_with_time.append((backup, backup_path.stat().st_mtime))
    
    backups_with_time.sort(key=lambda x: x[1], reverse=True)
    
    # Удаляем старые копии
    removed_count = 0
    for backup, _ in backups_with_time[keep_count:]:
        backup_path = Path('backups') / backup
        shutil.rmtree(backup_path)
        removed_count += 1
    
    return removed_count 