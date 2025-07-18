# ingest.py

from docx import Document
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
import os

# === Read Word Documents ===
def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

# === Split into Chunks ===
def split_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    return splitter.split_text(text)

# === Embedding Model ===
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_texts(texts):
    return embedding_model.encode(texts, convert_to_tensor=False)

# === ChromaDB client ===
chroma_client = chromadb.PersistentClient(path="chroma_store")

# === Store Embeddings in ChromaDB ===
def store_embeddings(collection_name, text_chunks, embeddings):
    collection = chroma_client.get_or_create_collection(collection_name)

    # Clear existing documents
    existing_ids = collection.get()['ids']
    if existing_ids:
        collection.delete(ids=existing_ids)
        print(f"🧹 Cleared {len(existing_ids)} documents in '{collection_name}'.")

    for i, (text, vector) in enumerate(zip(text_chunks, embeddings)):
        collection.add(
            documents=[text],
            embeddings=[vector.tolist()],
            ids=[f"{collection_name}_doc_{i}"]
        )
    print(f"✅ Stored {len(text_chunks)} embeddings in '{collection_name}'.")

# === Process Documents from Folder ===
def process_documents(folder_path, collection_name):
    all_chunks = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".docx"):
            full_path = os.path.join(folder_path, filename)
            print(f"📄 Processing: {filename}")
            content = read_docx(full_path)
            chunks = split_text(content)
            all_chunks.extend(chunks)

    if all_chunks:
        embeddings = embed_texts(all_chunks)
        store_embeddings(collection_name, all_chunks, embeddings)
    else:
        print(f"⚠ No valid documents found in '{folder_path}'.")

# === MAIN ===
if __name__ == "__main__":
    process_documents("Policies/org_docs", "allowed_docs")
    process_documents("Policies/restricted_docs", "restricted_docs")
