from nltk.tokenize import word_tokenize as word_tokenizer
from typing import List

from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain.retrievers import EnsembleRetriever


class Retriever:
    def __init__(self, model_name="deepseek-r1:8b"):
        self.embeddings = OllamaEmbeddings(model=model_name)
        self.vector_store = None
        self.bm25_retriever_obj = None
        self.semantic_retriever_obj = None
        self.ensemble_retriever_obj = None

    def semantic_retriever(self, documents: List[Document]):
        """Index Processed Documents in Vector Store"""
        self.vector_store = InMemoryVectorStore(self.embeddings)
        self.vector_store.add_documents(documents)
        self.semantic_retriever_obj = self.vector_store.as_retriever(search_kwargs={"k": 5})

        return self.semantic_retriever_obj
    
    def bm25_retriever(self, documents: List[Document]):
        self.bm25_retriever_obj = BM25Retriever.from_documents(documents, preprocess_func = word_tokenizer)
        return self.bm25_retriever_obj
    
    def create_hybrid_retriever(self, semantic_weight=0.5, bm25_weight=0.5):
        if self.vector_store is None or self.bm25_retriever_obj is None:
            return None
        
        self.ensemble_retriever_obj = EnsembleRetriever(
            retrievers=[self.semantic_retriever_obj, self.bm25_retriever_obj],
            weight=[semantic_weight, bm25_weight]
        )
        return self.ensemble_retriever_obj
    
    
    def retrieve_relevant_docs(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve relevant documents with similarity search"""
        if self.ensemble_retriever_obj:
            return self.enesmble_retriever_obj.get_relevant_documents(query)
        else:
            return []
        