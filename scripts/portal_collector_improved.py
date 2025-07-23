#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script aprimorado para coletar notícias de portais locais usando Playwright para simular navegador.
Contorna bloqueios e restrições de acesso aos sites de notícias locais.
"""

import os
import sys
import json
import datetime
import time
import random
from pathlib import Path
from playwright.sync_api import sync_playwright

# Configurações
BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "dados"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Lista de portais para scraping com seletores ajustados
PORTAIS = [
    {
        "nome": "RC24H",
        "url": "https://rc24h.com.br/",
        "seletor_noticias": "article.elementor-post",
        "seletor_titulo": "h3.elementor-post__title a",
        "seletor_link": "h3.elementor-post__title a",
        "seletor_data": "span.elementor-post-date",
        "seletor_resumo": "div.elementor-post__excerpt p",
        "regiao": "Cabo Frio"
    },
    {
        "nome": "Folha dos Lagos",
        "url": "https://www.folhadoslagos.com/",
        "seletor_noticias": "div.noticia, article.post",
        "seletor_titulo": "h2 a, h3 a",
        "seletor_link": "h2 a, h3 a",
        "seletor_data": "span.data, time",
        "seletor_resumo": "p.resumo, div.excerpt p",
        "regiao": "Região dos Lagos"
    },
    {
        "nome": "G1 Região dos Lagos",
        "url": "https://g1.globo.com/rj/regiao-dos-lagos/",
        "seletor_noticias": "div.feed-post-body",
        "seletor_titulo": "a.feed-post-link",
        "seletor_link": "a.feed-post-link",
        "seletor_data": "span.feed-post-datetime",
        "seletor_resumo": "div.feed-post-body-resumo",
        "regiao": "Região dos Lagos"
    },
    {
        "nome": "O Dia - Cabo Frio",
        "url": "https://odia.ig.com.br/cabo-frio",
        "seletor_noticias": "div.chamada",
        "seletor_titulo": "h2 a",
        "seletor_link": "h2 a",
        "seletor_data": "time",
        "seletor_resumo": "p",
        "regiao": "Cabo Frio"
    },
    {
        "nome": "Prefeitura de Cabo Frio",
        "url": "https://cabofrio.rj.gov.br/noticias/",
        "seletor_noticias": "article.post",
        "seletor_titulo": "h2 a",
        "seletor_link": "h2 a",
        "seletor_data": "time",
        "seletor_resumo": "div.excerpt p",
        "regiao": "Cabo Frio"
    },
    {
        "nome": "Prefeitura de Cabo Frio - Segundo Distrito",
        "url": "https://cabofrio.rj.gov.br/category/segundo-distrito/",
        "seletor_noticias": "article.post",
        "seletor_titulo": "h2 a",
        "seletor_link": "h2 a",
        "seletor_data": "time",
        "seletor_resumo": "div.excerpt p",
        "regiao": "Tamoios"
    }
]

def extrair_noticias_do_portal(page, portal):
    """
    Extrai notícias de um portal específico usando Playwright.
    
    Args:
        page: Instância da página do Playwright
        portal (dict): Informações do portal
        
    Returns:
        list: Lista de notícias extraídas
    """
    print(f"Coletando notícias de {portal['nome']}...")
    
    noticias = []
    
    try:
        # Navega para a URL do portal
        page.goto(portal['url'], wait_until="domcontentloaded", timeout=60000)
        
        # Aguarda um tempo para carregamento completo
        page.wait_for_timeout(5000)
        
        # Scroll para carregar conteúdo dinâmico
        for _ in range(3):
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            page.wait_for_timeout(1000)
        
        # Extrai as notícias usando os seletores
        elementos_noticias = page.query_selector_all(portal['seletor_noticias'])
        
        for elemento in elementos_noticias:
            noticia = {
                'portal': portal['nome'],
                'regiao': portal['regiao'],
                'data_coleta': datetime.datetime.now().isoformat()
            }
            
            # Extrai o título
            titulo_elem = elemento.query_selector(portal['seletor_titulo'])
            if titulo_elem:
                noticia['titulo'] = titulo_elem.inner_text().strip()
            
            # Extrai o link
            link_elem = elemento.query_selector(portal['seletor_link'])
            if link_elem:
                link = link_elem.get_attribute('href')
                # Verifica se o link é relativo e adiciona o domínio se necessário
                if link and link.startswith('/'):
                    base_url = '/'.join(portal['url'].split('/')[:3])
                    link = base_url + link
                noticia['link'] = link
            
            # Extrai a data
            data_elem = elemento.query_selector(portal['seletor_data'])
            if data_elem:
                noticia['data_publicacao'] = data_elem.inner_text().strip()
            
            # Extrai o resumo
            resumo_elem = elemento.query_selector(portal['seletor_resumo'])
            if resumo_elem:
                noticia['resumo'] = resumo_elem.inner_text().strip()
            
            # Verifica se a notícia tem pelo menos título e link
            if 'titulo' in noticia and 'link' in noticia and noticia['titulo'] and noticia['link']:
                # Filtra por palavras-chave relevantes
                keywords = ['cabo frio', 'unamar', 'tamoios', 'barra de são joão', 'região dos lagos', 'aquarios']
                titulo_lower = noticia['titulo'].lower()
                resumo_lower = noticia.get('resumo', '').lower()
                
                if any(keyword in titulo_lower or keyword in resumo_lower for keyword in keywords):
                    noticias.append(noticia)
        
        print(f"Coletadas {len(noticias)} notícias relevantes de {portal['nome']}")
        
    except Exception as e:
        print(f"Erro ao coletar notícias de {portal['nome']}: {e}")
    
    # Pausa para evitar sobrecarga nos servidores
    page.wait_for_timeout(random.randint(2000, 5000))
    
    return noticias

def salvar_noticias(noticias, nome_portal):
    """
    Salva as notícias extraídas em um arquivo JSON.
    
    Args:
        noticias (list): Lista de notícias extraídas
        nome_portal (str): Nome do portal
    """
    if not noticias:
        print(f"Nenhuma notícia relevante encontrada para {nome_portal}")
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
    """Função principal para coletar notícias de todos os portais usando Playwright."""
    print("Iniciando coleta de notícias dos portais locais com simulação de navegador...")
    
    todas_noticias = []
    
    with sync_playwright() as p:
        # Inicia o navegador em modo headless
        browser = p.chromium.launch(headless=True)
        
        # Cria um contexto de navegador com user agent de desktop
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            viewport={'width': 1280, 'height': 800}
        )
        
        # Cria uma nova página
        page = context.new_page()
        
        for portal in PORTAIS:
            # Extrai notícias do portal
            noticias = extrair_noticias_do_portal(page, portal)
            
            # Salva as notícias extraídas
            if noticias:
                salvar_noticias(noticias, portal['nome'])
                todas_noticias.extend(noticias)
        
        # Fecha o navegador
        browser.close()
    
    # Salva todas as notícias em um único arquivo
    if todas_noticias:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = OUTPUT_DIR / f"todas_noticias_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(todas_noticias, f, ensure_ascii=False, indent=4)
        
        print(f"Total de {len(todas_noticias)} notícias salvas em {filename}")
    else:
        print("Nenhuma notícia relevante foi coletada de nenhum portal.")
    
    print("Coleta de notícias dos portais locais concluída!")

if __name__ == "__main__":
    # Cria diretório de dados se não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Executa a função principal
    main()
