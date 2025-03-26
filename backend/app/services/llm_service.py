import re
from typing import List


from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_text_splitters import TextSplitter

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

class LLMService:
    def __init__(self, model_name = "deepseek-r1:8b"):
        self.answer_prompt = ChatPromptTemplate(answer_template)
        self.llm = OllamaLLM(model=model_name)
        
    def answer_question(self, question: str, documents: List[Document]) -> str:
        """Generate answer using retrieved documents"""
        context = "\n\n".join([doc.page_content for doc in documents])
        chain = self.answer_prompt | self.llm
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
        
        chain = summary_prompt | self.llm
        result = chain.invoke({"text": combined_text})
        clean_content, _ = self.clean_thinking(result)
        return clean_content
