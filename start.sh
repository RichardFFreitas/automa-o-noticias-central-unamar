#!/bin/bash
set -e

# Executa os scripts sequencialmente
echo "Executando portal_collector_improved.py"
python scripts/portal_collector_improved.py

echo "Executando news_processor.py"
python scripts/news_processor.py

echo "Executando news_writer.py"
python scripts/news_writer.py

echo "Executando news_publisher.py"
python scripts/news_publisher.py
