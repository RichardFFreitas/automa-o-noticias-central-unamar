#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para automatizar a publicação de notícias na plataforma Central Unamar.
Utiliza API ou simulação de publicação para integrar as notícias geradas.
"""

import os
import sys
import json
import datetime
import time
import random
import requests

from pathlib import Path
import re
from supabase import create_client, Client
from news_writer import gerar_citacao

# Configurações

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "noticias_geradas"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

SUPABASE_URL = "https://fqeawknurzhdoznzuctb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZxZWF3a251cnpoZG96bnp1Y3RiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczOTU1MjE5OCwiZXhwIjoyMDU1MTI4MTk4fQ.fC2AaHpngWvgkUZBNdk_MI9k5CPUCvsab1oACew9ZAo"
SUPABASE_USER_ID = "94ee49f4-c56d-4425-a6ce-a0f724ca6260"


GEMINI_API_KEY = "AIzaSyDLTtIFhzJYmeI8MHK4FwPGch_eCxYCbUw"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def carregar_noticias_redigidas():
    """
    Carrega as notícias redigidas dos arquivos JSON.
    
    Returns:
        dict: Notícias redigidas por região
    """
    noticias_por_regiao = {}
    
    # Busca arquivos de notícias redigidas
    arquivos_json = list(INPUT_DIR.glob("noticias_redigidas_*.json"))
    
    if not arquivos_json:
        print("Nenhum arquivo de notícias redigidas encontrado.")
        return noticias_por_regiao
    
    # Carrega as notícias de cada arquivo
    for arquivo in arquivos_json:
        try:
            # Extrai a região do nome do arquivo
            partes = arquivo.stem.split('_')
            if len(partes) >= 3:
                regiao = partes[2]
                
                with open(arquivo, 'r', encoding='utf-8') as f:
                    noticias = json.load(f)
                    
                    if isinstance(noticias, list):
                        noticias_por_regiao[regiao] = noticias
                        print(f"Carregadas {len(noticias)} notícias redigidas para {regiao}")
        except Exception as e:
            print(f"Erro ao carregar notícias de {arquivo.name}: {e}")
    
    return noticias_por_regiao

def preparar_payload_noticia(noticia):
    """
    Prepara o payload para envio da notícia à API da plataforma (apenas para simulação).
    Args:
        noticia (dict): Dados da notícia redigida
    Returns:
        dict: Payload formatado para a API (simulação)
    """
    categorias = noticia.get('categorias', ['geral'])
    regiao = noticia.get('regiao', 'indefinida')
    payload = {
        "titulo": noticia.get('titulo', ''),
        "conteudo": noticia.get('texto', ''),
        "categorias": categorias,
        "regiao": regiao,
        "fonte": noticia.get('fonte_original', ''),
        "link_original": noticia.get('link_original', ''),
        "data_publicacao": datetime.datetime.now().isoformat(),
        "autor": "Automação Central Unamar",
        "destaque": False,
        "tags": [regiao] + categorias
    }
    return payload

def publicar_noticia_api(payload):
    """
    Publica a notícia na plataforma através da API.
    
    Args:
        payload (dict): Dados formatados da notícia
        
    Returns:
        dict: Resposta da API ou simulação
    """
    # Configuração para modo de simulação (sem envio real)
    MODO_SIMULACAO = True  # Alterar para False quando a API estiver disponível
    
    if MODO_SIMULACAO:
        print(f"[SIMULAÇÃO] Enviando notícia: {payload['titulo']}")
        time.sleep(random.uniform(0.5, 1.5))  # Simula tempo de resposta da API
        
        # Simula resposta da API
        resposta = {
            "sucesso": True,
            "id": f"noticia_{random.randint(1000, 9999)}",
            "url": f"https://centralunamar.com.br/noticias/{payload['regiao']}/{random.randint(1000, 9999)}",
            "mensagem": "Notícia publicada com sucesso (simulação)",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        print(f"[SIMULAÇÃO] Notícia publicada com sucesso: ID {resposta['id']}")
        return resposta
    
    # Código para envio real à API (quando disponível)
    try:
        # Aqui ficaria o código real de publicação na API, se necessário
        # Como não há plataforma, apenas simulação
        return {"sucesso": False, "erro": "API real não implementada", "timestamp": datetime.datetime.now().isoformat()}
        
    except Exception as e:
        print(f"Erro ao publicar notícia: {e}")
        return {
            "sucesso": False,
            "erro": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }

def registrar_log(noticia, resultado_publicacao):
    """
    Registra log da publicação da notícia.
    
    Args:
        noticia (dict): Dados da notícia
        resultado_publicacao (dict): Resultado da publicação
    """
    log_entry = {
        "titulo_noticia": noticia.get('titulo', ''),
        "regiao": noticia.get('regiao', ''),
        "categorias": noticia.get('categorias', []),
        "resultado": resultado_publicacao,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Cria nome do arquivo de log
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = LOGS_DIR / f"publicacao_log_{timestamp}.json"
    
    # Salva o log
    with open(log_filename, 'w', encoding='utf-8') as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=4)
    
    print(f"Log de publicação salvo em {log_filename}")

def gerar_slug(titulo):
    slug = titulo.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

# Mapeamento das categorias internas para as oficiais
CATEGORIAS_OFICIAIS = {
    'economia': 'Economia e negócios',
    'negocios': 'Economia e negócios',
    'eventos': 'Eventos e cultura',
    'cultura': 'Eventos e cultura',
    'esporte': 'Esportes',
    'esportes': 'Esportes',
    'seguranca': 'Segurança pública',
    'policial': 'Segurança pública',
    'saude': 'Saúde',
    'clima': 'Clima e trânsito',
    'transito': 'Clima e trânsito',
    'geral': 'Eventos e cultura',
    'politica': 'Eventos e cultura',
    'educacao': 'Eventos e cultura',
    'turismo': 'Eventos e cultura'
}

def gerar_html_estruturado(noticia):
    """
    Gera HTML estruturado para o campo content, usando <p>, <h2>, <blockquote>, <hr>.
    """
    texto = noticia.get('texto', '')
    linhas = texto.split('\n')
    html = ''
    for linha in linhas:
        l = linha.strip()
        if not l:
            continue
        if l.startswith('"') and l.endswith('"'):
            html += f'<blockquote><p>{l}</p></blockquote>'
        elif l.isupper() or l.startswith('SEGURANÇA:') or l.startswith('SAÚDE:') or l.startswith('POLÍTICA:'):
            html += f'<h2>{l}</h2>'
        elif l.startswith('Fonte:') or l.startswith('Leia mais em:'):
            html += f'<hr><p>{l}</p>'
        else:
            html += f'<p>{l}</p>'
    return html

def gerar_excerpt_gemini(noticia):
    """
    Usa a API do Google Gemini para gerar o campo content estruturado em HTML.
    """
    prompt = (
        "Gere o conteúdo de uma chamada para uma notícia para minha plataforma chamada Central Unamar, com base nas informações abaixo.\n"
        "IMPORTANTE:\n"
        "- Retorne apenas o conteúdo do excerpt da notícia, sem explicações, comentários, instruções, nem tags <html>, <head>, <body>, <style>, nem nada além do conteúdo da notícia.\n"
        "- Não escreva nada além do excerpt da notícia.\n"
        "- Se for duas ou mais noticias lempre de escrever um excerpt condizente para cada noticia.\n"
        "- Não escreva frases como 'Aqui está...', 'Segue abaixo...', etc.\n"
        "- Caso tenha alguma citação adicione aspas e reticências para demonstrar continuação \n"
        "\nExemplo de estrutura desejada:\n"
        "A noite desta quinta-feira (3) foi marcada por tensão em Tamoios, Cabo Frio.\n"
        "\nINFORMAÇÕES DA NOTÍCIA:\n" + noticia.get('texto', '')
    )
    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    try:
        resp = requests.post(GEMINI_API_URL, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        content = data['candidates'][0]['content']['parts'][0]['text']
        return content.strip()
    except Exception as e:
        print(f"[Gemini] Erro ao gerar content: {e}. Usando texto original.")
        return noticia

def gerar_content_gemini(noticia):
    """
    Usa a API do Google Gemini para gerar o campo content estruturado em HTML.
    """
    prompt = (
        "Gere o conteúdo de uma notícia para minha plataforma chamada Central Unamar, com base nas informações abaixo.\n"
        "IMPORTANTE:\n"
        "- O título principal da notícia (tag <h1>) deve sempre começar com um emoji relevante ao tema.\n"
        "- Estruture a notícia de forma detalhada, encorpada e envolvente, usando subtítulos (<h2>) com emojis, blocos de citação, separadores (<hr>), parágrafos, destaques com <strong>, e emojis também em subtítulos e parágrafos quando fizer sentido.\n"
        "- Aprofunde o contexto, causas, consequências, reações e desdobramentos, como no exemplo abaixo.\n"
        "- Retorne apenas o conteúdo da notícia em HTML, sem explicações, comentários, instruções, nem tags <html>, <head>, <body>, <style>, nem nada além do conteúdo da notícia.\n"
        "- Não escreva nada além do HTML da notícia.\n"
        "- Não divulgue o link de outros portais de noticia, no maximo coloque os links pertinentes a noticia, mas nunca o link de outra plataforma, adicione apenas na fonte o nome, exemplo: Fonte: G1 Região dos Lagos.\n"
        "- Não compartilhe o link da noticia original, apenas cite as fontes, sem link.\n"
        "- Deixe a noticícia menos densa, aumentando o espaçamento das letras evitando assim o cansaço da leitura.\n"
        "- Se for duas ou mais noticias lempre de escrever um excerpt condizente para cada noticia.\n"
        "- Não escreva frases como 'Aqui está...', 'Segue abaixo...', etc.\n"
        "\nExemplo de estrutura desejada:\n"
        "<p>A Prefeitura de <strong>Linhares (ES)</strong> denunciou o suposto abandono de <strong>12 pessoas em situação de rua</strong>, incluindo uma gestante, vindas de Cabo Frio. Em resposta, o prefeito <strong>Dr. Serginho</strong> gravou um vídeo para esclarecer o ocorrido e rebater as acusações.</p><hr><h2>🗣️ <strong>Prefeito esclarece: programa de retorno assistido já existe há anos</strong></h2><p>Segundo Dr. Serginho, a <strong>Secretaria de Assistência Social de Cabo Frio</strong> atua há anos com um programa de <strong>retorno assistido</strong>, que viabiliza o deslocamento de pessoas em situação de rua para suas cidades de origem, <strong>a pedido delas mesmas</strong>.</p><p>📍 O grupo encaminhado a Linhares teria manifestado o desejo de retornar por <strong>motivos pessoais e vínculos familiares</strong> com o município capixaba.</p><blockquote><p>\"Não abandonamos ninguém. Aquelas pessoas pediram para voltar, e levamos com dignidade, com alimentação e respeito\", declarou o prefeito.</p></blockquote><hr><h2>👩‍🍼 <strong>Gestante também pediu para ir</strong></h2><p>Entre os encaminhados estava uma <strong>mulher grávida</strong> que, segundo o prefeito, é cabo-friense e solicitou a viagem por <strong>questões de segurança pessoal</strong>, afirmando estar sofrendo ameaças. A decisão de se mudar foi <strong>voluntária e acompanhada por profissionais da assistência social</strong>.</p><hr><h2>⚖️ <strong>Críticas ao uso político e sensacionalismo</strong></h2><p>Dr. Serginho criticou a postura da administração de Linhares, classificando a repercussão como <strong>politicamente motivada e sensacionalista</strong>. Ele também afirmou que <strong>a Prefeitura de Cabo Frio está à disposição para prestar todos os esclarecimentos formais necessários</strong>.</p><hr><h2>🤝 <strong>O debate está aberto: responsabilidade compartilhada entre municípios</strong></h2><p>O caso provocou grande repercussão nas redes sociais e reacende o debate sobre <strong>a responsabilidade compartilhada entre cidades</strong> no cuidado com pessoas em situação de vulnerabilidade.</p><p>📢 Acompanhe a Central Unamar para mais atualizações sobre o caso e outros assuntos relevantes da nossa região.</p>\n"
        "\nINFORMAÇÕES DA NOTÍCIA:\n" + noticia.get('texto', '')
    )
    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    try:
        resp = requests.post(GEMINI_API_URL, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        content = data['candidates'][0]['content']['parts'][0]['text']
        return content.strip()
    except Exception as e:
        print(f"[Gemini] Erro ao gerar content: {e}. Usando texto original.")
        return gerar_html_estruturado(noticia)

def montar_json_supabase(noticia, resultado_publicacao):
    agora = datetime.datetime.now()
    data_iso = agora.strftime('%Y-%m-%d')
    data_full = agora.strftime('%Y-%m-%dT%H:%M:%SZ')
    slug = gerar_slug(noticia.get('titulo', ''))
    categorias = noticia.get('categorias', ['geral'])
    categoria_interna = categorias[0].lower() if categorias else 'geral'
    categoria_oficial = CATEGORIAS_OFICIAIS.get(categoria_interna, 'Eventos e cultura')
    excerpt = gerar_excerpt_gemini(noticia)
    content_html = gerar_content_gemini(noticia)
    return {
        "user_id": SUPABASE_USER_ID,
        "slug": slug,
        "title": noticia.get('titulo', ''),
        "excerpt": excerpt,
        "content": content_html,
        "category": categoria_oficial,
        "images": [],
        "date": data_iso,
        "created_at": data_full,
        "updated_at": data_full
    }

def postar_supabase(json_noticia):
    try:
        resp = supabase.table('news').insert(json_noticia).execute()
        if hasattr(resp, 'data'):
            print(f"[SUPABASE] Notícia inserida com sucesso: {json_noticia['slug']}")
        else:
            print(f"[SUPABASE] Falha ao inserir notícia: {resp}")
    except Exception as e:
        print(f"[SUPABASE] Erro ao inserir notícia: {e}")

def main():
    """Função principal para automatizar a publicação de notícias."""
    print("Iniciando automação de publicação de notícias na plataforma Central Unamar...")
    
    # Carrega as notícias redigidas
    noticias_por_regiao = carregar_noticias_redigidas()
    
    if not noticias_por_regiao:
        print("Nenhuma notícia redigida encontrada para publicação.")
        return
    
    resultados_publicacao = []
    
    # Para cada região, publica as notícias
    for regiao, noticias in noticias_por_regiao.items():
        print(f"Publicando {len(noticias)} notícias para {regiao}...")
        
        for noticia in noticias:
            # Prepara o payload
            payload = preparar_payload_noticia(noticia)
            
            # Publica a notícia
            resultado = publicar_noticia_api(payload)
            
            # Registra o log
            registrar_log(noticia, resultado)
            
            # Atualiza o status da notícia
            noticia['status_publicacao'] = 'publicada' if resultado.get('sucesso', False) else 'falha'
            noticia['resultado_publicacao'] = resultado
            
            resultados_publicacao.append({
                'titulo': noticia.get('titulo', ''),
                'regiao': regiao,
                'sucesso': resultado.get('sucesso', False),
                'url': resultado.get('url', ''),
                'mensagem': resultado.get('mensagem', '')
            })
            
            # Posta no Supabase se publicação foi bem-sucedida
            if resultado.get('sucesso', False):
                json_supabase = montar_json_supabase(noticia, resultado)
                postar_supabase(json_supabase)
            # Pausa para evitar sobrecarga na API
            time.sleep(random.uniform(1.0, 2.0))
    
    # Salva o relatório de publicação
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    relatorio_filename = LOGS_DIR / f"relatorio_publicacao_{timestamp}.json"
    
    with open(relatorio_filename, 'w', encoding='utf-8') as f:
        json.dump(resultados_publicacao, f, ensure_ascii=False, indent=4)
    
    print(f"Relatório de publicação salvo em {relatorio_filename}")
    print("Automação de publicação de notícias concluída!")

if __name__ == "__main__":
    # Cria diretório de logs se não existir
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Executa a função principal
    main()
