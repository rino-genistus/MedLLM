import os
from pinecone import ServerlessSpec, Pinecone
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=api_key)