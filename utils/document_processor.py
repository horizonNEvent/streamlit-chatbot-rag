import streamlit as st
import PyPDF2
import asyncio
import nest_asyncio
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config.settings import RAG_CONFIG, SUPPORTED_FILE_TYPES

def extract_text_from_file(uploaded_file):
    """
    Extrai texto de diferentes tipos de arquivo
    """
    text = ""
    
    try:
        if uploaded_file.type == "application/pdf":
            # PDF
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        
        elif uploaded_file.type == "text/plain":
            # TXT
            text = str(uploaded_file.read(), "utf-8")
        
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # DOCX
            doc = Document(uploaded_file)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        
        return text
    
    except Exception as e:
        st.error(f"Erro ao extrair texto do arquivo {uploaded_file.name}: {str(e)}")
        return ""

def split_text_into_chunks(text):
    """
    Divide texto em chunks menores
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=RAG_CONFIG["chunk_size"],
        chunk_overlap=RAG_CONFIG["chunk_overlap"],
        length_function=len
    )
    
    chunks = text_splitter.split_text(text)
    return chunks

def create_vectorstore(chunks, api_key):
    """
    Cria vectorstore com os chunks de texto
    """
    try:
        # Configurar loop de eventos para resolver o erro de threading
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
        
        nest_asyncio.apply(loop)
        
        # Criar embeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        
        # Criar vectorstore
        vectorstore = FAISS.from_texts(chunks, embeddings)
        return vectorstore
        
    except Exception as e:
        st.error(f"Erro ao criar vectorstore: {str(e)}")
        return None

def process_uploaded_files(uploaded_files, api_key):
    """
    Processa todos os arquivos uploadados
    """
    if not uploaded_files or not api_key:
        st.warning("⚠️ Arquivos ou API Key não fornecidos!")
        return None
    
    try:
        with st.spinner("Processando documentos..."):
            # Extrair texto de todos os arquivos
            all_text = ""
            processed_files = []
            
            for uploaded_file in uploaded_files:
                st.info(f"📄 Processando: {uploaded_file.name}")
                text = extract_text_from_file(uploaded_file)
                if text:
                    all_text += f"\n\n--- {uploaded_file.name} ---\n\n" + text
                    processed_files.append(uploaded_file.name)
                else:
                    st.warning(f"⚠️ Não foi possível extrair texto de: {uploaded_file.name}")
            
            if not all_text:
                st.error("❌ Nenhum texto foi extraído dos arquivos.")
                return None
            
            # Dividir em chunks
            st.info("🔪 Dividindo texto em chunks...")
            chunks = split_text_into_chunks(all_text)
            
            # Criar vectorstore
            st.info("🔧 Criando vectorstore...")
            vectorstore = create_vectorstore(chunks, api_key)
            
            if vectorstore:
                st.success(f"✅ {len(processed_files)} arquivo(s) processado(s):")
                for filename in processed_files:
                    st.success(f"📄 {filename}")
                st.info(f"📊 Criados {len(chunks)} chunks de texto")
                
                return vectorstore
            else:
                st.error("❌ Erro ao criar vectorstore")
                return None
                
    except Exception as e:
        st.error(f"❌ Erro ao processar documentos: {str(e)}")
        return None