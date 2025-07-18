import os
import fitz  # PyMuPDF
import docx2txt
import chromadb
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from google.generativeai import GenerativeModel, configure
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sklearn.metrics.pairwise import cosine_similarity

# === API Key Setup ===
os.environ["GOOGLE_API_KEY"] = "AIzaSyAQeX-6290bk8OmA27CfScTpq9HQKZZhQY"
configure(api_key=os.environ["GOOGLE_API_KEY"])

# === App Initialization ===
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Models ===
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
gemini = GenerativeModel("models/gemini-1.5-flash-latest")

# === ChromaDB ===
chroma_client = chromadb.PersistentClient(path="chroma_store")
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

ORG_DOCS_DIR = r"Policies/org_docs"
RESTRICTED_DOCS_DIR = r"Policies/restricted_docs"

def load_text_from_folder(folder):
    content = ""
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if file.endswith(".pdf"):
            pdf = fitz.open(path)
            for page in pdf:
                content += page.get_text()
        elif file.endswith(".docx"):
            content += docx2txt.process(path)
    return content

# === Setup ChromaDB for Organizational Docs ===
allowed_collection = chroma_client.get_or_create_collection("allowed_docs")
restricted_collection = chroma_client.get_or_create_collection("restricted_docs")

def embed_collection_if_empty(collection, content, prefix):
    chunks = splitter.split_text(content)
    if len(collection.get()["ids"]) == 0:
        for i, chunk in enumerate(chunks):
            emb = embedding_model.encode(chunk).tolist()
            collection.add(documents=[chunk], embeddings=[emb], ids=[f"{prefix}_{i}"])

embed_collection_if_empty(allowed_collection, load_text_from_folder(ORG_DOCS_DIR), "allowed")
embed_collection_if_empty(restricted_collection, load_text_from_folder(RESTRICTED_DOCS_DIR), "restricted")

# === In-memory user sessions ===
user_sessions = {}

# === Data Models ===
class QueryRequest(BaseModel):
    session_id: str
    question: str

@app.post("/upload")
async def upload_user_doc(file: UploadFile = File(...)):
    filename = file.filename.lower()
    content = ""

    # === File Reading ===
    try:
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
            raise HTTPException(status_code=400, detail="Only PDF or DOCX files are supported.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {e}")

    if not content.strip():
        raise HTTPException(status_code=400, detail="Document is empty or unreadable.")

    user_emb = embedding_model.encode(content).reshape(1, -1)

    # === Check Restricted ===
    r = restricted_collection.query(query_embeddings=user_emb.tolist(), n_results=1)
    r_sim = cosine_similarity(user_emb, embedding_model.encode(r["documents"][0][0]).reshape(1, -1))[0][0] if r["documents"] else 0

    if r_sim > 0.6:
        session_id = str(uuid.uuid4())
        user_sessions[session_id] = {"content": content, "type": "restricted"}
        return {"session_id": session_id, "message": "⚠️ Restricted document uploaded."}

    # === Check Allowed ===
    a = allowed_collection.query(query_embeddings=user_emb.tolist(), n_results=1)
    a_sim = cosine_similarity(user_emb, embedding_model.encode(a["documents"][0][0]).reshape(1, -1))[0][0] if a["documents"] else 0

    if a_sim > 0.6:
        session_id = str(uuid.uuid4())
        user_sessions[session_id] = {"content": content, "type": "allowed"}
        return {"session_id": session_id, "message": "✅ Organizational document uploaded."}

    return {"message": "🚫 Not an official document."}


@app.post("/ask")
async def ask_from_documents(request: QueryRequest):
    session_id = request.session_id
    question = request.question.strip()

    user_emb = embedding_model.encode(question).reshape(1, -1)

    if question.lower() in ["hi", "hello", "hey"]:
        return {"answer": "Hi! I am your AI assistant. How can I help you today?"}

    # === Session-based answering ===
    context, source = "", ""
    if session_id in user_sessions:
        doc_data = user_sessions[session_id]
        doc_emb = embedding_model.encode(doc_data["content"]).reshape(1, -1)
        sim = cosine_similarity(user_emb, doc_emb)[0][0]
        if sim > 0.6:
            context = doc_data["content"]
            source = doc_data["type"]
        else:
            collection = restricted_collection if doc_data["type"] == "restricted" else allowed_collection
            results = collection.query(query_embeddings=user_emb.tolist(), n_results=3)
            context = "\n\n".join(results["documents"][0]) if results["documents"] else ""
            source = doc_data["type"]
    else:
        # No session: fallback
        r = restricted_collection.query(query_embeddings=user_emb.tolist(), n_results=1)
        if r["documents"]:
            r_score = cosine_similarity(user_emb, embedding_model.encode(r["documents"][0][0]).reshape(1, -1))[0][0]
            if r_score > 0.6:
                return {"answer": "⛔ Access to restricted content denied."}
        a = allowed_collection.query(query_embeddings=user_emb.tolist(), n_results=3)
        context = "\n\n".join(a["documents"][0]) if a["documents"] else ""
        source = "allowed"

    if not context:
        return {"answer": f"No relevant info found in {source} documents."}

    # === Gemini Prompt ===
    prompt = f"""You are a helpful assistant answering questions strictly from the '{source}' document content below. 

Document Content:
\"\"\"{context[:2000]}\"\"\"

Question:
{question}

Answer:"""

    try:
        response = gemini.generate_content(prompt)
        return {"answer": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini Error: {e}")
