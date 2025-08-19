import os
import logging
from pathlib import Path


def setup_logging():
    """Configure logging"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def check_dependencies():
    """Check for necessary dependencies (Docker, Docker Compose)"""
    logging.info("Checking dependencies...")
    
    # Check Docker
    if os.system("docker info > /dev/null 2>&1") != 0:
        logging.error("Docker is not installed or not running. Please install and start Docker.")
        return False
    logging.info("Docker is installed and running.")
    
    # Check Docker Compose
    if os.system("docker-compose version > /dev/null 2>&1") != 0:
        logging.error("Docker Compose is not installed. Please install Docker Compose.")
        return False
    logging.info("Docker Compose is installed.")
    
    return True


def create_directories():
    """Create necessary directories"""
    logging.info("Creating necessary directories...")
    
    dirs = [
        'config/xray',
        'config/nginx',
        'config/client',
        'data/ssl',
        'data/www',
        'data/secret-configs',
        'logs'
    ]
    
    for d in dirs:
        path = Path(d)
        path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Directory created: {path}")
    
    logging.info("All necessary directories created.")