#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para validar a automação e qualidade das notícias geradas.
Analisa todo o fluxo e gera relatório de validação.
"""

import os
import sys
import json
import datetime
import glob
from pathlib import Path

# Configurações
PROJECT_DIR = Path("/home/lawli/projects/automacao_noticias_central_unamar")
VALIDATION_DIR = PROJECT_DIR / "validacao"
VALIDATION_DIR.mkdir(exist_ok=True)

def contar_arquivos_por_diretorio():
    """
    Conta os arquivos em cada diretório do projeto.
    
    Returns:
        dict: Contagem de arquivos por diretório
    """
    contagem = {}
    
    # Lista de diretórios para verificar
    diretorios = [
        "fontes",
        "scripts",
        "dados",
        "dados/processados",
        "noticias_geradas",
        "logs"
    ]
    
    for diretorio in diretorios:
        caminho = PROJECT_DIR / diretorio
        if caminho.exists():
            arquivos = list(caminho.glob("*.*"))
            contagem[diretorio] = len(arquivos)
        else:
            contagem[diretorio] = 0
    
    return contagem

def validar_scripts():
    """
    Valida a existência e permissões dos scripts principais.
    
    Returns:
        dict: Resultado da validação dos scripts
    """
    scripts = [
        "twitter_collector.py",
        "portal_collector.py",
        "portal_collector_improved.py",
        "news_processor.py",
        "news_writer.py",
        "news_publisher.py"
    ]
    
    resultado = {}
    
    for script in scripts:
        caminho = PROJECT_DIR / "scripts" / script
        if caminho.exists():
            resultado[script] = {
                "existe": True,
                "executavel": os.access(caminho, os.X_OK),
                "tamanho": caminho.stat().st_size,
                "ultima_modificacao": datetime.datetime.fromtimestamp(caminho.stat().st_mtime).isoformat()
            }
        else:
            resultado[script] = {
                "existe": False
            }
    
    return resultado

def validar_fluxo_dados():
    """
    Valida o fluxo de dados entre as etapas da automação.
    
    Returns:
        dict: Resultado da validação do fluxo de dados
    """
    resultado = {
        "coleta": {
            "arquivos": [],
            "status": "não iniciado"
        },
        "processamento": {
            "arquivos": [],
            "status": "não iniciado"
        },
        "redacao": {
            "arquivos": [],
            "status": "não iniciado"
        },
        "publicacao": {
            "arquivos": [],
            "status": "não iniciado"
        }
    }
    
    # Verifica arquivos de coleta
    arquivos_coleta = list((PROJECT_DIR / "dados").glob("*.json"))
    if arquivos_coleta:
        resultado["coleta"]["arquivos"] = [arquivo.name for arquivo in arquivos_coleta]
        resultado["coleta"]["status"] = "concluído"
    
    # Verifica arquivos de processamento
    arquivos_processamento = list((PROJECT_DIR / "dados" / "processados").glob("*.json"))
    if arquivos_processamento:
        resultado["processamento"]["arquivos"] = [arquivo.name for arquivo in arquivos_processamento]
        resultado["processamento"]["status"] = "concluído"
    
    # Verifica arquivos de redação
    arquivos_redacao = list((PROJECT_DIR / "noticias_geradas").glob("*.json"))
    arquivos_redacao_txt = list((PROJECT_DIR / "noticias_geradas").glob("*.txt"))
    if arquivos_redacao or arquivos_redacao_txt:
        resultado["redacao"]["arquivos"] = [arquivo.name for arquivo in arquivos_redacao + arquivos_redacao_txt]
        resultado["redacao"]["status"] = "concluído"
    
    # Verifica arquivos de publicação
    arquivos_publicacao = list((PROJECT_DIR / "logs").glob("*.json"))
    if arquivos_publicacao:
        resultado["publicacao"]["arquivos"] = [arquivo.name for arquivo in arquivos_publicacao]
        resultado["publicacao"]["status"] = "concluído"
    
    return resultado

def validar_qualidade_noticias():
    """
    Valida a qualidade das notícias geradas.
    
    Returns:
        dict: Resultado da validação de qualidade
    """
    resultado = {
        "noticias_analisadas": 0,
        "criterios": {
            "titulo_presente": 0,
            "conteudo_completo": 0,
            "fonte_citada": 0,
            "regiao_identificada": 0,
            "categorias_atribuidas": 0
        },
        "amostras": []
    }
    
    # Busca arquivos de notícias redigidas
    arquivos_noticias = list((PROJECT_DIR / "noticias_geradas").glob("noticias_redigidas_*.json"))
    
    for arquivo in arquivos_noticias:
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                noticias = json.load(f)
                
                if isinstance(noticias, list):
                    resultado["noticias_analisadas"] += len(noticias)
                    
                    for noticia in noticias:
                        # Verifica critérios de qualidade
                        if noticia.get('titulo', ''):
                            resultado["criterios"]["titulo_presente"] += 1
                        
                        if noticia.get('texto', '') and len(noticia.get('texto', '')) > 100:
                            resultado["criterios"]["conteudo_completo"] += 1
                        
                        if "Fonte:" in noticia.get('texto', ''):
                            resultado["criterios"]["fonte_citada"] += 1
                        
                        if noticia.get('regiao', ''):
                            resultado["criterios"]["regiao_identificada"] += 1
                        
                        if noticia.get('categorias', []):
                            resultado["criterios"]["categorias_atribuidas"] += 1
                        
                        # Adiciona amostra
                        if len(resultado["amostras"]) < 3:  # Limita a 3 amostras
                            resultado["amostras"].append({
                                "titulo": noticia.get('titulo', ''),
                                "categorias": noticia.get('categorias', []),
                                "regiao": noticia.get('regiao', ''),
                                "tamanho_texto": len(noticia.get('texto', ''))
                            })
        except Exception as e:
            print(f"Erro ao analisar notícias de {arquivo.name}: {e}")
    
    return resultado

def validar_logs_publicacao():
    """
    Valida os logs de publicação.
    
    Returns:
        dict: Resultado da validação dos logs
    """
    resultado = {
        "logs_analisados": 0,
        "publicacoes_sucesso": 0,
        "publicacoes_falha": 0,
        "detalhes": []
    }
    
    # Busca arquivos de log de publicação
    arquivos_log = list((PROJECT_DIR / "logs").glob("publicacao_log_*.json"))
    
    for arquivo in arquivos_log:
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                log = json.load(f)
                
                resultado["logs_analisados"] += 1
                
                if log.get('resultado', {}).get('sucesso', False):
                    resultado["publicacoes_sucesso"] += 1
                else:
                    resultado["publicacoes_falha"] += 1
                
                # Adiciona detalhes
                resultado["detalhes"].append({
                    "titulo": log.get('titulo_noticia', ''),
                    "regiao": log.get('regiao', ''),
                    "sucesso": log.get('resultado', {}).get('sucesso', False),
                    "timestamp": log.get('timestamp', '')
                })
        except Exception as e:
            print(f"Erro ao analisar log de {arquivo.name}: {e}")
    
    return resultado

def gerar_relatorio_validacao():
    """
    Gera um relatório completo de validação da automação.
    
    Returns:
        dict: Relatório de validação
    """
    timestamp = datetime.datetime.now().isoformat()
    
    relatorio = {
        "timestamp": timestamp,
        "contagem_arquivos": contar_arquivos_por_diretorio(),
        "validacao_scripts": validar_scripts(),
        "validacao_fluxo": validar_fluxo_dados(),
        "validacao_qualidade": validar_qualidade_noticias(),
        "validacao_publicacao": validar_logs_publicacao(),
        "conclusao": {
            "fluxo_completo": False,
            "pontos_fortes": [],
            "pontos_fracos": [],
            "recomendacoes": []
        }
    }
    
    # Analisa resultados para conclusão
    fluxo = relatorio["validacao_fluxo"]
    if (fluxo["coleta"]["status"] == "concluído" and
        fluxo["processamento"]["status"] == "concluído" and
        fluxo["redacao"]["status"] == "concluído" and
        fluxo["publicacao"]["status"] == "concluído"):
        relatorio["conclusao"]["fluxo_completo"] = True
    
    # Pontos fortes
    if relatorio["conclusao"]["fluxo_completo"]:
        relatorio["conclusao"]["pontos_fortes"].append("Fluxo completo de automação implementado com sucesso")
    
    if relatorio["validacao_qualidade"]["noticias_analisadas"] > 0:
        relatorio["conclusao"]["pontos_fortes"].append("Sistema capaz de gerar notícias automaticamente")
    
    if relatorio["validacao_publicacao"]["publicacoes_sucesso"] > 0:
        relatorio["conclusao"]["pontos_fortes"].append("Sistema capaz de publicar notícias automaticamente")
    
    # Pontos fracos
    if relatorio["contagem_arquivos"].get("dados", 0) < 5:
        relatorio["conclusao"]["pontos_fracos"].append("Quantidade limitada de dados coletados")
    
    if relatorio["validacao_qualidade"]["noticias_analisadas"] < 3:
        relatorio["conclusao"]["pontos_fracos"].append("Poucas notícias geradas para validação robusta")
    
    # Recomendações
    relatorio["conclusao"]["recomendacoes"].append("Ampliar fontes de notícias para aumentar cobertura")
    relatorio["conclusao"]["recomendacoes"].append("Implementar sistema de agendamento para coleta periódica")
    relatorio["conclusao"]["recomendacoes"].append("Adicionar validação manual antes da publicação final")
    relatorio["conclusao"]["recomendacoes"].append("Desenvolver painel de controle para monitoramento do fluxo")
    
    return relatorio

def salvar_relatorio_validacao(relatorio):
    """
    Salva o relatório de validação em formato JSON e texto.
    
    Args:
        relatorio (dict): Relatório de validação
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salva em formato JSON
    json_filename = VALIDATION_DIR / f"relatorio_validacao_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=4)
    
    print(f"Relatório de validação salvo em {json_filename}")
    
    # Salva em formato texto para fácil leitura
    txt_filename = VALIDATION_DIR / f"relatorio_validacao_{timestamp}.txt"
    
    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE VALIDAÇÃO DA AUTOMAÇÃO DE NOTÍCIAS\n")
        f.write("==============================================\n\n")
        f.write(f"Data e hora: {relatorio['timestamp']}\n\n")
        
        f.write("1. CONTAGEM DE ARQUIVOS\n")
        f.write("----------------------\n")
        for diretorio, contagem in relatorio["contagem_arquivos"].items():
            f.write(f"{diretorio}: {contagem} arquivos\n")
        f.write("\n")
        
        f.write("2. VALIDAÇÃO DE SCRIPTS\n")
        f.write("----------------------\n")
        for script, info in relatorio["validacao_scripts"].items():
            status = "✓ Presente e executável" if info.get("existe", False) and info.get("executavel", False) else "✗ Ausente ou não executável"
            f.write(f"{script}: {status}\n")
        f.write("\n")
        
        f.write("3. VALIDAÇÃO DO FLUXO DE DADOS\n")
        f.write("-----------------------------\n")
        for etapa, info in relatorio["validacao_fluxo"].items():
            f.write(f"{etapa.title()}: {info['status']}\n")
            if info["arquivos"]:
                f.write(f"  Arquivos: {', '.join(info['arquivos'][:3])}")
                if len(info["arquivos"]) > 3:
                    f.write(f" e mais {len(info['arquivos']) - 3} arquivo(s)")
                f.write("\n")
        f.write("\n")
        
        f.write("4. VALIDAÇÃO DE QUALIDADE DAS NOTÍCIAS\n")
        f.write("-------------------------------------\n")
        qualidade = relatorio["validacao_qualidade"]
        f.write(f"Notícias analisadas: {qualidade['noticias_analisadas']}\n")
        if qualidade['noticias_analisadas'] > 0:
            for criterio, valor in qualidade["criterios"].items():
                percentual = (valor / qualidade['noticias_analisadas']) * 100 if qualidade['noticias_analisadas'] > 0 else 0
                f.write(f"{criterio.replace('_', ' ').title()}: {valor}/{qualidade['noticias_analisadas']} ({percentual:.1f}%)\n")
        f.write("\n")
        
        f.write("5. VALIDAÇÃO DE PUBLICAÇÃO\n")
        f.write("--------------------------\n")
        publicacao = relatorio["validacao_publicacao"]
        f.write(f"Logs analisados: {publicacao['logs_analisados']}\n")
        f.write(f"Publicações com sucesso: {publicacao['publicacoes_sucesso']}\n")
        f.write(f"Publicações com falha: {publicacao['publicacoes_falha']}\n")
        f.write("\n")
        
        f.write("6. CONCLUSÃO\n")
        f.write("-----------\n")
        conclusao = relatorio["conclusao"]
        f.write(f"Fluxo completo: {'Sim' if conclusao['fluxo_completo'] else 'Não'}\n\n")
        
        f.write("Pontos fortes:\n")
        for ponto in conclusao["pontos_fortes"]:
            f.write(f"- {ponto}\n")
        f.write("\n")
        
        f.write("Pontos fracos:\n")
        for ponto in conclusao["pontos_fracos"]:
            f.write(f"- {ponto}\n")
        f.write("\n")
        
        f.write("Recomendações:\n")
        for rec in conclusao["recomendacoes"]:
            f.write(f"- {rec}\n")
    
    print(f"Relatório de validação em texto salvo em {txt_filename}")
    
    return json_filename, txt_filename

def main():
    """Função principal para validar a automação e qualidade das notícias."""
    print("Iniciando validação da automação de notícias...")
    
    # Gera o relatório de validação
    relatorio = gerar_relatorio_validacao()
    
    # Salva o relatório
    json_file, txt_file = salvar_relatorio_validacao(relatorio)
    
    print("Validação da automação concluída!")
    
    return json_file, txt_file

if __name__ == "__main__":
    # Cria diretório de validação se não existir
    os.makedirs(VALIDATION_DIR, exist_ok=True)
    
    # Executa a função principal
    main()
