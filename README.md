# PDF and Website Chatbot with Retrieval Augmented Generation (RAG)

This project aims to build a powerful chatbot capable of understanding and responding to information extracted from both PDF files and websites.  It leverages Retrieval Augmented Generation (RAG) to provide accurate and contextually relevant answers, addressing the limitations of traditional chatbot approaches.

## Current Issues & Motivation

Current chatbot solutions often struggle with:

* **Long Loading Times:** Processing large PDF files (especially text-heavy ones exceeding 1MB) can result in significant delays, hindering user experience.
* **Contextual Understanding:**  Accurately grasping the nuances and context within lengthy documents remains a challenge, leading to less precise and sometimes irrelevant responses.
* **Lack of Optimized Prompts:**  Without a well-defined prompt structure, chatbot outputs may lack clarity, focus, and overall quality.

This project directly tackles these issues by implementing a RAG-based approach.

## Proposed Solution

This project will deliver a web application with the following key features:

* **Web Scraper Retrieval with RAG:**  A robust web scraping mechanism combined with Retrieval Augmented Generation will enable the chatbot to access and process information from both uploaded PDF files and specified websites. This will ensure access to a broader range of data and improve the chatbot's ability to understand complex information.
* **Intuitive Streamlit Interface:** A user-friendly Streamlit web application will be developed, featuring a sidebar with clear options for users to select their data source: uploading a PDF file or providing a website URL. This streamlined approach will simplify the interaction process.
* **Prompt Recommendation Feature:**  To enhance the quality and relevance of chatbot responses, a prompt recommendation feature will be implemented. This will guide users in formulating effective queries and help the chatbot generate more focused and informative outputs.

## Technology Stack (Planned)

* **Python:** Core programming language.
* **Streamlit:** For building the web application.
* **LangChain/LlamaIndex:** For RAG implementation and PDF processing.
* **Beautiful Soup/Scrapy:** For web scraping.
* **(Other libraries as needed for vector databases, embeddings, etc.)**

## Documentation (Tentative)
**Version 0.1 (Initial Setup):**  Project initialization and basic structure.

**Version 0.2 (Model Completion & Deployment):**  Finished the core RAG model and deployed the application using Streamlit.
![Screenshot 2025-02-05 232033](https://github.com/user-attachments/assets/229171b3-31d5-4d7a-8ad0-893973f97e87)

**Version 0.3 (Feature Enhancement & Testing):** Added a success notification when data has been successfully indexed. Implemented a test RAG module for evaluating retrieval performance.  This allows for more rigorous testing and ensures the retrieval component is functioning correctly.
