#!/bin/bash

# Falha se ocorrer qualquer erro
set -e

# Instala as bibliotecas do sistema necessárias para rodar o navegador (Playwright)
apt-get update && \
apt-get install -y \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libnspr4 \
    libnss3 \
    libnssutil3 \
    libsmime3 \
    libgio-2.0-0 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libexpat1 \
    libxcb1 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libcairo2 \
    libpango-1.0-0 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    libxshmfence1 \
    lsb-release \
    xdg-utils \
    wget \
    ca-certificates \
    --no-install-recommends

# Instala o navegador Chromium do Playwright
python -m playwright install chromium

# Executa os scripts sequenciais
echo "Executando: portal_collector_improved.py"
python scripts/portal_collector_improved.py

echo "Executando: news_processor.py"
python scripts/news_processor.py

echo "Executando: news_writer.py"
python scripts/news_writer.py

echo "Executando: news_publisher.py"
python scripts/news_publisher.py
