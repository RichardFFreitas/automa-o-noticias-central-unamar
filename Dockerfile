FROM python:3.11-slim

# Instala dependências do sistema para o Playwright
RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates \
    libglib2.0-0 libgobject-2.0-0 libnspr4 libnss3 libnssutil3 libsmime3 \
    libatk-1.0-0 libatk-bridge2.0-0 libcups2 libdbus-1-3 \
    libdrm2 libexpat1 libx11-6 libxcomposite1 libxdamage1 \
    libxext6 libxfixes3 libxrandr2 libgbm1 libxkbcommon0 \
    libasound2 libpangocairo-1.0-0 libpango-1.0-0 libcairo2 \
    libatspi2.0-0 libgtk-3-0 fonts-liberation libappindicator3-1 \
    && rm -rf /var/lib/apt/lists/*

# Cria diretório da aplicação
WORKDIR /app

# Copia os arquivos
COPY . /app

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m playwright install --with-deps chromium

# Dá permissão ao start.sh
RUN chmod +x start.sh

# Comando inicial
CMD ["./start.sh"]
