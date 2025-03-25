Current State (MERN STACK):
![Screenshot 2025-03-24 175234](https://github.com/user-attachments/assets/7bd67c31-a54b-458b-9771-3bc4829b7eeb)
![Screenshot 2025-03-24 175318](https://github.com/user-attachments/assets/16c6ba6c-4e28-4dcb-bba9-e194eef5e3e2)

# PDF and Website Chatbot with Retrieval Augmented Generation (RAG)

This project aims to build a powerful chatbot capable of understanding and responding to information extracted from PDF files and websites.  It leverages Retrieval Augmented Generation (RAG) to provide accurate and contextually relevant answers, addressing the limitations of traditional chatbot approaches.

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

**Version 0.4 (Combined Retrieval & Web Testing):** Combined Web and PDF retrieval into a unified system. Added a dedicated Web Retrieval Testing File to specifically test and refine the web retrieval component, ensuring its accuracy and efficiency.
![Screenshot 2025-02-06 182859](https://github.com/user-attachments/assets/432fce7a-4250-4333-87c0-f4510f162fe6)
![Screenshot 2025-02-06 183434](https://github.com/user-attachments/assets/46f00a60-af41-43aa-b4aa-55e4fd8db88e)

**Version 0.5 (Add Summary, Youtube Retrieval, Change retrieval to Hybrid for more accurate retrieval)**:  Implement a feature to generate and display a summary of retrieved content automatically, integrate a YouTube data retrieval function using the YouTube API to gather and analyze comments or video data, and Improve the retrieval system by combining keyword-based and semantic search to enhance the accuracy of retrieved information.
![Screenshot 2025-03-12 220056](https://github.com/user-attachments/assets/b4a06024-f043-4a2f-b8b1-f0181cad3f4c)

**Version 1.0 (Create Dashboard & Notebook Chatbot from Scratch using MERN + Python Stack):** Build a user-friendly dashboard using React to display data and insights, and develop a chatbot using Python to handle user queries, summarize data, and provide recommendations directly from the notebook.
<div style="display: flex; justify-content: center; gap: 10px;">
    <img src="https://github.com/user-attachments/assets/7bd67c31-a54b-458b-9771-3bc4829b7eeb" alt="Screenshot 1" width="45%" />
    <img src="https://github.com/user-attachments/assets/16c6ba6c-4e28-4dcb-bba9-e194eef5e3e2" alt="Screenshot 2" width="45%" />
</div>

**Version 1.0.1 (Create UI & Dark Mode Feature)**: Build a user-friendly dashboard and implement darkmode
<div style="display: flex; justify-content: center; gap: 10px;">
    <img src="https://github.com/user-attachments/assets/d38dcdb7-3555-4dfc-8c15-2a0fc914c487" alt="Screenshot 1" style="max-width: 45%; height: auto;" />
    <img src="https://github.com/user-attachments/assets/daefe674-fe9b-448c-8871-b146e451ebb3" alt="Screenshot 2" style="max-width: 45%; height: auto;" />
</div>

<div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px;">
    <img src="https://github.com/user-attachments/assets/001684b8-f7cb-4865-938b-3216055486df" alt="Screenshot 3" style="max-width: 45%; height: auto;" />
    <img src="https://github.com/user-attachments/assets/d6f845ec-415e-4c4a-bbf8-f53969df2e9a" alt="Screenshot 4" style="max-width: 45%; height: auto;" />
</div>










