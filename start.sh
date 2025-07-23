#!/bin/bash

# Encerra imediatamente se qualquer comando falhar
set -e

# Ativa o virtualenv (Railway já faz isso, mas garante compatibilidade local)
if [ -d "/opt/venv/bin" ]; then
  source /opt/venv/bin/activate
fi

# Instala dependências do sistema necessárias ao Playwright (caso esteja num container Ubuntu slim)
apt-get update && apt-get install -y \
    libglib2.0-0 libgobject-2.0-0 libnspr4 libnss3 libnssutil3 libsmime3 \
    libgio-2.0-0 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libexpat1 \
    libxcb1 libxkbcommon0 libatspi2.0-0 libx11-6 libxcomposite1 libxdamage1 \
    libxext6 libxfixes3 libxrandr2 libgbm1 libcairo2 libpango-1.0-0 libasound2 \
    fonts-liberation libappindicator3-1 libxshmfence1 lsb-release xdg-utils wget \
    ca-certificates --no-install-recommends

# Instala o navegador Chromium (headless) para o Playwright
python -m playwright install chromium

# Executa os scripts em sequência
echo "🟢 Executando: portal_collector_improved.py"
python scripts/portal_collector_improved.py

echo "🟢 Executando: news_processor.py"
python scripts/news_processor.py

echo "🟢 Executando: news_writer.py"
python scripts/news_writer.py

echo "🟢 Executando: news_publisher.py"
python scripts/news_publisher.py

echo "✅ Processo finalizado com sucesso."
