import json
from src.scraper import create_text_and_images, create_dir, books, chosen_books
from src.processor import get_useable_chunks, get_chunk_json
from src.database import pine, create_content_list, create_db, upsert_to_pinecone
from langchain_openai.embeddings import OpenAIEmbeddings
from pinecone_text.sparse import BM25Encoder
import os


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

with open("/Users/rino/MedLLM/MedLLM/data/processed/chunks_json.json", "r") as f:
    chunks_json = json.load(f)
#pine(chunks_json)
    
all_content_list = create_content_list(chunks_json=chunks_json)

bm25 = BM25Encoder()
if os.path.exists("/Users/rino/MedLLM/MedLLM/models/bm25-encoder.json"):
    bm25.load("/Users/rino/MedLLM/MedLLM/models/bm25-encoder.json")
bm25.fit(all_content_list)
bm25.dump("/Users/rino/MedLLM/MedLLM/models/bm25-encoder.json")

hybrid_index = create_db()
upsert_to_pinecone(chunks_json=chunks_json, bm25=bm25, hybrid_index=hybrid_index)