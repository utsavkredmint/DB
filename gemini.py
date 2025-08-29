import os
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import numpy as np
from numpy.linalg import norm

# === Load environment variables ===
load_dotenv()

MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEYS")

# === Load embedding model and Gemini model ===
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-pro", google_api_key=GEMINI_API_KEY)

# === Cosine similarity ===
def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

# === Get MongoDB collection ===
def get_collection():
    client = MongoClient(MONGO_URI)
    return client["rag_db"]["kredbot_reports"]  # Make sure name is correct here

# === Embed user query ===
def embed_query(query):
    return model.encode(query).tolist()

def get_relevant_docs(collection, query, top_k=3):
    query_embedding = embed_query(query)
    results = []

    for doc in collection.find():
        if "embedding" not in doc:
            continue
        sim = cosine_similarity(query_embedding, doc["embedding"])
        results.append((sim, doc["text"]))

    results.sort(key=lambda x: x[0], reverse=True)
    top_results = results[:top_k]

    return " ".join([text for _, text in top_results])

# === Generate response from Gemini ===
def generate_response(query, context):
    prompt_template = PromptTemplate(
        input_variables=["prompt", "context"],
        template="""
Use the following pieces of context to answer the user's question.

Context:
{context}

User's Question:
{prompt}
"""
    )
    chain = prompt_template | llm
    return chain.invoke({"prompt": query, "context": context}).content

# === Main driver ===
if __name__ == "__main__":
    collection = get_collection()

    # Accept input
    user_query = input("Enter your question: ").strip()

    # Get relevant context from local MongoDB
    context = get_relevant_docs(collection, user_query)

    # Ask Gemini to answer
    response = generate_response(user_query, context)

    print("\n=== Final Response ===\n")
    print(response)
