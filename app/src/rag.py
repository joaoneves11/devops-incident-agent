"""
RAG (Retrieval-Augmented Generation) para runbooks e documentação de incidentes.

Implementação com LangChain:
- DirectoryLoader: carrega arquivos .md da pasta docs/
- RecursiveCharacterTextSplitter: chunking com overlap para não perder contexto entre chunks
- OpenAIEmbeddings: vetorização semântica dos chunks
- FAISS: vector store local (sem infra externa)
- similarity_search: recupera os top_k chunks mais relevantes para a query
"""
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

# Tamanho do chunk e overlap calibrados para runbooks em Markdown:
# - 600 tokens captura uma seção inteira (ex.: "O que investigar primeiro")
# - 80 de overlap evita perda de contexto na fronteira entre chunks
CHUNK_SIZE = 600
CHUNK_OVERLAP = 80

# Singleton do vector store — construído uma vez e reutilizado
_vectorstore: FAISS | None = None


def _build_vectorstore() -> FAISS:
   
    # DirectoryLoader com TextLoader para .md (preserva texto limpo)
    loader = DirectoryLoader(
        str(DOCS_DIR),
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=False,
    )
    docs = loader.load()

    if not docs:
        raise FileNotFoundError(
            f"Nenhum runbook encontrado em {DOCS_DIR}. "
            "Adicione arquivos .md para que o RAG funcione."
        )

    # Chunking recursivo: tenta dividir por \n\n, \n, " " nessa ordem
    # Mantém seções semânticas juntas o máximo possível
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    return FAISS.from_documents(chunks, embeddings)


def _get_vectorstore() -> FAISS:
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = _build_vectorstore()
    return _vectorstore


def retrieve(query: str, top_k: int = 3) -> list[tuple[str, str]]:
   
    vs = _get_vectorstore()
    results = vs.similarity_search(query, k=top_k)

    chunks = []
    for doc in results:
        # metadata["source"] contém o caminho completo; extraímos só o nome do arquivo
        source = Path(doc.metadata.get("source", "runbook")).stem
        chunks.append((source, doc.page_content))

    return chunks


def reload_vectorstore() -> None:
  
    global _vectorstore
    _vectorstore = None
    _get_vectorstore()
