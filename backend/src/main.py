import json
from scraper import create_text_and_images, create_dir, books, chosen_books, remaining_textbooks
from processor import get_useable_chunks, get_chunk_json
from database import pine, create_content_list, create_db, upsert_to_pinecone, ask_medllm
from langchain_openai.embeddings import OpenAIEmbeddings
from pinecone_text.sparse import BM25Encoder
from supabase import create_client, Client
import os
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)



""" 
    Used to Create the Directory for the textbooks' text files and the diagrams from the those respective text files. Only ran this code
    on the Chemistry textbook for testing purposes and MVP. 
"""
#create_dir()
#create_text_and_images(chosen_books)

"""
    Used these lines to create the JSON file needed for vector database and the metadata for passing it to the database itself.
"""
#chunks_to_feed = get_useable_chunks()
#chunks_in_json = get_chunk_json(chunks_to_feed)

"""with open("/Users/rino/MedLLM/MedLLM/data/processed/chunks_json.json", "r") as f:
    chunks_json = json.load(f)"""
#pine(chunks_json)
    

#Upserting    
"""
    Creates the list of all the content; Creates an embedder for the sparse embeddings and fits it to the context of the content list
"""
"""all_content_list = create_content_list(chunks_json=chunks_json)

bm25 = BM25Encoder()
if os.path.exists("/Users/rino/MedLLM/MedLLM/models/bm25-encoder.json"):
    bm25.load("/Users/rino/MedLLM/MedLLM/models/bm25-encoder.json")
bm25.fit(all_content_list)
bm25.dump("/Users/rino/MedLLM/MedLLM/models/bm25-encoder.json")

hybrid_index = create_db()"""
#upsert_to_pinecone(chunks_json=chunks_json, bm25=bm25, hybrid_index=hybrid_index)


#query = "What is Sublimation?"
#ask_medllm(query=query, bm25=bm25, hybrid_index=hybrid_index)

#Creating the text files for the other textbooks
#create_text_and_images(remaining_textbooks)



#MAIN LOOP FOR REST OF TEXTBOOKS
textbook_dir = "/Users/rino/MedLLM/MedLLM/data/processed/TEXTBOOKS"
completed_textbooks_dir = "/Users/rino/MedLLM/MedLLM/data/processed/COMPLETED_TEXTBOOKS"

"""for e in os.scandir(textbook_dir):
    with open(e.path, "r") as f:
        print(f"PROCESSING FOR: {Path(e.path).stem}")        
        textbook_name = Path(e.path).stem
        json_path = f"/Users/rino/MedLLM/MedLLM/data/processed/chunks_json_{textbook_name}.json"
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                chunks_json = json.load(f)
        else:
            chunks_to_feed = get_useable_chunks(e.path)
            chunks_json = get_chunk_json(chunks_to_feed, textbook_name)
            with open(f"/Users/rino/MedLLM/MedLLM/data/processed/chunks_json_{textbook_name}.json", "r") as f:
                chunks_json = json.load(f)
        all_content_list = create_content_list(chunks_json=chunks_json)

        bm25 = BM25Encoder()
        if os.path.exists(f"/Users/rino/MedLLM/MedLLM/models/bm25-{textbook_name}-encoder.json"):
            bm25.load(f"/Users/rino/MedLLM/MedLLM/models/bm25-{textbook_name}-encoder.json")
        bm25.fit(all_content_list)
        bm25.dump(f"/Users/rino/MedLLM/MedLLM/models/bm25-{textbook_name}-encoder.json")

        hybrid_index = create_db()
        upsert_to_pinecone(chunks_json=chunks_json, bm25=bm25, hybrid_index=hybrid_index, textbook_name=textbook_name)"""


"""total_content_list = []

for e in os.scandir("/Users/rino/MedLLM/MedLLM/backend/data/processed/json_chunks"):
    with open(e.path, "r") as f:
        data = json.load(f)
        current_content_list = create_content_list(data)
        total_content_list.extend(current_content_list)
        print(len(total_content_list))

global_bm25_encoder = BM25Encoder()
global_bm25_encoder.fit(total_content_list)
global_bm25_encoder.dump("/Users/rino/MedLLM/MedLLM/backend/data/models/global_bm25.json")"""


@app.get("/")
def root():
    return {"Hello": "World"}

@app.get("/medLLM_message")
def getMessage(query: str):
    hybrid_index = create_db()
    global_bm25_encoder = BM25Encoder()
    global_bm25_encoder.load("/Users/rino/MedLLM/MedLLM/backend/data/models/global_bm25.json")
    raw = ask_medllm(query, global_bm25_encoder, hybrid_index)

    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
        cleaned = cleaned.strip()
    
    cleaned = cleaned.replace("\\(", "\\\\(").replace("\\)", "\\\\)").replace("\\[", "\\\\[").replace("\\]", "\\\\]")

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("PARSE FAILED:", e)
        print("CLEANED WAS:", repr(cleaned))
        return {"topic": "", "answer": cleaned, "sources": []}
    return {  
        "topic": parsed["topic"],
        "answer": parsed["answer"],
        "sources": parsed["sources"]
    }

class MessagePayload(BaseModel):
    conversation_id: str | None = None
    title: str | None = None
    role: str
    content: str
    auth0_id: str


@app.post("/save_message")
def save_conversations(payload: MessagePayload):
    user = supabase.table("users").select("id").eq("auth0_id", payload.auth0_id).execute()
    if not user.data:
        new_user = supabase.table("users").insert({"auth0_id": payload.auth0_id}).execute()
        user_id = new_user.data[0]["id"]
    else:
        user_id = user.data[0]["id"]

    convo_id = payload.conversation_id
    if not convo_id:
        new_convo = supabase.table("conversations").insert({
            "user_id": user_id,
            "title": payload.title or "New conversation"
        }).execute()
        convo_id = new_convo.data[0]["id"]
    
    supabase.table("messages").insert({
        "conversation_id": convo_id,
        "role": payload.role,
        "content": payload.content,
    }).execute()

    return {"conversation_id": convo_id}

@app.get("/get_conversations")
def get_conversations(auth0_id: str):
    user = supabase.table("users").select("id").eq("auth0_id", auth0_id).execute()
    if not user.data:
        return {"conversations": []}
    user_id = user.data[0]["id"]
    convos = supabase.table("conversations").select("title", "id", "created_at").eq("user_id", user_id).order("created_at", desc=True).execute()
    return {"conversations": convos.data}

@app.get("/get_messages")
def get_messages(conversation_id: str):
    messages = supabase.table("messages").select("role", "content").eq("conversation_id", conversation_id).order("created_at").execute()
    return {"messages": messages.data}