import os
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

load_dotenv()

MONGO_URI = os.getenv("MONGODB_CONNECTION_STRING")
SOURCE_COLLECTION = "raw_data"         # your existing collection
VECTOR_COLLECTION = "kredbot_reports"     # collection for embeddings

# Load embedding model
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)

# Connect to MongoDB
client = MongoClient(MONGO_URI)
source_col = client["rag_db"][SOURCE_COLLECTION]
vector_col = client["rag_db"][VECTOR_COLLECTION]

# Clear old vector data (optional)
vector_col.delete_many({})

# Process and embed each doc
for doc in source_col.find():
    # Build plain text from your fields (customize this!)
    text = f"{doc.get('title', '')}\n{doc.get('description', '')}\n{doc.get('content', '')}"

    embedding = model.encode(text).tolist()

    vector_doc = {
        "source_id": str(doc["_id"]),
        "text": text,
        "embedding": embedding
    }

    vector_col.insert_one(vector_doc)

print(" Embedding pipeline completed.")
