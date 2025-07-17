import os
import chromadb
from sentence_transformers import SentenceTransformer
from google.generativeai import GenerativeModel, configure

# Configure API
os.environ["GOOGLE_API_KEY"] = "AIzaSyDCF4XPdZ7BCAE0PhXvG38b9G5H_0W8lB8"
configure(api_key=os.environ["GOOGLE_API_KEY"])

# Initialize ChromaDB and embedding model
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_collection(name="company_docs")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Chat history (optional)
chat_history = []

def ask_question(query):
    query_vector = embedding_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=3,
        include=['documents']
    )

    docs = results['documents'][0]
    context = "\n\n".join(docs)
    prompt = f"""Answer the following question based on the company policy documents:\n
Question: {query}\n
Relevant Context:\n{context}\n
Answer:"""

    model = GenerativeModel("models/gemini-1.5-flash-latest")
    response = model.generate_content(prompt)
    answer = response.text.strip()
    chat_history.append((query, answer))
    return answer

if __name__ == "__main__":
    while True:
        user_q = input("\nAsk a question (or type 'exit'): ")
        if user_q.lower() == "exit":
            break
        elif user_q.lower() in ["hi", "hello", "hey"]:
            print("\n🧠 Assistant:\nHi! I am your assistant. How may I help you?")
        else:
            answer = ask_question(user_q)
            print("\n🧠 Gemini Answer:\n", answer)
