#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para redigir automaticamente notícias baseadas nas informações coletadas.
Utiliza templates e técnicas de geração de texto para criar notícias prontas para publicação.
"""

import os
import sys
import json
import datetime
import random
from pathlib import Path

# Configurações

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "dados" / "processados"
OUTPUT_DIR = BASE_DIR / "noticias_geradas"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Templates para diferentes categorias de notícias
TEMPLATES = {
    "policial": [
        "{titulo}\n\n{data_formatada} - {intro_texto} {detalhe_local}.\n\n{corpo_texto}\n\n\n{conclusao}\n\nFonte: {portal}. Acesse a notícia original em: {link}",
        "SEGURANÇA: {titulo}\n\n{data_formatada} - {intro_texto} {detalhe_local}.\n\n{corpo_texto}\n\n{conclusao}\n\nFonte: {portal}. Leia mais em: {link}"
    ],
    "saude": [
        "{titulo}\n\n{data_formatada} - {intro_texto} {detalhe_local}.\n\n{corpo_texto}\n\n\n{conclusao}\n\nFonte: {portal}. Acesse a notícia original em: {link}",
        "SAÚDE: {titulo}\n\n{data_formatada} - {intro_texto} {detalhe_local}.\n\n{corpo_texto}\n\n{conclusao}\n\nFonte: {portal}. Leia mais em: {link}"
    ],
    "politica": [
        "{titulo}\n\n{data_formatada} - {intro_texto} {detalhe_local}.\n\n{corpo_texto}\n\n{conclusao}\n\nFonte: {portal}. Acesse a notícia original em: {link}",
        "POLÍTICA: {titulo}\n\n{data_formatada} - {intro_texto} {detalhe_local}.\n\n{corpo_texto}\n\n{conclusao}\n\nFonte: {portal}. Leia mais em: {link}"
    ],
    "geral": [
        "{titulo}\n\n{data_formatada} - {intro_texto} {detalhe_local}.\n\n{corpo_texto}\n\n{conclusao}\n\nFonte: {portal}. Acesse a notícia original em: {link}",
        "{titulo}\n\n{data_formatada} - {intro_texto} {detalhe_local}.\n\n{corpo_texto}\n\n{conclusao}\n\nFonte: {portal}. Leia mais em: {link}"
    ]
}

# Frases para introdução por categoria
INTRO_FRASES = {
    "policial": [
        "Um caso de violência foi registrado",
        "A Polícia Civil prendeu um suspeito",
        "Um incidente violento foi reportado",
        "As autoridades policiais agiram rapidamente",
        "Um crime foi registrado pelas autoridades"
    ],
    "saude": [
        "Um caso médico foi atendido",
        "Profissionais de saúde prestaram atendimento",
        "Um incidente com ferimentos foi reportado",
        "Serviços de emergência foram acionados",
        "Uma ocorrência médica foi registrada"
    ],
    "politica": [
        "Uma importante decisão foi tomada",
        "Autoridades municipais anunciaram",
        "Um novo projeto foi apresentado",
        "Representantes do governo local informaram",
        "Uma medida administrativa foi implementada"
    ],
    "geral": [
        "Um fato importante foi registrado",
        "Um acontecimento chamou atenção",
        "Um evento relevante ocorreu",
        "Uma situação inusitada foi reportada",
        "Um caso interessante foi documentado"
    ]
}

# Frases para conclusão por categoria
CONCLUSAO_FRASES = {
    "policial": [
        "A Polícia Civil continua investigando o caso e busca mais informações sobre as circunstâncias do ocorrido.",
        "As autoridades pedem que testemunhas que possam ter presenciado o incidente entrem em contato.",
        "O caso segue sob investigação e mais detalhes podem ser divulgados nos próximos dias.",
        "A segurança na região tem sido reforçada após o incidente, segundo informações das autoridades.",
        "A população é orientada a denunciar casos semelhantes através dos canais oficiais de segurança."
    ],
    "saude": [
        "As autoridades de saúde reforçam a importância de buscar atendimento médico imediato em casos semelhantes.",
        "Profissionais da área recomendam atenção aos sinais de alerta para prevenir situações como esta.",
        "O caso serve como alerta para a importância dos primeiros socorros e atendimento rápido.",
        "A Secretaria de Saúde está monitorando a situação e prestando todo o suporte necessário.",
        "Campanhas de conscientização sobre o tema devem ser intensificadas na região."
    ],
    "politica": [
        "A administração municipal promete novas ações nos próximos dias para atender às demandas da população.",
        "O tema deve voltar a ser discutido na próxima reunião da Câmara Municipal.",
        "A população pode acompanhar os desdobramentos através dos canais oficiais da prefeitura.",
        "Especialistas consideram a medida importante para o desenvolvimento da região.",
        "Novas informações serão divulgadas à medida que o projeto avançar."
    ],
    "geral": [
        "O caso tem chamado a atenção dos moradores da região e gerado discussões nas redes sociais.",
        "Situações como esta reforçam a importância da atenção e cuidado no dia a dia.",
        "A comunidade local tem se mobilizado em resposta ao ocorrido.",
        "Especialistas recomendam atenção a situações semelhantes que possam ocorrer.",
        "Mais informações sobre o caso podem ser divulgadas nos próximos dias."
    ]
}

def formatar_data(data_texto):
    """
    Formata a data de publicação para um formato mais amigável.
    
    Args:
        data_texto (str): Texto da data original
        
    Returns:
        str: Data formatada
    """
    hoje = datetime.datetime.now()
    
    if "Há" in data_texto:
        if "horas" in data_texto or "hora" in data_texto:
            return f"Hoje, {hoje.strftime('%d de %B de %Y')}"
        elif "dias" in data_texto or "dia" in data_texto:
            try:
                dias = int(data_texto.split()[1])
                data = hoje - datetime.timedelta(days=dias)
                return data.strftime('%d de %B de %Y')
            except:
                return hoje.strftime('%d de %B de %Y')
    
    # Se não conseguir interpretar, retorna a data atual
    return hoje.strftime('%d de %B de %Y')

def gerar_detalhe_local(noticia):
    """
    Gera texto detalhando o local do acontecimento.
    
    Args:
        noticia (dict): Dados da notícia
        
    Returns:
        str: Texto com detalhes do local
    """
    locais = noticia.get('locais_mencionados', [])
    regiao = noticia.get('regiao_especifica', '').replace('_', ' ').title()
    
    if locais:
        local = locais[0]
        return f"no {local} de {regiao}"
    else:
        return f"em {regiao}"

def gerar_corpo_texto(noticia):
    """
    Gera o corpo principal do texto da notícia.
    
    Args:
        noticia (dict): Dados da notícia
        
    Returns:
        str: Corpo do texto da notícia
    """
    resumo = noticia.get('resumo', '')
    
    # Expande o resumo em parágrafos
    paragrafos = []
    
    # Divide o resumo em frases
    frases = resumo.split('. ')
    
    # Agrupa as frases em parágrafos
    if len(frases) <= 2:
        paragrafos.append(resumo)
    else:
        meio = len(frases) // 2
        paragrafos.append('. '.join(frases[:meio]) + '.')
        paragrafos.append('. '.join(frases[meio:]))
    
    return '\n\n'.join(paragrafos)

def gerar_citacao(noticia, categoria):
    """
    Gera uma citação relevante para a notícia.
    
    Args:
        noticia (dict): Dados da notícia
        categoria (str): Categoria da notícia
        
    Returns:
        str: Texto com citação
    """
    if categoria == "policial":
        return '"Estamos investigando todos os detalhes do caso e tomando as medidas cabíveis conforme a lei", informou a Polícia Civil em nota oficial.'
    
    elif categoria == "saude":
        return '"É fundamental que vítimas de agressão procurem atendimento médico imediatamente, mesmo que os ferimentos pareçam leves", destacou um profissional de saúde que atendeu o caso.'
    
    elif categoria == "politica":
        return '"A administração municipal está atenta a todos os acontecimentos e trabalhando para garantir a segurança e bem-estar dos cidadãos", afirmou a assessoria da Prefeitura.'
    
    else:
        return '"A comunidade está acompanhando o caso com atenção e espera que as autoridades tomem as providências necessárias", comentou um morador da região.'

def redigir_noticia(noticia):
    """
    Redige uma notícia completa baseada nos dados processados.
    
    Args:
        noticia (dict): Dados da notícia processada
        
    Returns:
        dict: Notícia redigida com metadados
    """
    # Determina a categoria principal
    categorias = noticia.get('categorias', ['geral'])
    categoria_principal = categorias[0] if categorias else 'geral'
    
    # Seleciona um template aleatório para a categoria
    template = random.choice(TEMPLATES.get(categoria_principal, TEMPLATES['geral']))
    
    # Prepara os dados para o template
    dados_template = {
        'titulo': noticia.get('titulo', ''),
        'data_formatada': formatar_data(noticia.get('data_publicacao', '')),
        'intro_texto': random.choice(INTRO_FRASES.get(categoria_principal, INTRO_FRASES['geral'])),
        'detalhe_local': gerar_detalhe_local(noticia),
        'corpo_texto': gerar_corpo_texto(noticia),
        'conclusao': random.choice(CONCLUSAO_FRASES.get(categoria_principal, CONCLUSAO_FRASES['geral'])),
        'portal': noticia.get('portal', ''),
        'link': noticia.get('link', '')
    }
    
    # Gera o texto da notícia
    texto_noticia = template.format(**dados_template)
    
    # Cria o objeto da notícia redigida
    noticia_redigida = {
        'titulo': noticia.get('titulo', ''),
        'texto': texto_noticia,
        'regiao': noticia.get('regiao_especifica', ''),
        'categorias': noticia.get('categorias', []),
        'fonte_original': noticia.get('portal', ''),
        'link_original': noticia.get('link', ''),
        'data_publicacao_original': noticia.get('data_publicacao', ''),
        'data_redacao': datetime.datetime.now().isoformat(),
        'status_publicacao': 'pendente'
    }
    
    return noticia_redigida

def carregar_noticias_processadas():
    """
    Carrega as notícias processadas dos arquivos JSON.
    
    Returns:
        dict: Notícias processadas por região
    """
    noticias_por_regiao = {}
    
    # Busca arquivos de notícias processadas por região
    arquivos_json = list(INPUT_DIR.glob("noticias_*_*.json"))
    
    if not arquivos_json:
        print("Nenhum arquivo de notícias processadas encontrado.")
        return noticias_por_regiao
    
    # Carrega as notícias de cada arquivo
    for arquivo in arquivos_json:
        if "todas_noticias_processadas" in arquivo.name:
            continue  # Pula o arquivo consolidado
            
        try:
            regiao = arquivo.stem.split('_')[1]  # Extrai a região do nome do arquivo
            
            with open(arquivo, 'r', encoding='utf-8') as f:
                noticias = json.load(f)
                
                if isinstance(noticias, list):
                    noticias_por_regiao[regiao] = noticias
                    print(f"Carregadas {len(noticias)} notícias processadas para {regiao}")
        except Exception as e:
            print(f"Erro ao carregar notícias de {arquivo.name}: {e}")
    
    return noticias_por_regiao

def salvar_noticias_redigidas(noticias_redigidas, regiao):
    """
    Salva as notícias redigidas em arquivos JSON.
    
    Args:
        noticias_redigidas (list): Lista de notícias redigidas
        regiao (str): Nome da região
    """
    if not noticias_redigidas:
        print(f"Nenhuma notícia redigida para a região {regiao}")
        return
    
    # Cria o nome do arquivo com timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = OUTPUT_DIR / f"noticias_redigidas_{regiao}_{timestamp}.json"
    
    # Salva as notícias em um arquivo JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(noticias_redigidas, f, ensure_ascii=False, indent=4)
    
    print(f"Salvas {len(noticias_redigidas)} notícias redigidas para {regiao} em {filename}")
    
    # Também salva cada notícia em um arquivo de texto separado para facilitar a visualização
    for i, noticia in enumerate(noticias_redigidas):
        texto_filename = OUTPUT_DIR / f"noticia_{regiao}_{i+1}_{timestamp}.txt"
        
        with open(texto_filename, 'w', encoding='utf-8') as f:
            f.write(noticia['texto'])
        
        print(f"Texto da notícia {i+1} salvo em {texto_filename}")

def main():
    """Função principal para redigir notícias automaticamente."""
    print("Iniciando redação automática de notícias...")
    
    # Carrega as notícias processadas
    noticias_por_regiao = carregar_noticias_processadas()
    
    if not noticias_por_regiao:
        print("Nenhuma notícia processada encontrada para redigir.")
        return
    
    # Para cada região, redige as notícias
    for regiao, noticias in noticias_por_regiao.items():
        print(f"Redigindo {len(noticias)} notícias para {regiao}...")
        
        noticias_redigidas = []
        
        for noticia in noticias:
            # Redige a notícia
            noticia_redigida = redigir_noticia(noticia)
            noticias_redigidas.append(noticia_redigida)
        
        # Salva as notícias redigidas
        salvar_noticias_redigidas(noticias_redigidas, regiao)
    
    print("Redação automática de notícias concluída!")

if __name__ == "__main__":
    # Cria diretório de saída se não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Executa a função principal
    main()
