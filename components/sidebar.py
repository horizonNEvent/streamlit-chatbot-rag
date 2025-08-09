"""
Componentes da barra lateral
"""
import streamlit as st
from config.settings import SUPPORTED_FILE_TYPES, URLS
from utils.document_processor import process_uploaded_files

def render_sidebar():
    """
    Renderiza toda a barra lateral
    """
    api_key = None
    
    with st.sidebar:
        # Seção de configurações
        api_key = render_config_section()  # ← Capturar o retorno
        
        # Separador
        st.markdown("---")
        
        # Seção de upload de documentos
        render_document_section()
        
        # Separador
        st.markdown("---")
        
        # Seção de instruções
        render_instructions_section()
        
        # Separador
        st.markdown("---")
        
        # Seção de links úteis
        render_links_section()
    
    return api_key

def render_config_section():
    """
    Seção de configurações (API Key e botão limpar)
    """
    st.header("⚙️ Configurações")

    # Input da API Key
    api_key = st.text_input(
        "Google API Key",
        type="password",
        help="Cole aqui a sua chave de API do Google AI Studio"
    )

    # Botão para limpar conversa
    if st.button("🗑️ Limpar Conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.documents_processed = False
        st.session_state.vectorstore = None
        st.rerun()
    
    return api_key

def render_document_section():
    """
    Seção de upload e processamento de documentos
    """
    st.header("📁 Upload de Documentos")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Escolha seus arquivos",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        help=f"Suporte para: {', '.join(SUPPORTED_FILE_TYPES).upper()}"
    )
    
    # Mostrar arquivos selecionados
    if uploaded_files:
        st.write("**Arquivos selecionados:**")
        for file in uploaded_files:
            st.write(f"📄 {file.name} ({file.size} bytes)")
    
    # Botão para processar documentos
    col1, col2 = st.columns(2)
    
    with col1:
        process_button = st.button("🚀 Processar", use_container_width=True)
    
    with col2:
        clear_docs_button = st.button("🗑️ Limpar Docs", use_container_width=True)
    
    # Lógica dos botões
    if process_button:
        api_key = st.session_state.get('api_key')
        if uploaded_files and api_key:
            vectorstore = process_uploaded_files(uploaded_files, api_key)
            if vectorstore:
                st.session_state.vectorstore = vectorstore
                st.session_state.documents_processed = True
        else:
            st.warning("⚠️ Adicione documentos e API Key primeiro!")
    
    if clear_docs_button:
        st.session_state.documents_processed = False
        st.session_state.vectorstore = None
        st.success("✅ Documentos removidos!")
    
    return uploaded_files

def render_instructions_section():
    """
    Seção de instruções de uso
    """
    st.header("📖 Como utilizar")
    
    st.markdown("""
    **Modo Normal:**
    1. Insira sua API Key do Google
    2. Digite sua pergunta no chat
    3. Pressione Enter para enviar
    
    **Modo RAG (com documentos):**
    1. Insira sua API Key do Google  
    2. Faça upload de documentos
    3. Clique em "🚀 Processar"
    4. Faça perguntas sobre os documentos
    """)

def render_links_section():
    """
    Seção de links úteis
    """
    st.header("🔗 Links Úteis")
    
    st.markdown(f"""
    - [📋 Obter API Key]({URLS["api_key"]})
    - [📚 Documentação Gemini](https://ai.google.dev/)
    - [🤖 LangChain Docs](https://docs.langchain.com/)
    """)

def render_status_info():
    """
    Mostra informações de status na parte principal
    """
    # Status da API Key
    api_key = st.session_state.get('api_key')
    if not api_key:
        st.warning("⚠️ Insira sua API Key do Google na barra lateral.")
        return False
    
    # Status dos documentos
    if st.session_state.get('documents_processed', False):
        st.success("📚 Documentos carregados! Você pode fazer perguntas sobre eles.")
    else:
        st.info("💡 Faça upload de documentos na barra lateral para usar RAG, ou converse normalmente.")
    
    return True