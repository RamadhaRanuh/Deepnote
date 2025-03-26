import concurrent.futures
import re
import requests
import logging
from typing import List

from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

from langchain_community.document_loaders import PDFPlumberLoader, SeleniumURLLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " "]
        )

    def load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF and split into chunks"""
        try:
            loader = PDFPlumberLoader(file_path)
            documents = loader.load()
            split_docs = self.text_splitter.split_documents(documents)
            return split_docs
        except Exception as e:
            logger.error(f"Error loading PDF: {str(e)}")
            return []
    
    def load_url(self, url: str) -> List[Document]:
        """Load content from a URL, extract text and create a Document"""
        try:
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
        except Exception as e:
            logger.error(f"Error loading URL: {str(e)}")
    
    def load_youtube(self, url: str) -> List[Document]:
        """Load content from a YouTube video, extract transcript and create a Document"""

        try:
            video_id_match = re.search(r'?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
            if not video_id_match:
                return []
            video_id = video_id_match.group(1)
            title = self.get_youtube_title(url, video_id)

            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            if not transcript_list:
                logger.error(f"No transcript found for video {video_id}")
                return []
            full_transcript = " ".join([entry["text"] for entry in transcript_list])

            doc = Document(
                page_content = full_transcript,
                metadata = {
                    "source": url,
                    "title": title,
                    "type": "youtube_transcript"
                }
            )

            split_docs = self.text_splitter.split_documents([doc])
            return split_docs
        except Exception as e:
            logger.error(f"Error loading YouTube video: {str(e)}")
            return []
        
    def get_youtube_title(self, url: str, video_id: str) -> str:
        """Get YouTube video title using multiple fallback methods"""
        
        # Method 1: Try using pytube
        try:
            yt = YouTube(url)
            return yt.title
        except Exception:
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
    
    def process_documents(self, documents: str, type: str) -> List[Document]:
        """Process documents based on their type"""
        docs = []
        processed_docs = []

        try:
            match type:
                case ("pdf"):
                    docs = self.load_pdf(documents)
                case ("url"):
                    docs = self.load_url(documents)
                case ("youtube"):
                    docs = self.load_youtube(documents) 
                case _:
                    docs = []

            with concurrent.futures.ThreadPoolExecutor() as executor:
                def process_doc(doc):
                    cleaned_content = self.clean_text(doc.page_content)
                    doc.page_content = cleaned_content
                    if cleaned_content.strip():
                        return doc
                    return None
                processed_docs = list(filter(None, executor.map(process_doc, docs)))

            return processed_docs
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return []


        

    
