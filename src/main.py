#!/usr/bin/env python3
"""
Xray VPN Server - Генератор конфигураций
Поддерживает множественные протоколы: VMess, VLESS, Trojan
Транспорты: WebSocket, gRPC
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_generator import ConfigGenerator
from key_generator import KeyGenerator
from utils import setup_logging, check_dependencies, create_directories


def init_project(args: argparse.Namespace) -> None:
    """Инициализация проекта с генерацией ключей и конфигураций"""
    
    domain = args.domain
    email = args.email or f"admin@{domain}"
    server_ip = args.server_ip
    
    print("🚀 Инициализация Xray VPN Server...")
    print(f"📋 Домен: {domain}")
    print(f"📧 Email: {email}")
    print(f"🌐 IP сервера: {server_ip}")
    
    # Проверка зависимостей
    if not check_dependencies():
        print("❌ Не все зависимости установлены")
        sys.exit(1)
    
    # Создание директорий
    create_directories()
    
    # Генерация ключей
    key_gen = KeyGenerator()
    config_gen = ConfigGenerator()
    
    # Получаем существующие переменные или генерируем новые
    env_vars = config_gen.get_env_vars()
    
    # Устанавливаем домен, email и IP сервера
    env_vars['domain'] = domain
    env_vars['email'] = email
    env_vars['server_ip'] = server_ip
    
    # Генерируем новые ключи если они не заданы
    if not env_vars['vmess_uuid']:
        env_vars['vmess_uuid'] = key_gen.generate_uuid()
        print(f"✅ Сгенерирован VMess UUID: {env_vars['vmess_uuid']}")
    
    if not env_vars['vless_uuid']:
        env_vars['vless_uuid'] = key_gen.generate_uuid()
        print(f"✅ Сгенерирован VLESS UUID: {env_vars['vless_uuid']}")
    
    if not env_vars['trojan_password']:
        env_vars['trojan_password'] = key_gen.generate_trojan_password()
        print(f"✅ Сгенерирован Trojan пароль: {env_vars['trojan_password']}")
    
    # Генерируем пути если они не заданы
    if not env_vars['vmess_ws_path'] or env_vars['vmess_ws_path'] == '/vmess/ws':
        env_vars['vmess_ws_path'] = key_gen.generate_ws_path('vmess')
        print(f"✅ Сгенерирован VMess WS путь: {env_vars['vmess_ws_path']}")
    
    if not env_vars['vless_ws_path'] or env_vars['vless_ws_path'] == '/vless/ws':
        env_vars['vless_ws_path'] = key_gen.generate_ws_path('vless')
        print(f"✅ Сгенерирован VLESS WS путь: {env_vars['vless_ws_path']}")
    
    if not env_vars['trojan_ws_path'] or env_vars['trojan_ws_path'] == '/trojan/ws':
        env_vars['trojan_ws_path'] = key_gen.generate_ws_path('trojan')
        print(f"✅ Сгенерирован Trojan WS путь: {env_vars['trojan_ws_path']}")
    
    # Генерируем gRPC сервисы если они не заданы
    if not env_vars['vmess_grpc_service'] or env_vars['vmess_grpc_service'] == 'VmessService':
        env_vars['vmess_grpc_service'] = key_gen.generate_grpc_service_name('vmess')
        env_vars['vmess_grpc_path'] = key_gen.generate_grpc_path(env_vars['vmess_grpc_service'])
        print(f"✅ Сгенерирован VMess gRPC сервис: {env_vars['vmess_grpc_service']}")
    
    if not env_vars['vless_grpc_service'] or env_vars['vless_grpc_service'] == 'VlessService':
        env_vars['vless_grpc_service'] = key_gen.generate_grpc_service_name('vless')
        env_vars['vless_grpc_path'] = key_gen.generate_grpc_path(env_vars['vless_grpc_service'])
        print(f"✅ Сгенерирован VLESS gRPC сервис: {env_vars['vless_grpc_service']}")
    
    if not env_vars['trojan_grpc_service'] or env_vars['trojan_grpc_service'] == 'TrojanService':
        env_vars['trojan_grpc_service'] = key_gen.generate_grpc_service_name('trojan')
        env_vars['trojan_grpc_path'] = key_gen.generate_grpc_path(env_vars['trojan_grpc_service'])
        print(f"✅ Сгенерирован Trojan gRPC сервис: {env_vars['trojan_grpc_service']}")
    
    # Генерируем секретный путь если он не задан
    if not env_vars['secret_config_path'] or env_vars['secret_config_path'] == '/secret/configs':
        env_vars['secret_config_path'] = key_gen.generate_secret_path()
        print(f"✅ Сгенерирован секретный путь: {env_vars['secret_config_path']}")
    
    # Сохранение .env файла
    env_content = config_gen.env.get_template('env_multi.j2').render(**env_vars)
    
    env_path = '/app/workspace/.env' if Path('/app/workspace').exists() else '.env'
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Файл .env создан/обновлен")
    
    # Перезагружаем переменные окружения в существующем ConfigGenerator
    config_gen.reload_env_vars()
    
    # Генерация всех конфигураций
    config_gen.generate_all_configs()
    print("✅ Все конфигурации сгенерированы")
    
    print("\n🎉 Инициализация завершена!")
    print(f"\n📋 Проект готов для домена: {domain}")
    print("\n🚀 Для запуска выполните:")
    print("   docker-compose up -d")


def generate_configs(args: argparse.Namespace) -> None:
    """Генерация конфигураций"""
    
    print("🔧 Генерация конфигураций...")
    
    config_gen = ConfigGenerator()
    config_gen.generate_all_configs()
    
    print("✅ Конфигурации сгенерированы в папке config/")


def generate_client_config(args: argparse.Namespace) -> None:
    """Генерация клиентской конфигурации"""
    
    config_gen = ConfigGenerator()
    
    try:
        # Генерация JSON конфигурации
        client_config = config_gen.generate_client_config(
            protocol=args.protocol,
            transport=args.transport
        )
        
        # Сохранение в файл
        config_dir = Path('config/client')
        config_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f'{args.protocol}_{args.transport}.json'
        filepath = config_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(client_config)
        
        print(f"✅ Клиентская конфигурация сохранена: {filepath}")
        
        # Генерация URL для мобильных приложений
        if args.url:
            try:
                if args.protocol == 'vless':
                    url = config_gen.generate_vless_url(transport=args.transport)
                elif args.protocol == 'vmess':
                    url = config_gen.generate_vmess_url(transport=args.transport)
                elif args.protocol == 'trojan':
                    url = config_gen.generate_trojan_url(transport=args.transport)
                else:
                    raise ValueError(f"URL генерация не поддерживается для протокола {args.protocol}")
                
                print(f"\n📱 URL для мобильного приложения:")
                print(url)
                
                # Сохранение URL в файл
                url_file = config_dir / f'{args.protocol}_{args.transport}_url.txt'
                with open(url_file, 'w', encoding='utf-8') as f:
                    f.write(url)
                
                print(f"✅ URL сохранен в файл: {url_file}")
                
            except Exception as e:
                print(f"⚠️  Ошибка генерации URL: {e}")
        
    except Exception as e:
        print(f"❌ Ошибка генерации клиентской конфигурации: {e}")
        sys.exit(1)


def show_status(args: argparse.Namespace) -> None:
    """Показать статус сервера"""
    
    print("📊 Статус Xray VPN Server")
    print("=" * 50)
    
    # Проверка файлов конфигурации
    config_files = [
        'config/xray/config.json',
        'config/nginx/nginx.conf',
        'config/nginx/demo-site.conf',
        '.env'
    ]
    
    print("\n📁 Файлы конфигурации:")
    for file_path in config_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
    
    # Проверка клиентских конфигураций
    client_dir = Path('config/client')
    if client_dir.exists():
        client_configs = list(client_dir.glob('*.json'))
        print(f"\n👥 Клиентские конфигурации ({len(client_configs)}):")
        for config_file in client_configs:
            print(f"  ✅ {config_file.name}")
    else:
        print("\n👥 Клиентские конфигурации: не найдены")
    
    # Проверка переменных окружения
    config_gen = ConfigGenerator()
    env_vars = config_gen.get_env_vars()
    
    print("\n🔧 Основные настройки:")
    print(f"  Домен: {env_vars['domain']}")
    print(f"  IP сервера: {env_vars['server_ip']}")
    print(f"  Email: {env_vars['email']}")
    print(f"  Уровень логирования: {env_vars['log_level']}")
    
    print("\n🔑 Протоколы:")
    print(f"  VMess UUID: {env_vars['vmess_uuid'][:8]}...")
    print(f"  VLESS UUID: {env_vars['vless_uuid'][:8]}...")
    print(f"  Trojan пароль: {env_vars['trojan_password'][:8]}...")


def show_ssl_status(args: argparse.Namespace) -> None:
    """Показать статус SSL сертификатов"""
    
    print("🔒 Статус SSL сертификатов")
    print("=" * 50)
    
    config_gen = ConfigGenerator()
    env_vars = config_gen.get_env_vars()
    domain = env_vars['domain']
    
    ssl_dir = Path(f'data/ssl/live/{domain}')
    
    if ssl_dir.exists():
        cert_files = ['fullchain.pem', 'privkey.pem', 'cert.pem', 'chain.pem']
        
        print(f"\n📁 Сертификаты для домена {domain}:")
        for cert_file in cert_files:
            cert_path = ssl_dir / cert_file
            if cert_path.exists():
                print(f"  ✅ {cert_file}")
            else:
                print(f"  ❌ {cert_file}")
        
        # Проверка срока действия сертификата
        cert_path = ssl_dir / 'cert.pem'
        if cert_path.exists():
            try:
                import subprocess
                result = subprocess.run([
                    'openssl', 'x509', '-in', str(cert_path), '-noout', '-dates'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"\n📅 Информация о сертификате:")
                    for line in result.stdout.strip().split('\n'):
                        print(f"  {line}")
                
            except Exception as e:
                print(f"⚠️  Не удалось проверить срок действия сертификата: {e}")
    else:
        print(f"\n❌ Сертификаты для домена {domain} не найдены")
        print("\n💡 Для получения сертификата выполните:")
        print(f"docker-compose --profile tools run --rm certbot certonly --webroot -w /var/www/html -d {domain}")


def main():
    """Главная функция"""
    
    parser = argparse.ArgumentParser(
        description='Xray VPN Server - Генератор конфигураций',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python -m src.main init                           # Инициализация проекта
  python -m src.main generate                       # Генерация всех конфигураций
  python -m src.main generate-client vless ws       # Генерация клиентской конфигурации VLESS WebSocket
  python -m src.main generate-client vmess grpc -u  # Генерация VMess gRPC с URL
  python -m src.main status                         # Показать статус
  python -m src.main ssl-status                     # Показать статус SSL
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда init
    init_parser = subparsers.add_parser('init', help='Инициализация проекта')
    init_parser.add_argument('--domain', required=True, help='Домен сервера (например: vpn.example.com)')
    init_parser.add_argument('--email', help='Email для Let\'s Encrypt (по умолчанию: admin@домен)')
    init_parser.add_argument('--server-ip', '-i', required=True, help='IP адрес сервера')
    
    # Команда generate
    generate_parser = subparsers.add_parser('generate', help='Генерация всех конфигураций')
    
    # Команда generate-client
    client_parser = subparsers.add_parser('generate-client', help='Генерация клиентской конфигурации')
    client_parser.add_argument('protocol', choices=['vmess', 'vless', 'trojan'], help='Протокол')
    client_parser.add_argument('transport', choices=['ws', 'grpc'], help='Транспорт')
    client_parser.add_argument('-u', '--url', action='store_true', help='Генерировать URL для мобильных приложений')
    
    # Команда status
    status_parser = subparsers.add_parser('status', help='Показать статус сервера')
    
    # Команда ssl-status
    ssl_parser = subparsers.add_parser('ssl-status', help='Показать статус SSL сертификатов')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Настройка логирования
    setup_logging()
    
    # Выполнение команд
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