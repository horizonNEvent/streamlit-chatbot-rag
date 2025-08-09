"""
Identificador de empresas e transmissoras usando JSONs
"""
import json
import re
import streamlit as st

def load_json_data():
    """
    Carrega os dados dos JSONs
    """
    try:
        # Carregar transmissoras
        with open('TransmissorasTust.json', 'r', encoding='utf-8') as f:
            transmissoras_data = json.load(f)
        
        # Carregar empresas
        with open('EmpresasTust.json', 'r', encoding='utf-8') as f:
            empresas_data = json.load(f)
        
        return transmissoras_data, empresas_data
    
    except Exception as e:
        st.error(f"Erro ao carregar JSONs: {str(e)}")
        return None, None

def normalize_cnpj(cnpj):
    """
    Normaliza CNPJ removendo pontuações
    """
    if cnpj:
        return re.sub(r'[^\d]', '', str(cnpj))
    return ""

def extract_cnpjs_from_text(text):
    """
    Extrai todos os CNPJs do texto
    """
    # Padrão para CNPJ com ou sem formatação
    cnpj_pattern = r'\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}'
    cnpjs = re.findall(cnpj_pattern, text)
    return [normalize_cnpj(cnpj) for cnpj in cnpjs]

def find_transmissora(cnpj=None, nome=None, codigo_ons=None):
    """
    Encontra transmissora pelos critérios fornecidos
    """
    transmissoras_data, _ = load_json_data()
    if not transmissoras_data:
        return None
    
    # Normalizar CNPJ de busca
    cnpj_busca = normalize_cnpj(cnpj) if cnpj else None
    
    # Buscar nas transmissoras
    for transmissora in transmissoras_data.get('results', [{}])[0].get('items', []):
        # Busca por CNPJ
        if cnpj_busca and normalize_cnpj(transmissora.get('codigo_fornecedor')) == cnpj_busca:
            return transmissora
        
        # Busca por nome (case insensitive)
        if nome and transmissora.get('nome', '').upper() == nome.upper():
            return transmissora
        
        # Busca por código ONS
        if codigo_ons and transmissora.get('codigo_ons') == str(codigo_ons):
            return transmissora
    
    return None

def find_empresa_pagadora(cnpj=None, nome=None):
    """
    Encontra empresa pagadora pelos critérios fornecidos
    """
    _, empresas_data = load_json_data()
    if not empresas_data:
        return None, None
    
    # Normalizar CNPJ de busca
    cnpj_busca = normalize_cnpj(cnpj) if cnpj else None
    
    # Buscar em todas as categorias (RE, AE, DE)
    for categoria, empresas in empresas_data.items():
        for codigo_empresa, dados_empresa in empresas.items():
            # Busca por CNPJ
            if cnpj_busca and normalize_cnpj(dados_empresa.get('cnpj')) == cnpj_busca:
                return categoria, {
                    'codigo': codigo_empresa,
                    'nome': dados_empresa.get('nome'),
                    'cnpj': dados_empresa.get('cnpj'),
                    'codigo_neoenergia': dados_empresa.get('codigoneoenergia'),
                    'categoria': categoria
                }
            
            # Busca por nome (case insensitive)
            if nome and dados_empresa.get('nome', '').upper() == nome.upper():
                return categoria, {
                    'codigo': codigo_empresa,
                    'nome': dados_empresa.get('nome'),
                    'cnpj': dados_empresa.get('cnpj'),
                    'codigo_neoenergia': dados_empresa.get('codigoneoenergia'),
                    'categoria': categoria
                }
    
    return None, None

def identify_companies_from_boleto(boleto_text):
    """
    Identifica transmissora e empresa pagadora a partir do texto do boleto
    """
    result = {
        'transmissora': None,
        'empresa_pagadora': None,
        'cnpjs_encontrados': [],
        'sucesso': False
    }
    
    try:
        # Extrair CNPJs do boleto
        cnpjs = extract_cnpjs_from_text(boleto_text)
        result['cnpjs_encontrados'] = cnpjs
        
        # Tentar identificar transmissora e empresa para cada CNPJ
        for cnpj in cnpjs:
            # Buscar transmissora
            if not result['transmissora']:
                transmissora = find_transmissora(cnpj=cnpj)
                if transmissora:
                    result['transmissora'] = transmissora
            
            # Buscar empresa pagadora
            if not result['empresa_pagadora']:
                categoria, empresa = find_empresa_pagadora(cnpj=cnpj)
                if empresa:
                    result['empresa_pagadora'] = empresa
        
        # Marcar como sucesso se encontrou pelo menos uma identificação
        result['sucesso'] = bool(result['transmissora'] or result['empresa_pagadora'])
        
        return result
    
    except Exception as e:
        st.error(f"Erro na identificação: {str(e)}")
        return result