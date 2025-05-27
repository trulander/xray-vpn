#!/bin/bash

# Xray VPN Server - Скрипт автоматической установки
# Поддерживает Ubuntu 20.04+, Debian 11+, CentOS 8+

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка прав root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "Этот скрипт должен быть запущен от имени root"
        exit 1
    fi
}

# Определение операционной системы
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        print_error "Не удалось определить операционную систему"
        exit 1
    fi
    
    print_info "Обнаружена ОС: $OS $VER"
}

# Обновление системы
update_system() {
    print_info "Обновление системы..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        apt update && apt upgrade -y
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        yum update -y
    else
        print_warning "Неизвестная ОС, пропускаем обновление"
    fi
}

# Установка базовых пакетов
install_base_packages() {
    print_info "Установка базовых пакетов..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        yum install -y curl wget git unzip yum-utils device-mapper-persistent-data lvm2
    fi
}

# Установка Docker
install_docker() {
    print_info "Установка Docker..."
    
    if command -v docker &> /dev/null; then
        print_warning "Docker уже установлен"
        return
    fi
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        # Добавление официального GPG ключа Docker
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # Добавление репозитория Docker
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Установка Docker
        apt update
        apt install -y docker-ce docker-ce-cli containerd.io
        
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        # Добавление репозитория Docker
        yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        
        # Установка Docker
        yum install -y docker-ce docker-ce-cli containerd.io
    fi
    
    # Запуск и автозапуск Docker
    systemctl start docker
    systemctl enable docker
    
    print_success "Docker установлен успешно"
}

# Установка Docker Compose
install_docker_compose() {
    print_info "Установка Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose уже установлен"
        return
    fi
    
    # Получение последней версии
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    
    # Скачивание и установка
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Создание символической ссылки
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    print_success "Docker Compose установлен успешно"
}

# Установка Python и UV
install_python() {
    print_info "Установка Python и UV..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        apt install -y python3 python3-pip python3-venv
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        yum install -y python3 python3-pip
    fi
    
    # Установка UV
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    print_success "Python и UV установлены успешно"
}

# Настройка файрвола
setup_firewall() {
    print_info "Настройка файрвола..."
    
    if command -v ufw &> /dev/null; then
        # UFW (Ubuntu/Debian)
        ufw --force reset
        ufw default deny incoming
        ufw default allow outgoing
        ufw allow 22/tcp
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw --force enable
        print_success "UFW настроен"
        
    elif command -v firewall-cmd &> /dev/null; then
        # FirewallD (CentOS/RHEL)
        systemctl start firewalld
        systemctl enable firewalld
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
        print_success "FirewallD настроен"
        
    else
        print_warning "Файрвол не найден, настройте его вручную"
    fi
}

# Создание пользователя для приложения
create_app_user() {
    print_info "Создание пользователя приложения..."
    
    if id "xray-vpn" &>/dev/null; then
        print_warning "Пользователь xray-vpn уже существует"
        return
    fi
    
    useradd -m -s /bin/bash xray-vpn
    usermod -aG docker xray-vpn
    
    print_success "Пользователь xray-vpn создан"
}

# Клонирование репозитория
clone_repository() {
    print_info "Клонирование репозитория..."
    
    APP_DIR="/opt/xray-vpn"
    
    if [[ -d "$APP_DIR" ]]; then
        print_warning "Директория $APP_DIR уже существует"
        rm -rf "$APP_DIR"
    fi
    
    git clone https://github.com/your-repo/xray-vpn.git "$APP_DIR"
    chown -R xray-vpn:xray-vpn "$APP_DIR"
    
    print_success "Репозиторий клонирован в $APP_DIR"
}

# Создание systemd сервиса
create_systemd_service() {
    print_info "Создание systemd сервиса..."
    
    cat > /etc/systemd/system/xray-vpn.service << EOF
[Unit]
Description=Xray VPN Server
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/xray-vpn
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=xray-vpn
Group=xray-vpn

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable xray-vpn
    
    print_success "Systemd сервис создан"
}

# Интерактивная настройка
interactive_setup() {
    print_info "Интерактивная настройка..."
    
    echo
    read -p "Введите ваш домен (например, example.com): " DOMAIN
    read -p "Введите ваш email для SSL сертификатов: " EMAIL
    read -p "Введите IP адрес сервера: " SERVER_IP
    
    # Валидация
    if [[ -z "$DOMAIN" ]] || [[ -z "$EMAIL" ]] || [[ -z "$SERVER_IP" ]]; then
        print_error "Все поля обязательны для заполнения"
        exit 1
    fi
    
    print_info "Настройка проекта..."
    
    cd /opt/xray-vpn
    
    # Установка зависимостей
    sudo -u xray-vpn bash -c "source ~/.cargo/env && uv sync"
    
    # Инициализация проекта
    sudo -u xray-vpn bash -c "source ~/.cargo/env && source .venv/bin/activate && python -m src.main init --domain $DOMAIN --email $EMAIL --server-ip $SERVER_IP"
    
    print_success "Проект настроен"
}

# Получение SSL сертификатов
get_ssl_certificates() {
    print_info "Получение SSL сертификатов..."
    
    cd /opt/xray-vpn
    
    # Запуск инициализации сертификатов
    sudo -u xray-vpn docker-compose --profile init up certbot-init
    
    if [[ -f "data/certbot/conf/live/$DOMAIN/fullchain.pem" ]]; then
        print_success "SSL сертификаты получены успешно"
    else
        print_error "Не удалось получить SSL сертификаты"
        print_info "Проверьте, что домен $DOMAIN указывает на IP $SERVER_IP"
        exit 1
    fi
}

# Запуск сервисов
start_services() {
    print_info "Запуск сервисов..."
    
    cd /opt/xray-vpn
    
    sudo -u xray-vpn docker-compose up -d
    
    # Проверка статуса
    sleep 10
    if sudo -u xray-vpn docker-compose ps | grep -q "Up"; then
        print_success "Сервисы запущены успешно"
    else
        print_error "Ошибка при запуске сервисов"
        sudo -u xray-vpn docker-compose logs
        exit 1
    fi
}

# Генерация клиентских конфигураций
generate_client_configs() {
    print_info "Генерация клиентских конфигураций..."
    
    cd /opt/xray-vpn
    
    sudo -u xray-vpn bash -c "source ~/.cargo/env && source .venv/bin/activate && python -m src.main generate-client"
    
    print_success "Клиентские конфигурации сгенерированы"
    print_info "Конфигурации находятся в /opt/xray-vpn/config/client/"
}

# Вывод итоговой информации
show_final_info() {
    echo
    print_success "Установка завершена успешно!"
    echo
    print_info "Информация о сервере:"
    echo "  Домен: $DOMAIN"
    echo "  IP: $SERVER_IP"
    echo "  Директория: /opt/xray-vpn"
    echo
    print_info "Управление сервисом:"
    echo "  Запуск: systemctl start xray-vpn"
    echo "  Остановка: systemctl stop xray-vpn"
    echo "  Статус: systemctl status xray-vpn"
    echo
    print_info "Клиентские конфигурации:"
    echo "  Файл: /opt/xray-vpn/config/client/config.json"
    echo "  VLESS URL: см. вывод команды generate-client"
    echo
    print_info "Логи:"
    echo "  cd /opt/xray-vpn && docker-compose logs"
    echo
    print_warning "Не забудьте настроить регулярные обновления системы!"
}

# Основная функция
main() {
    echo "=================================================="
    echo "    Xray VPN Server - Автоматическая установка"
    echo "=================================================="
    echo
    
    check_root
    detect_os
    update_system
    install_base_packages
    install_docker
    install_docker_compose
    install_python
    setup_firewall
    create_app_user
    clone_repository
    create_systemd_service
    interactive_setup
    get_ssl_certificates
    start_services
    generate_client_configs
    show_final_info
}

# Запуск
main "$@" 