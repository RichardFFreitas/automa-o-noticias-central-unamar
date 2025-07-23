#!/bin/bash

# Ativa o virtualenv (importante apenas localmente, no Railway já é ativado)
source /opt/venv/bin/activate

# Instala navegador Chromium do Playwright
python -m playwright install chromium

# Executa o script principal
python scripts/portal_collector_improved.py
