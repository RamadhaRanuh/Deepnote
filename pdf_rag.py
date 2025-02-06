import streamlit as st
import re
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_core.documents import Document


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

embeddings = OllamaEmbeddings(model = "deepseek-r1:8b")
vector_store = InMemoryVectorStore(embeddings)


llm = OllamaLLM(model = "deepseek-r1:8b")

class PDFProcessor:
    def __init__(self):
        self.answer_prompt = ChatPromptTemplate.from_template(answer_template)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", "!", "?", ",", " "],
            add_start_index=True
        )

    def load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF and split into chunks"""
        # Load PDF
        loader = PDFPlumberLoader(file_path)
        documents = loader.load()
        
        # Split documents
        split_docs = self.text_splitter.split_documents(documents)
        return split_docs
    
    def clean_text(self, text: str) -> str:
        """Enhanced PDF-specific text cleaning"""
        # Remove headers and footers (common in PDFs)
        text = re.sub(r'^\s*Page \d+\s*$', '', text, flags=re.MULTILINE)
        
        # Fix hyphenation at line breaks
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # Remove multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove non-ASCII characters while preserving useful unicode
        text = re.sub(r'[^\x20-\x7E\u2022\u2013\u2014\u2018\u2019\u201C\u201D]', '', text)
        
        # Remove redundant spaces around punctuation
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        
        # Fix common PDF artifacts
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Add space between merged words
        
        return text.strip()
    
    def process_pdf(self, file_path: str) -> List[Document]:
        """Complete PDF processing pipeline"""
        # Load PDF
        docs = self.load_pdf(file_path)
        
        # Clean each document
        processed_docs = []
        for doc in docs:
            cleaned_content = self.clean_text(doc.page_content)
            doc.page_content = cleaned_content
            if cleaned_content.strip():  # Only keep non-empty chunks
                processed_docs.append(doc)
        
        return processed_docs

    def index_documents(self, documents: List[Document]):
        """Index processed documents in vector store"""
        vector_store.add_documents(documents)
    
    def retrieve_relevant_docs(self, query: str, k: int = 3) -> List[Document]:
        """Retrieve relevant documents with similarity threshold"""
        docs = vector_store.similarity_search(query, k=k)
        return docs
    
    def answer_question(self, question: str, documents: List[Document]) -> str:
        """Generate answer using retrieved documents"""
        context = "\n\n".join([doc.page_content for doc in documents])
        chain = self.answer_prompt | llm
        return chain.invoke({"question": question, "context": context})

# Streamlit interface
def main():
    st.title("PDF Question Answering System")
    
    processor = PDFProcessor()
    
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        accept_multiple_files=False
    )
    
    if uploaded_file:
        # Save uploaded file
        file_path = pdfs_directory / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # Process PDF
        with st.spinner("Processing PDF..."):
            processed_docs = processor.process_pdf(str(file_path))
            processor.index_documents(processed_docs)
            st.success("PDF processed and indexed!")
    
        # Question answering interface
        question = st.chat_input("Ask a question about the PDF")
        if question:
            st.chat_message("user").write(question)
            
            # Retrieve and answer
            with st.spinner("Searching and analyzing..."):
                relevant_docs = processor.retrieve_relevant_docs(question)
                answer = processor.answer_question(question, relevant_docs)
                st.chat_message("assistant").write(answer)

if __name__ == "__main__":
    main()