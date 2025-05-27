FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Установка Python зависимостей
RUN pip install --no-cache-dir \
    docker>=7.0.0 \
    pyyaml>=6.0.1 \
    jinja2>=3.1.2 \
    cryptography>=41.0.0 \
    click>=8.1.0 \
    python-dotenv>=1.0.0

# Создание пользователя для безопасности
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Точка входа - файлы будут доступны через volume в /app/workspace
ENTRYPOINT ["python", "-m", "src.main"] 