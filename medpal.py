# medpal.py

import weaviate
from weaviate import Client
from weaviate.auth import AuthApiKey
from langchain_community.vectorstores import Weaviate as WeaviateVectorStore
# from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_community.embeddings import SentenceTransformerEmbeddings
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import requests
import os 
from pathlib import Path
import torch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WEAVIATE_URL="https://fepgdf97stgeefrfi9qnvg.c0.us-east1.gcp.weaviate.cloud"
WEAVIATE_API_KEY= "DPxBIZLN2cXBXkayuLo4uUhwMIc2qjtv84rR"

def connect_weaviate():
    weaviate_url = WEAVIATE_URL
    weaviate_api_key = WEAVIATE_API_KEY
    
    # try:
    #     auth_config = weaviate.AuthApiKey(api_key=weaviate_api_key)
    #     client = weaviate.Client(
    #         url=weaviate_url,
    #         auth_client_secret=auth_config
    #     )
    #     if client.is_ready():
    #         print("Connection successful")
    #     else:
    #         print("Weaviate server not ready")
    #         client = None
    # except Exception as e:
    #     print(f"Connection failed: {e}")
    #     client = None
    # return client

    try:
        auth_config = AuthApiKey(api_key=weaviate_api_key)
        client = Client(
            url=weaviate_url,
            auth_client_secret=auth_config
        )
        if client.is_ready():
            print("✅ Connection successful")
        else:
            print("❌ Weaviate server not ready")
            client = None
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        client = None

    return client


def fetch_nearby_clinics(zip_code):
    url = f"https://npiregistry.cms.hhs.gov/api/?version=2.1&postal_code={zip_code}&limit=5"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        clinics_info = []
        for res in data.get("results", []):
            basic = res.get("basic", {})
            address = res.get("addresses", [{}])[0]
            
            # Get name (organization or individual)
            name = basic.get("organization_name") or f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip()
            
            # Get address details
            street = address.get("address_1", "")
            city = address.get("city", "")
            state = address.get("state", "")
            postal = address.get("postal_code", "")
            full_address = f"{street}, {city}, {state} {postal}"
            
            # Get phone
            phone = address.get("telephone_number", "N/A")
            
            # Format clinic information with emojis for better presentation
            clinic_info = f"🏥 {name}\n📍 {full_address}\n📞 {phone}\n"
            clinics_info.append(clinic_info)
        
        return "\n".join(clinics_info) if clinics_info else "No clinics found."
    return "Error fetching clinics."
 
# def load_finetuned_model():
#     model_path = "./models/flan-t5-healthcare-finetuned"  # relative path
#     tokenizer = AutoTokenizer.from_pretrained(model_path)
#     model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
#     return tokenizer, model
from pathlib import Path

# def load_finetuned_model():
#     # Get the absolute path of the current script
#     current_file = Path(__file__).resolve()
    
#     # Get the parent directory of the current script (your project root)
#     project_dir = current_file.parent
    
#     # Build the path to your models directory
#     model_path = project_dir / "models" / "flan-t5-healthcare-finetuned"
    
#     print(f"Looking for model at: {model_path}")
    
#     # Check if the path exists
#     if model_path.exists():
#         try:
#             print(f"Loading model from: {model_path}")
#             tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
#             model = AutoModelForSeq2SeqLM.from_pretrained(str(model_path), local_files_only=True)
#             return tokenizer, model
#         except Exception as e:
#             print(f"Error loading custom model: {e}")
#             print("Falling back to default model")
#             tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
#             model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
#             return tokenizer, model
#     else:
#         print(f"Model directory not found at {model_path}")
#         print("Using default model instead")
#         tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
#         model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
#         return tokenizer, model
def load_finetuned_model():
    # Get the absolute path of the current script
    current_file = Path(__file__).resolve()
    project_dir = current_file.parent

    model_path = project_dir  # model files are directly in project root

    print(f"Looking for model at: {model_path}")

    if model_path.exists():
        try:
            print(f"Loading model from: {model_path}")
            tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
            model = AutoModelForSeq2SeqLM.from_pretrained(str(model_path), local_files_only=True)
            return tokenizer, model
        except Exception as e:
            print(f"Error loading custom model: {e}")
            print("Falling back to default model")
            tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
            model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
            return tokenizer, model
    else:
        print(f"Model directory not found at {model_path}")
        print("Using default model instead")
        tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
        model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
        return tokenizer, model

    
def upgrade_prompt(context, user_question):
    emergency_keywords = ["chest pain", "shortness of breath", "stroke", "heart attack"]
    is_emergency = any(word in user_question.lower() for word in emergency_keywords)

    if is_emergency:
        additional_instruction = "⚠️ Emergency detected! Suggest nearby clinics if symptoms persist."
    else:
        additional_instruction = "✅ Provide helpful advice and simple home remedies if safe."

    prompt = f"""
You are a highly knowledgeable healthcare assistant.

{additional_instruction}

Based on the following context, answer the user's question briefly and clearly.
Suggest medicine, treatment, or home remedy (upaay) if appropriate.

Context:
{context}

Question: {user_question}
Answer:
"""
    return prompt

def generate_synthetic_questions(user_question):
    templates = [
        "What could be the possible causes of {symptom}?",
        "When should I see a doctor for {symptom}?",
        "What home remedies can I try for {symptom}?",
        "Are there any medications available for {symptom}?"
    ]
    symptom = user_question.lower().strip("?.")

    synthetic_questions = [t.format(symptom=symptom) for t in templates[:2]]  # Pick top 2
    return synthetic_questions


def medpal(user_question):
    # Connect Weaviate (each time user asks)
    client = connect_weaviate()
    if client is None:
        print("Client connection failed")
        return "Error connecting to medical database. Please try again later.", 0, []

    # Load embeddings and vectorstore
    embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = WeaviateVectorStore(
        client=client,
        index_name="MedicalDoc",
        embedding=embedding_model,
        text_key="text",
    )
    # Load fine-tuned model
    # tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
    # model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
    tokenizer, model = load_finetuned_model()

    # Step 1: Embed and retrieve documents
    query_vector = embedding_model.embed_query(user_question)
    docs = vectorstore.similarity_search_by_vector(query_vector, k=3)
    context = "\n\n".join([doc.page_content for doc in docs if doc.page_content.lower() != "none"])

    # Step 2: Generate answer
#     prompt = f"""
# You are a highly knowledgeable healthcare assistant.

# Based on the following context, answer the user's question briefly and clearly.
# Suggest medicine, treatment, or home remedy (upaay) if possible.

# Context:
# {context}

# Question: {user_question}
# Answer:
# """
# NEW
    prompt = upgrade_prompt(context, user_question)

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    outputs = model.generate(**inputs, max_length=256)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Step 3: Estimate severity
    # critical_terms = ['chest pain', 'shortness of breath', 'unconscious', 'severe bleeding', 'stroke', 'heart attack', 'seizure']
    # severity_score = sum(1 for term in critical_terms if term in user_question.lower())
    # severity_score = min(severity_score, 5)
    # Step 3: Estimate severity
    critical_terms = {
    'chest pain': 4,  # Increase severity for chest pain
    'shortness of breath': 3,
    'unconscious': 5,
    'severe bleeding': 5,
    'stroke': 5,
    'heart attack': 5,
    'seizure': 5,
    'fever': 2,  # Moderate severity for fever
    'headache': 1, 
    'cough': 1
}

    severity_score = 0
    for term, score in critical_terms.items():
     if term in user_question.lower():
        severity_score = max(severity_score, score)  # Take highest severity match


    synthetic_questions = generate_synthetic_questions(user_question)
    return answer, severity_score, synthetic_questions
