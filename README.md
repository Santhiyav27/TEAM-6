# 🤖 AI-Powered Chatbot for HR, IT & Policy Queries (with Restricted Document Access) 

## 📌 Project Overview

This is an **AI-powered intelligent chatbot system** designed for **public sector organizations**, enabling employees to get **instant answers** to HR, IT, and policy-related queries. What makes this chatbot unique is its **document-aware access control**—users must upload the correct document to access sensitive content.

The system leverages **Google Gemini AI** and **ChromaDB** for intelligent question answering based on context from either **public** or **restricted** documents. It's a secure, scalable, and accurate solution aimed at improving organizational productivity and reducing repetitive queries.

## 🔧 Problem Statement

### ❗ Existing Issues Faced by Organizations:
- Employees wait long to get answers from HR or IT departments.
- Teams are burdened by answering the same repetitive questions.
- Company documents are often buried or hard to search.
- Sensitive policies lack proper access control.

### ❌ Current Solutions Are Inefficient:
- Old HR portals are outdated and non-intuitive.
- Generic chatbots fail to understand company-specific policies.
- Email-based support is slow and not scalable.

## ✅ Our Solution

We’ve built a **context-aware AI chatbot** that:
- Uses **Google Gemini AI** to answer user questions accurately.
- Differentiates between **public** and **restricted** documents.
- Allows access to sensitive content **only when the correct file is uploaded**.
- Delivers responses **within seconds**.
- Can scale to **multiple users** without performance drops.

## 🧠 Core Features

- ⚡ **Fast Response Time** – Under 5 seconds per query.
- 🧩 **Smart AI** – Powered by Google Gemini for natural conversation.
- 🔐 **Access Control** – Sensitive content shown only after document verification.
- 🔍 **Context-Aware Search** – Uses semantic matching, not just filenames.
- 👥 **Concurrent Users** – Supports 5+ users seamlessly.
- 🧬 **Extendable** – Can integrate login, memory, analytics, and more.
- 🌐 **Integration Ready** – Easy to connect with websites and apps.

## 🔄 Workflow Diagram

User Opens Chatbot → User Asks Question → Check if restricted → If Yes: Check uploaded doc → If matched → Search restricted DB → Gemini → Response. If No → Search public DB → Gemini → Response.

## 🛠️ Tech Stack

| Tool/Technology | Purpose |
|-----------------|---------|
| **Google Gemini AI** | Generative AI to answer user queries |
| **ChromaDB**     | Vector database to store document embeddings |
| **FastAPI**      | Python backend for handling chatbot requests |
| **React (optional)** | Frontend chatbot interface |
| **LangChain / Embedding Tools** | For converting docs to vector format |
| **Python**       | Programming logic & orchestration |

## ⚙️ Installation Guide

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Santhiyav27/TEAM-6.git
cd TEAM-6
```

### 2️⃣ Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scriptsctivate
```

### 3️⃣ Install Required Packages

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Google Gemini API Key

Dont forget to replace the api key in main.py:


export GOOGLE_API_KEY="your_google_gemini_api_key_h



### 5️⃣ Ingest Your Documents

Python Ingest_docs.py to run and create chroma db...if you change the files in policies document..you need to re-run the ingest_docs.py

Put docs in `org_docs/` and `restricted_docs/`. Then run:

```bash
python ingest_docs.py
```



### 6️⃣ Start Backend Server

```bash
uvicorn main:app --reload
```

To run in Localhost(connect multiple device over same network)
```bash
Python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Change the the ip address to your ip address in the app.js so that I will be hosted in your laptop then nearby system connected in the same wifi can also load the page bye pasting the url (given after running app.js )in the browser.


### 7️⃣ start frontend server :

# In another terminal
```bash
cd frontend/frontend
npm install
npm start
```


Visit: `http://127.0.0.1:8000`

incase of any issue in running the file contact : 

## 💬 How to Use

1. Open chatbot UI.
2. Upload a document (PDF or DOCX).
3. Ask questions in natural language.
4. If valid restricted doc is uploaded → get restricted info.
5. Otherwise → get public answers.

## 🎯 Target Users

- 🏛 Government Departments
- 🏥 Hospitals & Clinics
- 🏦 Banks & Financial Institutions
- 🎓 Universities & Colleges

## 👨‍💻 Team Members

| Name               | Reg. No.     |
|--------------------|--------------|
| Nidhiksha M K      | 23BAD077     |
| Poojith M          | 23BAD083     |
| Praksraj C         | 23BAD085     |
| Santhiya Varma S M | 23BAD103     |
| Saravanan K        | 23BAD106     |
| Navinraj S     | 23BAD306     |
| Risha Venkatesh    | 23BMC043     |

## 📁 Project Structure

TEAM-6-main/
├── backend/                # FastAPI server
├── frontend/               # (Optional) React interface
├── org_docs/               # Public documents
├── restricted_docs/        # Confidential documents
├── ingest_docs.py          # Preprocessing script
├── main.py                 # App logic
├── requirements.txt        # Dependencies
└── README.md

## 📜 License

MIT License – Open for educational and research use.
Raise an issue on GitHub or contact any team member.

> Built with ❤️ by Team 6 @ Kumaraguru College of Technology
