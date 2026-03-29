from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

_embeddings = None
_reranker = None
_vectorstores: dict = {}
_chunk_counts: dict = {}

# RAG (Retrieval-Augmented Generation) implementation for retrieving relevant document chunks based on user queries and providing them as context to the language model during response generation
def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"batch_size": 8}
        )
    return _embeddings

# Reranker for scoring the relevance of retrieved document chunks to the user query, used to rank the chunks before providing them as context to the language model
def _get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = HuggingFaceCrossEncoder(
            model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
            model_kwargs={"device": "cpu"}
        )
    return _reranker

def build_vectorstore(chat_id: str, document_text: str):
    embeddings = _get_embeddings()

    # Delete existing vectorstore for the chat_id if it exists to avoid stale data and manage memory
    if chat_id in _vectorstores:
        try:
            _vectorstores[chat_id].delete_collection()
        except Exception:
            pass
        del _vectorstores[chat_id]

    # Semantic chunking of the document text to create smaller, semantically meaningful pieces for better retrieval performance in the RAG system
    splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=0.5
    )
    chunks = splitter.split_text(document_text)
    _chunk_counts[chat_id] = len(chunks)

    # Create a new Chroma vectorstore for the chat_id with the extracted chunks and their embeddings for later retrieval during chat interactions
    _vectorstores[chat_id] = Chroma.from_texts(
        chunks,
        embeddings,
        collection_name=f"chat_{chat_id.replace('-', '_')}"
    )
    #print(f"[DEBUG] chat_id={chat_id} → {len(chunks)} chunks, collection=chat_{chat_id}")

def get_chunk_count(chat_id: str) -> int:
    return _chunk_counts.get(chat_id, 100)

def get_relevant_context(chat_id: str, question: str, k: int = 5) -> str:
    if chat_id not in _vectorstores:
        raise ValueError(f"Vectorstore not found for chat_id={chat_id}")
    try:
        ret_k = k * 2
        retriever = _vectorstores[chat_id].as_retriever(search_kwargs={"k": ret_k})
        docs = retriever.invoke(question)
        pairs = [(question, doc.page_content) for doc in docs]
        scores = _get_reranker().score(pairs)
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return "\n\n".join(doc.page_content for doc, _ in ranked[:k])
    except Exception as e:
        print(f"RAG Error: {e}")
        return ""

def delete_vectorstore(chat_id: str):
    if chat_id in _vectorstores:
        try:
            _vectorstores[chat_id].delete_collection()
        except Exception:
            pass
        del _vectorstores[chat_id]
        print(f"[RAG] chat_id={chat_id} → vectorstore deleted")