#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para coletar notícias de portais locais da região de Cabo Frio, Unamar, Tamoios e Barra de São João.
Utiliza web scraping para extrair notícias dos principais portais identificados.
"""

import os
import sys
import json
import requests
import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import time
import random

# Configurações
OUTPUT_DIR = Path("/home/ubuntu/automacao_noticias_central_unamar/dados")
OUTPUT_DIR.mkdir(exist_ok=True)

# Lista de portais para scraping
PORTAIS = [
    {
        "nome": "RC24H",
        "url": "https://rc24h.com.br/",
        "seletor_noticias": "article.post",
        "seletor_titulo": "h2.title a",
        "seletor_link": "h2.title a",
        "seletor_data": "span.date",
        "seletor_resumo": "div.excerpt",
        "regiao": "Cabo Frio"
    },
    {
        "nome": "Folha dos Lagos",
        "url": "https://www.folhadoslagos.com/",
        "seletor_noticias": "div.noticia",
        "seletor_titulo": "h2 a",
        "seletor_link": "h2 a",
        "seletor_data": "span.data",
        "seletor_resumo": "p.resumo",
        "regiao": "Região dos Lagos"
    },
    {
        "nome": "Lagos Informa",
        "url": "https://lagosinforma.com.br/",
        "seletor_noticias": "article.post",
        "seletor_titulo": "h2.entry-title a",
        "seletor_link": "h2.entry-title a",
        "seletor_data": "time.entry-date",
        "seletor_resumo": "div.entry-content",
        "regiao": "Região dos Lagos"
    },
    {
        "nome": "Cabo Frio em Foco",
        "url": "https://cabofrioemfoco.com.br/",
        "seletor_noticias": "article.post",
        "seletor_titulo": "h2.title a",
        "seletor_link": "h2.title a",
        "seletor_data": "span.date",
        "seletor_resumo": "div.excerpt",
        "regiao": "Cabo Frio"
    },
    {
        "nome": "Clique Diário - Unamar",
        "url": "https://cliquediario.com.br/tag/unamar",
        "seletor_noticias": "article.post",
        "seletor_titulo": "h2.title a",
        "seletor_link": "h2.title a",
        "seletor_data": "span.date",
        "seletor_resumo": "div.excerpt",
        "regiao": "Unamar"
    },
    {
        "nome": "Clique Diário - Barra de São João",
        "url": "https://cliquediario.com.br/tag/barra-de-sao-joao",
        "seletor_noticias": "article.post",
        "seletor_titulo": "h2.title a",
        "seletor_link": "h2.title a",
        "seletor_data": "span.date",
        "seletor_resumo": "div.excerpt",
        "regiao": "Barra de São João"
    }
]

def obter_user_agent():
    """Retorna um User-Agent aleatório para evitar bloqueios."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    ]
    return random.choice(user_agents)

def extrair_noticias_do_portal(portal):
    """
    Extrai notícias de um portal específico.
    
    Args:
        portal (dict): Informações do portal
        
    Returns:
        list: Lista de notícias extraídas
    """
    print(f"Coletando notícias de {portal['nome']}...")
    
    noticias = []
    
    try:
        # Configuração dos headers para evitar bloqueios
        headers = {
            'User-Agent': obter_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Faz a requisição HTTP
        response = requests.get(portal['url'], headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parseia o HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontra os elementos de notícias
        elementos_noticias = soup.select(portal['seletor_noticias'])
        
        for elemento in elementos_noticias:
            noticia = {
                'portal': portal['nome'],
                'regiao': portal['regiao'],
                'data_coleta': datetime.datetime.now().isoformat()
            }
            
            # Extrai o título
            titulo_elem = elemento.select_one(portal['seletor_titulo'])
            if titulo_elem:
                noticia['titulo'] = titulo_elem.get_text().strip()
            
            # Extrai o link
            link_elem = elemento.select_one(portal['seletor_link'])
            if link_elem and link_elem.has_attr('href'):
                link = link_elem['href']
                # Verifica se o link é relativo e adiciona o domínio se necessário
                if link.startswith('/'):
                    base_url = '/'.join(portal['url'].split('/')[:3])
                    link = base_url + link
                noticia['link'] = link
            
            # Extrai a data
            data_elem = elemento.select_one(portal['seletor_data'])
            if data_elem:
                noticia['data_publicacao'] = data_elem.get_text().strip()
            
            # Extrai o resumo
            resumo_elem = elemento.select_one(portal['seletor_resumo'])
            if resumo_elem:
                noticia['resumo'] = resumo_elem.get_text().strip()
            
            # Verifica se a notícia tem pelo menos título e link
            if 'titulo' in noticia and 'link' in noticia:
                noticias.append(noticia)
        
        print(f"Coletadas {len(noticias)} notícias de {portal['nome']}")
        
    except Exception as e:
        print(f"Erro ao coletar notícias de {portal['nome']}: {e}")
    
    # Pausa para evitar sobrecarga nos servidores
    time.sleep(random.uniform(1, 3))
    
    return noticias

def salvar_noticias(noticias, nome_portal):
    """
    Salva as notícias extraídas em um arquivo JSON.
    
    Args:
        noticias (list): Lista de notícias extraídas
        nome_portal (str): Nome do portal
    """
    if not noticias:
        print(f"Nenhuma notícia encontrada para {nome_portal}")
        return
    
    # Formata o nome do portal para o nome do arquivo
    portal_formatado = nome_portal.lower().replace(" ", "_").replace("-", "_").replace("ã", "a").replace("í", "i").replace("ó", "o")
    
    # Cria o nome do arquivo com timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = OUTPUT_DIR / f"noticias_{portal_formatado}_{timestamp}.json"
    
    # Salva as notícias em um arquivo JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)
    
    print(f"Salvas {len(noticias)} notícias de {nome_portal} em {filename}")

def main():
    """Função principal para coletar notícias de todos os portais."""
    print("Iniciando coleta de notícias dos portais locais...")
    
    todas_noticias = []
    
    for portal in PORTAIS:
        # Extrai notícias do portal
        noticias = extrair_noticias_do_portal(portal)
        
        # Salva as notícias extraídas
        if noticias:
            salvar_noticias(noticias, portal['nome'])
            todas_noticias.extend(noticias)
    
    # Salva todas as notícias em um único arquivo
    if todas_noticias:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = OUTPUT_DIR / f"todas_noticias_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(todas_noticias, f, ensure_ascii=False, indent=4)
        
        print(f"Total de {len(todas_noticias)} notícias salvas em {filename}")
    
    print("Coleta de notícias dos portais locais concluída!")

if __name__ == "__main__":
    # Cria diretório de dados se não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Executa a função principal
    main()
