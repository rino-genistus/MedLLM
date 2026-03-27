import os
from pinecone import Pinecone
from pinecone import ServerlessSpec
from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings

load_dotenv()
api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=api_key)

embedding = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=1024)

def create_content_list(chunks_json):
    all_content_list = [json_obect['content'] for json_obect in chunks_json]
    return all_content_list

def create_db():
    index_name = "hybrid-index"
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            vector_type="dense",
            dimension=1024,
            metric="dotproduct",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1",
            )
        )
    return pc.Index(index_name)

def upsert_to_pinecone(chunks_json, bm25, hybrid_index):
    vectors_list = []
    for idx, json_object in enumerate(chunks_json):
        dense_vector_embedding = embedding.embed_query(json_object['content'])
        sparse_vector_embedding = bm25.encode_documents(json_object['content'])
        clean_json_object={
            "header":str(json_object.get('header', 'Unknown Section')),
            "content":str(json_object.get('content', '')),
            "description":str(json_object.get('description', '')),
            "requires_previous_context":str(json_object.get('requires_previous_content', '')).lower() == 'true',
            "summary":str(json_object.get('summary', '')),
        }

        raw_keywords = json_object.get('keywords', [])
        if isinstance(raw_keywords, list):
            clean_json_object['keywords'] = [str(k) for k in raw_keywords if k]
        else:
            clean_json_object['keywords'] = [str(raw_keywords)]

        vectors_list.append({
            "id":f"chunk-{idx}",
            "values":dense_vector_embedding,
            "sparse_values":sparse_vector_embedding,
            "metadata":clean_json_object,
        })

        if len(vectors_list) == 100:
            hybrid_index.upsert(vectors=vectors_list, namespace="Chemistry2e")
            vectors_list=[]
    if len(vectors_list)>0:
        hybrid_index.upsert(vectors=vectors_list, namespace="Chemistry2e")


def pine(chunks_json):
    for idx, json_object in enumerate(chunks_json):
        vector_embedding = embedding.embed_query(json_object['content'])
        print(f"JSON OBJECT INDEX: {idx}\n")
        print(f"VECTOR EMBEDDING: {str(vector_embedding)[:50]}")