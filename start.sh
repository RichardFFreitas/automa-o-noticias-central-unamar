#!/bin/bash
set -e  # para parar no erro

echo "Instalando dependências Python..."
pip install -r requirements.txt

echo "Instalando navegadores do Playwright..."
python3 -m playwright install

echo "Executando script principal..."
python3 scripts/portal_collector_improved.py
