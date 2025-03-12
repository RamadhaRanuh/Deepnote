import streamlit as st
import re
from pathlib import Path
from typing import List

import requests

from langchain_community.document_loaders import PDFPlumberLoader, SeleniumURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from nltk.tokenize import word_tokenize as word_tokenizer
from langchain.retrievers import EnsembleRetriever
import concurrent.futures

distilled_template = """
DOCUMENT:
{text}

TASK:
Distill this document into its key points and important information.
Remove any redundant information, formatting artifacts, and non-essential content.
Preserve specific terminology, definitions, and critical details.

OUTPUT FORMAT:
Return the distilled content in clear, concise text.
"""

answer_template = """
CONTEXT:
{context}

QUESTION:
{question}

INSTRUCTIONS:
1. Analyze if the context contains sufficient information to answer the question
2. If insufficient, respond with "Insufficient context to answer this question"
3. If sufficient, provide a concise answer using only facts from the context
4. Highlight any specific terminology or important definitions used

Response should be clear and direct, citing specific parts of the context.
"""

pdfs_directory = Path('./pdf/')
pdfs_directory.mkdir(exist_ok=True)



llm = OllamaLLM(model="deepseek-r1:8b")

class DocumentProcessor:
    def __init__(self):
        self.answer_prompt = ChatPromptTemplate.from_template(answer_template)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " "],
            add_start_index=True
        )
        self.vector_store = None    
        self.bm25_retriever_obj = None
        self.semantic_retriever_obj = None
        self.ensemble_retriever_obj = None

    def load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF and split into chunks"""
        loader = PDFPlumberLoader(file_path)
        documents = loader.load()
        split_docs = self.text_splitter.split_documents(documents)
        return split_docs

    def load_url(self, url: str) -> List[Document]:
        """Load content from a URL, extract text and create a Document"""
        loader = SeleniumURLLoader(urls=[url])
        documents = loader.load()
        fixed_docs = []
        for doc in documents:
            # Ensure page_content is a string
            text = doc.page_content
            if not isinstance(text, str):
                text = str(text)
            fixed_doc = Document(page_content=text, metadata={"source": url})
            fixed_docs.extend(self.text_splitter.split_documents([fixed_doc]))
        return fixed_docs

    def clean_text(self, text: str) -> str:
        """Enhanced text cleaning for PDF and URL content"""
        text = re.sub(r'^\s*Page \d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\x20-\x7E\u2022\u2013\u2014\u2018\u2019\u201C\u201D]', '', text)
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
        return text.strip()

    def process_pdf(self, file_path: str) -> List[Document]:
        """Complete PDF processing pipeline"""
        docs = self.load_pdf(file_path)
        processed_docs = []

        # Process documents in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            def process_doc(doc):
                cleaned_content = self.clean_text(doc.page_content)
                doc.page_content = cleaned_content
                if cleaned_content.strip():
                    return doc
                return None
            processed_docs = list(filter(None, executor.map(process_doc, docs)))

        # Process documents sequentially
        # for doc in docs:
        #   cleaned_content = self.clean_text(doc.page_content)
        #    doc.page_content = cleaned_content
        #    if cleaned_content.strip():
        #        processed_docs.append(doc)
        return processed_docs

    def process_url(self, url: str) -> List[Document]:
        """Complete URL processing pipeline"""
        docs = self.load_url(url)
        processed_docs = []
        for doc in docs:
            cleaned_content = self.clean_text(doc.page_content)
            doc.page_content = cleaned_content
            if cleaned_content.strip():
                processed_docs.append(doc)
        return processed_docs

    def semantic_retriever(self, documents: List[Document]):
        """Index processed documents in vector store"""
        embeddings = OllamaEmbeddings(model="deepseek-r1:8b")
        self.vector_store = InMemoryVectorStore(embeddings)
        self.vector_store.add_documents(documents)
        self.semantic_retriever_obj = self.vector_store.as_retriever(search_kwargs={"k":5})

        return self.semantic_retriever_obj
    
    def bm25_retriever(self, documents: List[Document]):
        self.bm25_retriever_obj = BM25Retriever.from_documents(documents, preprocess_func=word_tokenizer)
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
            return self.ensemble_retriever_obj.get_relevant_documents(query)
        else:
            return []
    
    def answer_question(self, question: str, documents: List[Document]) -> str:
        """Generate answer using retrieved documents"""
        context = "\n\n".join([doc.page_content for doc in documents])
        chain = self.answer_prompt | llm
        summary = chain.invoke({"question": question, "context": context})
        clean_content, thinking = self.clean_thinking(summary)
        return clean_content, thinking
    
    def clean_thinking(self, text: str) -> str:
        """Clean thinking process text"""

        thinking = ""
        thinking_match = re.search(r"<think>(.*?)</think>", text, flags=re.DOTALL)
        if thinking_match:
            thinking = thinking_match.group(1).strip()

        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip(), thinking

# Streamlit interface
def main():
    st.title("PDF/URL Question Answering System")
    
    st.sidebar.title("Article URL/File")
    input_type = st.sidebar.radio("Choose Input Type", ["URL", "PDF"])
    
    processor = DocumentProcessor()
    
    # Hold documents to index
    all_documents = []
    
    if input_type == "URL":
        urls = []
        for i in range(3):
            url = st.sidebar.text_input(f"Article URL {i+1}")
            if url:
                urls.append(url)
        if urls:
            for url in urls:
                with st.spinner(f"Processing URL: {url}"):
                    docs = processor.process_url(url)
                    all_documents.extend(docs)
                    st.sidebar.write(f"URL indexed: {url}")
    elif input_type == "PDF":
        uploaded_files = st.sidebar.file_uploader("Upload File (PDF)", type=["pdf"], accept_multiple_files=True)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_path = pdfs_directory / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    docs = processor.process_pdf(str(file_path))
                    all_documents.extend(docs)
                    st.sidebar.write(f"File indexed: {uploaded_file.name}")
    
    # Index all collective documents if any
    if all_documents:
        processor.semantic_retriever(all_documents)
        processor.bm25_retriever(all_documents)
        processor.create_hybrid_retriever(semantic_weight=0.5, bm25_weight=0.5)
        st.success("All documents processed and indexed!")
        
    
    # Question answering interface
    question = st.chat_input("Ask a question about the documents")
    if question:
        st.chat_message("user").write(question)
        with st.spinner("Searching and analyzing..."):
            relevant_docs = processor.retrieve_relevant_docs(question)
            answer, thinking = processor.answer_question(question, relevant_docs)
            st.chat_message("assistant").write(answer)

            # Collapsible section for thinking process
            if thinking:
                with st.expander("View thinking process"):
                    st.markdown(thinking)

            # Collapsible section for thinking process
            with st.expander("View Retrieved Documents", expanded=False):
                st.markdown("### Retrieved Documents")
                for i, doc in enumerate(relevant_docs, 1):
                    st.markdown(f"**Document {i}**")
                    st.text(doc.page_content)
                    st.markdown(f"*Source: {doc.metadata.get('source', 'Not specified')}*")
                    st.markdown("---")

if __name__ == "__main__":
    main()