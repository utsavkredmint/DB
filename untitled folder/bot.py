import google.generativeai as genai
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
import google.generativeai as genai
genai.configure(api_key=GOOGLE_API_KEY)

GOOGLE_API_KEY = os.getenv("AIzaSyDnktZ1KvYUuOVwh51JzroyPUGdbFMSZpw")

 # List available models with content generation support
 #for m in genai.list_models():
  #   if 'generateContent' in m.supported_generation_methods:
   #      print(m.name)

MODEL_CONFIG = {
   "temperature": 0.2,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
    }

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=MODEL_CONFIG,
    safety_settings=safety_settings
)

uri = "mongodb://kredmintsuper:super%40%23%241234kredmint@10.160.0.6:27017/user?authSource=admin"
client = MongoClient(uri)
db = client['user']  # Your target DB

def gemini_output(database, system_prompt, user_prompt):
    data_info = fetch_relevant_data(database, user_prompt)

    input_prompt = [
         system_prompt.strip(),
         f"\n[Raw data from DB]\n{data_info}",
         f"\n[User Question]\n{user_prompt.strip()}"
    ]

    response = model.generate_content(input_prompt)
    return response.text

def fetch_relevant_data(database, query):
    """
    Modify this with smart query logic (e.g., NLP → Mongo query).
    """

system_prompt = """
You are a database reasoning assistant. Given a user question,
first fetch relevant data from the MongoDB, then return a clean and helpful human-readable response
"""

user_prompt = "find the status of LNL-125 in loan collection "

output = gemini_output(db, system_prompt, user_prompt)

print(output)
