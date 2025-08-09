import streamlit as st
from config.settings import PAGE_CONFIG
from components.sidebar import render_sidebar, render_status_info
from models.chat_model import init_model, get_normal_response, get_rag_response, get_boleto_identification_response

# Configurar página
st.set_page_config(**PAGE_CONFIG)

# Título principal
st.title("🤖 Chatbot com RAG")
st.markdown("Chat inteligente com suporte a documentos usando Retrieval-Augmented Generation")

# Inicializar session states
if "messages" not in st.session_state:
    st.session_state.messages = []

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "documents_processed" not in st.session_state:
    st.session_state.documents_processed = False

# Renderizar barra lateral e obter API key
api_key = render_sidebar()

# Salvar API key no session state
if api_key:
    st.session_state.api_key = api_key

# Verificar status e mostrar informações
if not render_status_info():
    st.stop()

# Inicializar modelo
llm = init_model(api_key)

if not llm:
    st.error("❌ Não foi possível inicializar o modelo. Verifique sua API Key.")
    st.stop()

# Container do chat
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

# Input do usuário
if prompt := st.chat_input("Digite sua mensagem aqui..."):
    
    # Adicionar mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)

    # Gerar resposta
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                # Verificar se deve usar RAG ou chat normal
                if (st.session_state.get('documents_processed', False) and 
                    st.session_state.get('vectorstore') is not None):
                    
                    # Detectar se é uma pergunta sobre identificação de empresas
                    palavras_identificacao = [
                        'transmissora', 'empresa', 'pagador', 'cnpj', 'identificar', 
                        'quem', 'qual empresa', 'qual transmissora', 'de-para', 
                        'codigo ons', 'beneficiario', 'codigo fornecedor'
                    ]
                    
                    pergunta_lower = prompt.lower()
                    is_identification_query = any(palavra in pergunta_lower for palavra in palavras_identificacao)
                    
                    if is_identification_query:
                        # Usar identificação de empresas
                        assistant_response = get_boleto_identification_response(
                            prompt, 
                            st.session_state.vectorstore, 
                            llm
                        )
                    else:
                        # Usar RAG normal
                        assistant_response = get_rag_response(
                            prompt, 
                            st.session_state.vectorstore, 
                            llm
                        )
                else:
                    # Chat normal
                    assistant_response = get_normal_response(
                        st.session_state.messages,
                        llm
                    )

                st.write(assistant_response)

                # Adicionar resposta ao histórico
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": assistant_response
                })
                
            except Exception as e:
                st.error(f"Erro ao gerar resposta: {str(e)}")