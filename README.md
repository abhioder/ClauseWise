ClauseWise ⚖️🤖
AI-Powered Legal Document Analyzer

📌 Description
ClauseWise is an AI-powered legal document analysis platform designed to simplify, decode, and classify complex legal texts for lawyers, businesses, and laypersons alike.
Legal documents such as contracts, NDAs, and agreements often require intensive manual reading and legal expertise to understand obligations, clauses, and document intent. ClauseWise automates this process using cutting-edge generative AI, enabling users to quickly extract insights, understand clauses in plain language, and identify document types efficiently.
 
🎯 Problem Statement
Understanding legal contracts is:
Time-consuming
Error-prone
Dependent on legal expertise
ClauseWise solves this by automating clause analysis and interpretation, making legal documents more accessible and easier to understand.

🚀 Expected Solutions & Features
1️⃣ Clause Simplification
Automatically rewrites complex legal clauses into simple, layman-friendly language.
Helps non-legal users understand obligations and rights clearly.

2️⃣ Named Entity Recognition (NER)
Extracts key legal entities such as:
Parties involved
Dates
Obligations
Monetary values
Legal terms

3️⃣ Clause Extraction & Breakdown
Detects and segments individual clauses from lengthy legal documents.
Enables focused clause-level analysis instead of reading entire docuents.

4️⃣ Document Type Classification
Automatically classifies legal documents into categories such as:
NDA
Lease Agreement
Employment Contract
Service Agreement

5️⃣ Multi-Format Document Support
Supports document uploads in:
PDF
DOCX
TXT

6️⃣ User-Friendly Interface
Interactive frontend built using:
Streamlit
Gradio
Designed for ease of use and quick interaction.

🛠️ Technologies & Tools
Programming Language
Python
AI & NLP
IBM Watson
Granite Models
HuggingFace
Frontend
Streamlit
Gradio

📁 Project Structure
ClauseWise/
│
├── backend/        # AI models, NLP processing, logic
├── frontend/       # Streamlit / Gradio interface
├── requirements.txt
└── README.md

⚙️ Installation & Setup (Basic)
git clone https://github.com/abhioder/ClauseWise.git
cd ClauseWise
pip install -r requirements.txt
streamlit run app.py
