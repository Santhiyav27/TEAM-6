import os
import fitz  # PyMuPDF
import chromadb
import docx2txt
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from google.generativeai import GenerativeModel, configure
from fastapi.middleware.cors import CORSMiddleware

# === CONFIGURATION ===
os.environ["GOOGLE_API_KEY"] = "AIzaSyDCF4XPdZ7BCAE0PhXvG38b9G5H_0W8lB8"
configure(api_key=os.environ["GOOGLE_API_KEY"])

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
model = GenerativeModel("models/gemini-1.5-flash-latest")

chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="company_docs")

app = FastAPI()
chat_history = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: QueryRequest):
    user_q = request.question.strip().lower()

    if user_q in ["hi", "hello", "hey"]:
        return {"answer": "Hi! I am your assistant. How may I help you?"}

    query_vector = embedding_model.encode(user_q).tolist()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=3,
        include=["documents"]
    )

    docs = results["documents"][0]
    context = "\n\n".join(docs)
    prompt = f"""Answer the following question based on the company policy documents:\n
Question: {user_q}\n
Relevant Context:\n{context}\n
Answer:"""

    response = model.generate_content(prompt)
    answer = response.text.strip()
    chat_history.append((user_q, answer))

    return {"answer": answer}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename.lower()
    content = ""

    # === Extract content ===
    if filename.endswith(".pdf"):
        pdf = fitz.open(stream=await file.read(), filetype="pdf")
        for page in pdf:
            content += page.get_text()
    elif filename.endswith(".docx"):
        temp_path = f"temp_{filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        content = docx2txt.process(temp_path)
        os.remove(temp_path)
    else:
        return {"status": "error", "message": "Only PDF or DOCX files are allowed."}

    if not content.strip():
        return {"status": "error", "message": "No content extracted from file."}

    # === Check relevance to existing DB ===
    content_vector = embedding_model.encode(content).tolist()
    results = collection.query(
        query_embeddings=[content_vector],
        n_results=1,
        include=["distances"]
    )

    relevance_score = results['distances'][0][0]  # Lower means more similar
    threshold = 0.5  # Adjust based on accuracy needs

    if relevance_score < threshold:
        doc_id = f"doc-{filename}"
        collection.add(documents=[content], ids=[doc_id])
        return {"status": "success", "message": "This document is relevant to the company and has been added."}
    else:
        return {"status": "rejected", "message": "This document is not relevant to the company and was not added."}
