import json
from src.scraper import create_text_and_images, create_dir, books, chosen_books, remaining_textbooks
from src.processor import get_useable_chunks, get_chunk_json
from src.database import pine, create_content_list, create_db, upsert_to_pinecone, ask_medllm
from langchain_openai.embeddings import OpenAIEmbeddings
from pinecone_text.sparse import BM25Encoder
import os
from pathlib import Path


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

create_text_and_images(remaining_textbooks)