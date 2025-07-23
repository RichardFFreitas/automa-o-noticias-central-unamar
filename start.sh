#!/bin/bash

# Ativa o virtualenv (importante apenas localmente, no Railway já é ativado)
source /opt/venv/bin/activate

# Instala navegador Chromium do Playwright
python -m playwright install chromium

# Executa o script principal
python scripts/portal_collector_improved.py
# Executa o script de processamento da noticia
python scripts/news_processor.py
# Executa o script para escrever a noticia
python scripts/news_writer.py
# Executa o script para publicar a noticia
python scripts/news_publisher.py