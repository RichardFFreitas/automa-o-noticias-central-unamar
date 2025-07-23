#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para extrair e filtrar informações relevantes das notícias coletadas.
Categoriza as notícias por região e prepara os dados para redação automática.
"""

import os
import sys
import json
import datetime
import re
from pathlib import Path

# Configurações
INPUT_DIR = Path("/home/lawli/projects/automacao_noticias_central_unamar/dados")
OUTPUT_DIR = Path("/home/lawli/projects/automacao_noticias_central_unamar/dados/processados")
OUTPUT_DIR.mkdir(exist_ok=True)

# Regiões de interesse
REGIOES = {
    "cabo_frio": ["cabo frio", "centro de cabo frio", "centro da cidade"],
    "unamar": ["unamar"],
    "tamoios": ["tamoios", "segundo distrito"],
    "barra_sao_joao": ["barra de são joão", "barra de sao joao", "barra são joão"]
}

def carregar_noticias():
    """
    Carrega todas as notícias coletadas dos arquivos JSON.
    
    Returns:
        list: Lista de todas as notícias carregadas
    """
    todas_noticias = []
    
    # Busca todos os arquivos JSON no diretório de dados
    arquivos_json = list(INPUT_DIR.glob("*.json"))
    
    if not arquivos_json:
        print("Nenhum arquivo de notícias encontrado.")
        return todas_noticias
    
    # Carrega as notícias de cada arquivo
    for arquivo in arquivos_json:
        if arquivo.name.startswith("todas_noticias_"):
            continue  # Pula o arquivo consolidado para evitar duplicações
            
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                noticias = json.load(f)
                
                if isinstance(noticias, list):
                    todas_noticias.extend(noticias)
                    print(f"Carregadas {len(noticias)} notícias de {arquivo.name}")
        except Exception as e:
            print(f"Erro ao carregar notícias de {arquivo.name}: {e}")
    
    return todas_noticias

def determinar_regiao(noticia):
    """
    Determina a região específica a que a notícia pertence.
    
    Args:
        noticia (dict): Dados da notícia
        
    Returns:
        str: Nome da região determinada
    """
    # Textos para análise
    titulo = noticia.get('titulo', '').lower()
    resumo = noticia.get('resumo', '').lower()
    regiao_original = noticia.get('regiao', '').lower()
    
    texto_completo = f"{titulo} {resumo} {regiao_original}"
    
    # Verifica cada região
    for regiao, palavras_chave in REGIOES.items():
        for palavra in palavras_chave:
            if palavra in texto_completo:
                return regiao
    
    # Se não encontrar correspondência específica, usa a região original
    if "região dos lagos" in regiao_original:
        return "regiao_dos_lagos"
    
    # Caso não identifique nenhuma região específica
    return "indefinida"

def extrair_informacoes_relevantes(noticia):
    """
    Extrai e estrutura informações relevantes da notícia.
    
    Args:
        noticia (dict): Dados da notícia original
        
    Returns:
        dict: Notícia com informações estruturadas
    """
    # Copia os dados básicos
    noticia_processada = {
        'titulo': noticia.get('titulo', ''),
        'resumo': noticia.get('resumo', ''),
        'link': noticia.get('link', ''),
        'portal': noticia.get('portal', ''),
        'data_publicacao': noticia.get('data_publicacao', ''),
        'data_coleta': noticia.get('data_coleta', datetime.datetime.now().isoformat()),
        'regiao_original': noticia.get('regiao', ''),
        'regiao_especifica': determinar_regiao(noticia)
    }
    
    # Extrai entidades mencionadas (pessoas, locais)
    texto_completo = f"{noticia_processada['titulo']} {noticia_processada['resumo']}"
    
    # Extrai possíveis pessoas mencionadas (nomes próprios)
    pessoas = re.findall(r'[A-Z][a-z]+ [A-Z][a-z]+', texto_completo)
    noticia_processada['pessoas_mencionadas'] = list(set(pessoas))
    
    # Extrai possíveis locais específicos
    locais = []
    padroes_locais = [
        r'no [A-Z][a-z]+',
        r'na [A-Z][a-z]+',
        r'em [A-Z][a-z]+'
    ]
    
    for padrao in padroes_locais:
        matches = re.findall(padrao, texto_completo)
        locais.extend([match.split(' ', 1)[1] for match in matches])
    
    noticia_processada['locais_mencionados'] = list(set(locais))
    
    # Determina categoria da notícia
    categorias = {
        'policial': ['preso', 'suspeito', 'crime', 'polícia', 'agredir', 'agressão', 'violência'],
        'politica': ['prefeitura', 'prefeito', 'vereador', 'câmara', 'eleição', 'político'],
        'saude': ['saúde', 'hospital', 'médico', 'doença', 'tratamento', 'paciente'],
        'educacao': ['escola', 'educação', 'estudante', 'professor', 'aula', 'ensino'],
        'turismo': ['turismo', 'praia', 'turista', 'temporada', 'hospedagem', 'hotel'],
        'cultura': ['cultura', 'evento', 'show', 'festival', 'exposição', 'teatro'],
        'esporte': ['esporte', 'campeonato', 'jogo', 'atleta', 'competição', 'torneio']
    }
    
    texto_categorias = texto_completo.lower()
    noticia_processada['categorias'] = []
    
    for categoria, palavras in categorias.items():
        if any(palavra in texto_categorias for palavra in palavras):
            noticia_processada['categorias'].append(categoria)
    
    # Se nenhuma categoria for identificada
    if not noticia_processada['categorias']:
        noticia_processada['categorias'] = ['geral']
    
    return noticia_processada

def processar_noticias(noticias):
    """
    Processa todas as notícias, extraindo informações relevantes.
    
    Args:
        noticias (list): Lista de notícias originais
        
    Returns:
        dict: Notícias processadas, organizadas por região
    """
    noticias_por_regiao = {
        'cabo_frio': [],
        'unamar': [],
        'tamoios': [],
        'barra_sao_joao': [],
        'regiao_dos_lagos': [],
        'indefinida': []
    }
    
    for noticia in noticias:
        # Extrai informações relevantes
        noticia_processada = extrair_informacoes_relevantes(noticia)
        
        # Adiciona à região correspondente
        regiao = noticia_processada['regiao_especifica']
        noticias_por_regiao[regiao].append(noticia_processada)
    
    return noticias_por_regiao

def salvar_noticias_processadas(noticias_por_regiao):
    """
    Salva as notícias processadas em arquivos JSON, organizadas por região.
    
    Args:
        noticias_por_regiao (dict): Notícias processadas, organizadas por região
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salva um arquivo para cada região
    for regiao, noticias in noticias_por_regiao.items():
        if not noticias:
            print(f"Nenhuma notícia encontrada para a região {regiao}")
            continue
        
        filename = OUTPUT_DIR / f"noticias_{regiao}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(noticias, f, ensure_ascii=False, indent=4)
        
        print(f"Salvas {len(noticias)} notícias processadas para {regiao} em {filename}")
    
    # Salva todas as notícias processadas em um único arquivo
    todas_processadas = []
    for noticias in noticias_por_regiao.values():
        todas_processadas.extend(noticias)
    
    if todas_processadas:
        filename = OUTPUT_DIR / f"todas_noticias_processadas_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(todas_processadas, f, ensure_ascii=False, indent=4)
        
        print(f"Total de {len(todas_processadas)} notícias processadas salvas em {filename}")

def main():
    """Função principal para extrair e filtrar informações das notícias."""
    print("Iniciando extração e filtragem de informações das notícias...")
    
    # Carrega todas as notícias coletadas
    noticias = carregar_noticias()
    
    if not noticias:
        print("Nenhuma notícia encontrada para processar.")
        return
    
    print(f"Carregadas {len(noticias)} notícias para processamento.")
    
    # Processa as notícias
    noticias_por_regiao = processar_noticias(noticias)
    
    # Salva as notícias processadas
    salvar_noticias_processadas(noticias_por_regiao)
    
    print("Extração e filtragem de informações concluídas!")

if __name__ == "__main__":
    # Cria diretório de saída se não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Executa a função principal
    main()
