import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage
from config.settings import MODEL_CONFIG
from utils.company_identifier import identify_companies_from_boleto

@st.cache_resource
def init_model(api_key):
    """
    Inicializa o modelo do Gemini
    """
    if not api_key:
        return None
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=MODEL_CONFIG["model_name"],
            google_api_key=api_key,
            temperature=MODEL_CONFIG["temperature"],
            max_tokens=MODEL_CONFIG["max_tokens"]
        )
        return llm
    except Exception as e:
        st.error(f"Erro ao inicializar o modelo: {str(e)}")
        return None

def get_normal_response(messages, llm):
    """
    Gera resposta normal do chatbot (sem RAG)
    """
    try:
        # Converter mensagens para formato LangChain
        langchain_messages = []
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            else:
                langchain_messages.append(AIMessage(content=msg["content"]))

        # Se não há mensagens, usar a última mensagem do usuário
        if not langchain_messages:
            # Pegar a última mensagem do session_state
            last_message = st.session_state.messages[-1]
            if last_message["role"] == "user":
                langchain_messages = [HumanMessage(content=last_message["content"])]

        response = llm.invoke(langchain_messages)
        return response.content
        
    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"

def get_rag_response(question, vectorstore, llm):
    """
    Gera resposta usando RAG (com documentos)
    """
    try:
        from config.settings import RAG_CONFIG
        
        # Buscar documentos relevantes
        docs = vectorstore.similarity_search(
            question, 
            k=RAG_CONFIG["similarity_search_k"]
        )
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Criar prompt com contexto
        rag_prompt = f"""
        Contexto dos documentos:
        {context}
        
        Pergunta: {question}
        
        Com base apenas no contexto fornecido acima, responda à pergunta de forma clara e precisa. 
        Se a informação não estiver no contexto, diga que não encontrou a informação nos documentos.
        """
        
        response = llm.invoke([HumanMessage(content=rag_prompt)])
        return response.content
        
    except Exception as e:
        return f"Erro ao gerar resposta RAG: {str(e)}"
    
def get_boleto_identification_response(question, vectorstore, llm):
    """
    Identifica transmissora e empresa pagadora do boleto usando RAG + JSONs
    """
    try:
        # Buscar documentos relevantes do boleto
        docs = vectorstore.similarity_search(question, k=5)
        boleto_text = "\n\n".join([doc.page_content for doc in docs])
        
        # Identificar empresas usando os JSONs
        identification_result = identify_companies_from_boleto(boleto_text)
        
        # Criar resposta estruturada
        response_parts = []
        
        if identification_result['transmissora']:
            trans = identification_result['transmissora']
            response_parts.append(f"""
🏢 **TRANSMISSORA IDENTIFICADA:**
- Nome: {trans.get('nome')}
- CNPJ: {trans.get('codigo_fornecedor')}
- Código ONS: {trans.get('codigo_ons')}
- ID: {trans.get('id_transmissora')}
            """)
        
        if identification_result['empresa_pagadora']:
            emp = identification_result['empresa_pagadora']
            response_parts.append(f"""
💼 **EMPRESA PAGADORA IDENTIFICADA:**
- Nome: {emp.get('nome')}
- CNPJ: {emp.get('cnpj')}
- Categoria: {emp.get('categoria')}
- Código: {emp.get('codigo')}
- Código NeoEnergia: {emp.get('codigo_neoenergia')}
            """)
        
        if identification_result['cnpjs_encontrados']:
            cnpjs_list = ', '.join(identification_result['cnpjs_encontrados'])
            response_parts.append(f"""
🔍 **CNPJs ENCONTRADOS NO BOLETO:**
{cnpjs_list}
            """)
        
        if not identification_result['sucesso']:
            response_parts.append("""
⚠️ **Não foi possível identificar transmissora ou empresa pagadora.**
Verifique se os CNPJs do boleto estão cadastrados nos JSONs.
            """)
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"Erro na identificação do boleto: {str(e)}"