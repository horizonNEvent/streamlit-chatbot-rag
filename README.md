# Streamlit Chatbot with RAG

Um chatbot inteligente construído com Streamlit que utiliza Retrieval-Augmented Generation (RAG) para responder perguntas baseadas em documentos carregados.

## ✨ Funcionalidades

- **Chat Normal**: Conversação padrão com IA
- **RAG (Retrieval-Augmented Generation)**: Respostas baseadas em documentos carregados
- **Identificação de Empresas**: Sistema especializado para identificar transmissoras e empresas
- **Interface Amigável**: Interface moderna construída com Streamlit
- **Upload de Documentos**: Suporte para PDFs e documentos de texto

## 🚀 Tecnologias Utilizadas

- **Streamlit** - Interface web
- **LangChain** - Framework para LLM
- **Python** - Linguagem principal
- **Vector Store** - Armazenamento de embeddings

## 📋 Pré-requisitos

- Python 3.8+
- API Key de provedor de LLM (OpenAI, Google, etc.)

## 🛠️ Instalação

1. Clone o repositório:
```bash
git clone https://github.com/horizonNEvent/streamlit-chatbot-rag.git
cd streamlit-chatbot-rag
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
streamlit run app.py
```

## 📁 Estrutura do Projeto

```
streamlit-chatbot-rag/
├── app.py                 # Aplicação principal
├── config/
│   └── settings.py        # Configurações
├── components/
│   └── sidebar.py         # Componentes da interface
├── models/
│   └── chat_model.py      # Modelos de chat
├── requirements.txt       # Dependências
├── README.md             # Este arquivo
└── .gitignore           # Arquivos ignorados pelo Git
```

## 🎯 Como Usar

1. Insira sua API Key na barra lateral
2. (Opcional) Faça upload de documentos para usar o RAG
3. Digite suas perguntas no chat
4. O sistema automaticamente detecta se deve usar RAG ou chat normal

## 🔧 Configuração

Configure suas variáveis de ambiente ou insira a API Key diretamente na interface.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request


