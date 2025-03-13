import streamlit as st
import re
from pathlib import Path
from typing import List

import requests

from nltk.tokenize import word_tokenize as word_tokenizer
import concurrent.futures

from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

from langchain_community.document_loaders import PDFPlumberLoader, SeleniumURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever



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
    
    def load_youtube(self, url: str) -> List[Document]:
        """Load content from a YouTube video, extract transcript and create a Document"""

        try:
            video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
            if not video_id_match:
                return []
            video_id = video_id_match.group(1)
            title = self.get_youtube_title(url, video_id)

            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_transcript = " ".join([entry["text"] for entry in transcript_list])

            doc = Document(
                page_content = full_transcript,
                metadata={
                    "source": url,
                    "title": title,
                    "type": "youtube_transcript"
                }
            )

            split_docs = self.text_splitter.split_documents([doc])
            return split_docs
        except Exception as e:
            st.error(f"Error loading YouTube video: {str(e)}")
            return []
        
    def get_youtube_title(self, url: str, video_id: str) -> str:
        """Get YouTube video title using multiple fallback methods"""
        
        # Method 1: Try using pytube
        try:
            yt = YouTube(url)
            return yt.title
        except Exception:
            pass
        
        # Method 2: Use requests to get page metadata
        try:
            response = requests.get(f"https://www.youtube.com/watch?v={video_id}")
            if response.status_code == 200:
                title_match = re.search(r'<title>(.*?)</title>', response.text)
                if title_match:
                    title = title_match.group(1)
                    # Clean up title (remove " - YouTube" suffix)
                    title = re.sub(r'\s*-\s*YouTube\s*$', '', title)
                    return title
        except Exception:
            pass
        
        # Fallback: Use video ID as title
        return f"YouTube Video {video_id}"

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
    
    def process_youtube(self, url: str) -> List[Document]:
        """Complete YouTube processing pipeline"""
        docs = self.load_youtube(url)
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
        text = re.sub(r"</?think>", "", text, flags=re.DOTALL)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip(), thinking
    

        # Add this method to the DocumentProcessor class
    def generate_summary(self, documents: List[Document]) -> str:
        """Generate a summary of the documents"""
        if not documents:
            return "No content to summarize."
        
        # Combine all document content, but limit to avoid token limits
        combined_text = " ".join([doc.page_content for doc in documents])
        # Limit to approximately 4000 chars to avoid token limits
        if len(combined_text) > 4000:
            combined_text = combined_text[:4000] + "..."
        
        summary_prompt = ChatPromptTemplate.from_template("""
        <think>
        You're tasked with summarizing the following content. First, identify the main topic, key points, 
        and important information. Focus on factual content and core concepts.
        </think>
        
        CONTENT:
        {text}
        
        TASK:
        Create a concise summary (3-5 sentences) of the above content that captures:
        - The main subject/topic
        - Key points and findings
        - Important concepts or conclusions
        
        Make the summary informative yet brief.
        """)
        
        chain = summary_prompt | llm
        result = chain.invoke({"text": combined_text})
        clean_content, _ = self.clean_thinking(result)
        return clean_content

# Streamlit interface
def main():

    st.title("RAG Question Answering System")
    
    st.sidebar.title("Content Source")
    input_type = st.sidebar.radio("Choose Input Type", ["URL", "PDF", "Youtube"])

    if 'all_documents' not in st.session_state:
        st.session_state.all_documents = []

    if 'content_summaries' not in st.session_state:
        st.session_state.content_summarises = []
    
    if 'indexed' not in st.session_state:
        st.session_state.indexed = False

    if 'last_input_type' not in st.session_state or st.session_state.last_input_type != input_type:
        st.session_state.all_documents = []
        st.session_state.content_summaries = []
        st.session_state.indexed = False
        st.session_state.last_input_type = input_type

    processor = DocumentProcessor()

    
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
                    st.session_state.all_documents.extend(docs)
                    st.sidebar.write(f"URL indexed: {url}")

                    # Generate summary for URL
                    with st.spinner(f"Generating summary for {url}..."):
                        summary = processor.generate_summary(docs)
                        st.session_state.content_summaries.append({"type": "URL", "source": url, "summary": summary})


    elif input_type == "PDF":
        uploaded_files = st.sidebar.file_uploader("Upload File (PDF)", type=["pdf"], accept_multiple_files=True)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_path = pdfs_directory / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    docs = processor.process_pdf(str(file_path))
                    st.session_state.all_documents.extend(docs)
                    st.sidebar.write(f"File indexed: {uploaded_file.name}")

                    # Generate summary for URL
                    with st.spinner(f"Generating summary for {uploaded_file.name}..."):
                        summary = processor.generate_summary(docs)
                        st.session_state.content_summaries.append({"type": "PDF", "source": uploaded_file.name, "summary": summary})

    elif input_type == "Youtube":
        youtube_urls = []
        for i in range(3):
            youtube_url = st.sidebar.text_input(f"Youtube URL {i+1}")
            if youtube_url:
                youtube_urls.append(youtube_url)

        if youtube_urls:
            for youtube_url in youtube_urls:
                with st.spinner(f"Processing Youtube video: {youtube_url}"):
                    docs = processor.process_youtube(youtube_url)
                    st.session_state.all_documents.extend(docs)
                    st.sidebar.write(f"Youtube video indexed: {youtube_url}")

                    # Generate summary for Youtube Video
                    with st.spinner(f"Generating summary for {youtube_url}..."):
                        summary = processor.generate_summary(docs)
                        st.session_state.content_summaries.append({"type": "URL", "source": youtube_url, "summary": summary})
    
    # Index all collective documents if any

    if st.session_state.all_documents:
        processor.semantic_retriever(st.session_state.all_documents)
        processor.bm25_retriever(st.session_state.all_documents)
        processor.create_hybrid_retriever(semantic_weight=0.5, bm25_weight=0.5)
        st.success("All documents processed and indexed!")
        
        if st.session_state.content_summaries:
            for item in st.session_state.content_summaries:
                if item["type"] == "YouTube":
                    st.markdown(f"**{item['title']}** (YouTube)")
                else:
                    st.markdown(f"**{item['source']}** ({item['type']})")
                st.markdown(item["summary"])
                st.markdown("---")
    
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
                    source = doc.metadata.get('source', 'Not specified')
                    doc_type = doc.metadata.get('type', '')

                    if doc_type == 'youtube_transcript':
                        video_title = doc.metadata.get('title', 'Youtube Video')
                        st.markdown(f"*Source: [{video_title}]({source}) (Youtube Transcript*")
                    else:
                        st.markdown(f"*Source: {source}*")
                    st.markdown("---")

if __name__ == "__main__":
    main()

