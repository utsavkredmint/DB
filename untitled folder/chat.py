import pymongo
import google.generativeai as genai
import os

def get_relevant_database_and_collection(user_question):
    
    question_lower = user_question.lower()
    if "account" in question_lower and ("loan" in question_lower or "anchor_sub_collection" in question_lower):
        return "account", "loan" if "loan" in question_lower else "anchor_sub_collection"
    elif "activity" in question_lower:
        return "activity", None  # You would need to create prompts for collections in "activity"
    elif "lead" in question_lower:
        return "lead", None
    else:
        return None, None


def generate_gemini_prompt_anchor_sub_collection(question, data):
    prompt = f"""
    You are an expert data analyst that answers user questions based on data from a MongoDB database.

    The database is named 'account'.

    The relevant collection is named 'anchor_sub_collection'.

    Here is the information about fields in 'anchor_sub_collection' collection.

    - `_id`: (String) Unique identifier for the record (e.g., "ASC-525")
    - `userId`: (String) User ID associated with the record (e.g., "YHoT2VRW9HRnC4JgkV8lQOvmak")
    - `name`: (String) Name associated with the record (e.g., "KREDMINT TECHNOLOGIES PRIVATE LIMITED")
    - `invoiceId`: (String) Invoice ID (e.g., "IN-10659")
    - `principalAmount`: (Number) Original loan amount (e.g., 10000.0)
    - `paidPrincipalAmount`: (Number) Amount of principal that has been paid (e.g., 0.0)
    - `pendingPrincipalAmount`: (Number) Amount of principal that is still owed (e.g., 10000.0)
    - `interestRate`: (Number) The interest rate of the loan (e.g., 18.0)
    - `interestAmount`: (Number) Total interest to be paid (e.g., 74.0)
    - `paidInterestAmount`: (Number) Amount of interest that has been paid (e.g., 74.0)
    - `status`: (String) Status of the record (e.g., "COMPLETED")
    - `date`: (Date) A date associated with the record.

    The user's question is: {question}

    Here is the data extracted from the database (if available). If there is no data, ignore this section.
    {data}

    Using the available data and your understanding of the 'anchor_sub_collection' collection, provide a clear and concise answer to the user's question.
    If you cannot answer the question based on the available data, respond with: "I cannot answer the question based on the available data from anchor_sub_collection.".
    """
    return prompt

def generate_gemini_prompt_loan(question, data):
    prompt = f"""
    You are an expert data analyst that answers user questions based on data from a MongoDB database.

    The database is named 'account'.

    The relevant collection is named 'loan'.

    Here is the information about fields in 'loan' collection.
    *   `_id`: (String) Unique identifier for the record (e.g., "LNL-125")
    *   `userId` (String): user id of the record
    *   `amount` (Number): total amount
    *   `paidAmount` (Number): amount paid
    *   `invoiceId` (String): Invoice id for a payment
    *   `status` (String): status of the payment
    *   `interestRate` (Number): interest rate

    The user's question is: {question}

    Here is the data extracted from the database (if available). If there is no data, ignore this section.
    {data}

    Using the available data and your understanding of the 'loan' collection, provide a clear and concise answer to the user's question.
    If you cannot answer the question based on the available data, respond with: "I cannot answer the question based on the available data from the loan collection.".
    """
    return prompt

#Generic prompt

def generate_gemini_prompt_generic(question, database_name):
    prompt = f"""
    You are an expert data analyst that answers user questions based on data from a MongoDB database.

    The database is named '{database_name}'.
    You do not have information on what is in this database.

    The user's question is: {question}

    Without data, respond that you cannot answer the question.
    If you cannot answer the question based on the available data, respond with: "I cannot answer the question, since the database information is not available.".
    """
    return prompt


def extract_data_from_mongodb(database_name, collection_name, query):
    MONGO_URI = os.environ.get("MONGO_URI")
    if not MONGO_URI:
        return "Error: MONGO_URI not set."
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[database_name]
        collection = db[collection_name]
        results = list(collection.find(query))  # Convert cursor to a list
        client.close()
        return results
    except Exception as e:
        return f"Database error: {e}"

def generate_gemini_prompt(database_name, collection_name, question, data):
    # Select the correct prompt based on database and collection
    if database_name == "account":
        if collection_name == "anchor_sub_collection":
            return generate_gemini_prompt_anchor_sub_collection(question, data)
        elif collection_name == "loan":
            return generate_gemini_prompt_loan(question, data)
        else:
            # Handle other collections under 'account' if needed
            return generate_gemini_prompt_generic(question, database_name) # Generic prompt
    elif database_name in ["activity", "admin", "admin-tool", "auth", "card", "client", "clientIntegration", "config", "coupon", "event", "lead", "local", "master", "masteriq", "new_auth", "oms", "paras", "scheduler", "underwriting", "user", "vendor"]:
         return generate_gemini_prompt_generic(question, database_name) # Generic prompt
    else:
        return "I'm sorry, I don't have information about that."


def process_user_question(user_question):
   
    # 1. Get database and collection.
    database_name, collection_name = get_relevant_database_and_collection(user_question)

    if not database_name:
        return "I'm sorry, I cannot understand the collection and database you mentioned. Please provide it again."

    # 2. Data extraction (if applicable)
    query = {}  #  Modify this depending on intent
    data = []
    if collection_name: #If specific collection.
        data = extract_data_from_mongodb(database_name, collection_name, query) #Get all data.

    # 3. Generate the Prompt
    prompt = generate_gemini_prompt(database_name, collection_name, user_question, data)

    # 4. Call Gemini
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text

# Example Usage
user_question = "Tell me about anchor sub collection status" #Generic use case without the exact database and collection.
user_question_2 = "What is the amount paid for user with id USR-306 in the loan collection?"
user_question_3 = "what is the status about this '_id' : 'BYR-27' in account (buyer) "

response = process_user_question(user_question_2)
print(response)